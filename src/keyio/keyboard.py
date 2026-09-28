import os


if os.name == "nt":
    from ._windows import WindowsKeyboard as Backend

else:
    from ._posix import PosixKeyboard as Backend


class Keyboard:

    def __init__(self):
        self.backend = Backend()

    def setup(self):
        self.backend.setup()

    def restore(self):
        self.backend.restore()

    def read(self):
        return self.backend.read()

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.restore()