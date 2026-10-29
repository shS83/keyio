import codecs
import os
import select
import sys
import termios
import tty
from collections import deque

from .keys import Key


ESCAPE_SEQUENCES = {
    b"\x1b[A": Key.UP,
    b"\x1b[B": Key.DOWN,
    b"\x1b[C": Key.RIGHT,
    b"\x1b[D": Key.LEFT,

    b"\x1b[H": Key.HOME,
    b"\x1b[F": Key.END,

    b"\x1b[2~": Key.INSERT,
    b"\x1b[3~": Key.DELETE,

    b"\x1b[5~": Key.PAGE_UP,
    b"\x1b[6~": Key.PAGE_DOWN,
}


class PosixKeyboard:

    def __init__(self):
        self.fd = None
        self.old_settings = None
        self.owns_fd = False
        # Keep unfinished UTF-8 sequences between non-blocking read() calls.
        self._decoder = codecs.getincrementaldecoder("utf-8")("replace")
        self._pending_keys = deque()

    def setup(self):
        self._decoder.reset()
        self._pending_keys.clear()

        if sys.stdin.isatty():
            self.fd = sys.stdin.fileno()

        else:
            self.fd = os.open("/dev/tty", os.O_RDONLY)
            self.owns_fd = True

        self.old_settings = termios.tcgetattr(self.fd)

        tty.setcbreak(self.fd)

    def restore(self):
        if self.old_settings is not None:
            termios.tcsetattr(
                self.fd,
                termios.TCSADRAIN,
                self.old_settings,
            )
        if self.owns_fd and self.fd is not None:
            os.close(self.fd)

        self.fd = None
        self.old_settings = None
        self.owns_fd = False
        self._decoder.reset()
        self._pending_keys.clear()

    def _emit_control(self, key):
        # A control key interrupts an unfinished UTF-8 sequence. Keep the
        # replacement character (if any) and the control event in order.
        self._pending_keys.extend(self._decoder.decode(b"", final=True))
        self._decoder.reset()
        if key is not None:
            self._pending_keys.append(key)
        return self._pending_keys.popleft() if self._pending_keys else None

    def read(self):
        if self._pending_keys:
            return self._pending_keys.popleft()

        ready, _, _ = select.select(
            [self.fd],
            [],
            [],
            0,
        )

        if not ready:
            return None

        key = os.read(self.fd, 1)
        if not key:
            return None

        if key == b"\x1b":
            return self._emit_control(self._read_escape_sequence())
        if key in (b"\r", b"\n"):
            return self._emit_control(Key.ENTER)

        if key == b"\t":
            return self._emit_control(Key.TAB)

        if key in (b"\x7f", b"\x08"):
            return self._emit_control(Key.BACKSPACE)

        if key == b" ":
            return self._emit_control(Key.SPACE)

        # One os.read() byte is not necessarily one Unicode character.
        # decode() returns an empty string until the character is complete.
        # A malformed sequence can emit multiple characters, so queue them.
        self._pending_keys.extend(self._decoder.decode(key, final=False))
        return self._pending_keys.popleft() if self._pending_keys else None

    def _read_escape_sequence(self):
        sequence = b"\x1b"
        while select.select(
            [self.fd],
            [],
            [],
            0.01,
        )[0]:
            sequence += os.read(self.fd, 1)
            # Stop once a recognized key is complete; do not swallow the
            # following event when multiple keys arrive in the same batch.
            if sequence in ESCAPE_SEQUENCES:
                return ESCAPE_SEQUENCES[sequence]

        if sequence == b"\x1b":
            return Key.ESCAPE

        return ESCAPE_SEQUENCES.get(sequence)
