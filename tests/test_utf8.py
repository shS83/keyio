"""POSIX backend tests: fake terminal bytes, no interactive TTY needed."""

import os
import sys
import unittest
from collections import deque
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from keyio._posix import PosixKeyboard
from keyio.keys import Key


@unittest.skipUnless(os.name == "posix", "POSIX tests only")
class PosixUtf8Tests(unittest.TestCase):
    def setUp(self):
        self.keyboard = PosixKeyboard()
        self.keyboard.fd = 42
        self.bytes = deque()

        def fake_select(read, write, error, timeout):
            return (read if self.bytes else [], [], [])

        def fake_read(fd, count):
            self.assertEqual(fd, 42)
            return bytes((self.bytes.popleft(),)) if self.bytes else b""

        self.select_patch = patch("keyio._posix.select.select", side_effect=fake_select)
        self.read_patch = patch("keyio._posix.os.read", side_effect=fake_read)
        self.select_patch.start()
        self.read_patch.start()
        self.addCleanup(self.select_patch.stop)
        self.addCleanup(self.read_patch.stop)

    def feed(self, data):
        self.bytes.extend(data)

    def drain(self):
        results = []
        while self.bytes or self.keyboard._pending_keys:
            result = self.keyboard.read()
            if result is not None:
                results.append(result)
        return results

    def test_finnish_letters(self):
        self.feed("äÄöÖåÅ".encode("utf-8"))
        self.assertEqual(self.drain(), list("äÄöÖåÅ"))

    def test_unicode_2_3_4_bytes(self):
        self.feed("é€🔥".encode("utf-8"))
        self.assertEqual(self.drain(), ["é", "€", "🔥"])

    def test_partial_sequence_never_blocks(self):
        self.feed(b"\xc3")
        self.assertIsNone(self.keyboard.read())
        self.assertIsNone(self.keyboard.read())
        self.feed(b"\xa4")
        self.assertEqual(self.keyboard.read(), "ä")

    def test_ascii_and_control_keys(self):
        self.feed(b"a \r\t\x7f")
        self.assertEqual(self.drain(), ["a", Key.SPACE, Key.ENTER, Key.TAB, Key.BACKSPACE])

    def test_arrow_and_escape(self):
        self.feed(b"\x1b[A\x1b")
        self.assertEqual(self.drain(), [Key.UP, Key.ESCAPE])

    def test_consecutive_arrow_keys_and_unicode(self):
        self.feed(b"\x1b[A\x1b[B" + "Ä".encode("utf-8"))
        self.assertEqual(self.drain(), [Key.UP, Key.DOWN, "Ä"])

    def test_invalid_utf8_does_not_swallow_following_ascii(self):
        self.feed(b"\xc3Z")
        self.assertEqual(self.drain(), ["\ufffd", "Z"])

    def test_partial_utf8_followed_by_control(self):
        self.feed(b"\xc3\r")
        self.assertEqual(self.drain(), ["\ufffd", Key.ENTER])


if __name__ == "__main__":
    unittest.main()
