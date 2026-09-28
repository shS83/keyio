import msvcrt

from .keys import Key


WINDOWS_EXTENDED_KEYS = {
    "H": Key.UP,
    "P": Key.DOWN,
    "K": Key.LEFT,
    "M": Key.RIGHT,
    "G": Key.HOME,
    "O": Key.END,
    "R": Key.INSERT,
    "S": Key.DELETE,
    "I": Key.PAGE_UP,
    "Q": Key.PAGE_DOWN,
}


class WindowsKeyboard:

    def setup(self):
        pass

    def restore(self):
        pass

    def read(self):
        if not msvcrt.kbhit():
            return None

        key = msvcrt.getwch()

        # Extended key
        if key in ("\x00", "\xe0"):
            key = msvcrt.getwch()

            return WINDOWS_EXTENDED_KEYS.get(key)

        if key == "\r":
            return Key.ENTER

        if key == "\x1b":
            return Key.ESCAPE

        if key == "\t":
            return Key.TAB

        if key == "\x08":
            return Key.BACKSPACE

        if key == " ":
            return Key.SPACE

        return key