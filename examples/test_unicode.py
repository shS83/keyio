"""Manual KEYiO input test: run from an interactive terminal."""

import time

from keyio import Key, Keyboard

print("Paina ä Ä ö Ö å Å ja kokeile nuolinäppäimiä. Esc lopettaa.")

with Keyboard() as keyboard:
    while True:
        key = keyboard.read()
        if key == Key.ESCAPE:
            break
        if key is not None:
            print(f"Näppäin: {key!s} / {key!r}")
        time.sleep(0.01)
