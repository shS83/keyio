import os
import select
import sys
import termios
import tty

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

    def setup(self):
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

    def read(self):
        ready, _, _ = select.select(
            [self.fd],
            [],
            [],
            0,
        )

        if not ready:
            return None

        key = os.read(self.fd, 1)

        if key == b"\x1b":
            return self._read_escape_sequence()

        if key in (b"\r", b"\n"):
            return Key.ENTER

        if key == b"\t":
            return Key.TAB

        if key in (b"\x7f", b"\x08"):
            return Key.BACKSPACE

        if key == b" ":
            return Key.SPACE

        try:
            return key.decode()

        except UnicodeDecodeError:
            return None

    def _read_escape_sequence(self):
        sequence = b"\x1b"

        while select.select(
            [self.fd],
            [],
            [],
            0.01,
        )[0]:
            sequence += os.read(self.fd, 1)

        if sequence == b"\x1b":
            return Key.ESCAPE

        return ESCAPE_SEQUENCES.get(sequence)