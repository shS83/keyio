# KEYiO

**Cross-platform terminal keyboard input for Linux and Windows.**

KEYiO is a small Python library for reading keyboard input from a terminal without requiring the user to press Enter. It presents the same `Keyboard` / `Key` API on Linux (POSIX terminals) and Windows consoles. Originally developed for the RockSpock terminal game.

> **Note:** This is a terminal-input library, not a system-wide keyboard hook or hotkey listener. The application needs to run in an interactive terminal.

## Requirements

- Python **3.13+** (as declared in `pyproject.toml`)
- Linux / POSIX-compatible terminal or Windows console
- No third-party runtime dependencies

## Installation

Clone the repository:

```bash
git clone https://github.com/shS83/keyio.git
cd keyio
uv sync
```

To add your locally checked-out KEYiO as a dependency to **another uv project**:

```bash
cd /path/to/your-project
uv add --editable ../keyio
```

Adjust `../keyio` to point to your local KEYiO project. Alternatively, install it from GitHub in your uv project:

```bash
uv add git+https://github.com/shS83/keyio.git
```

Or, with pip, install a local clone into your Python environment:

```bash
python -m pip install -e /path/to/keyio
```

**Do not use `pip install keyio` to install this project.** A different package with the same name already exists on PyPI. Use the local path or GitHub URL above.

## Quick start

Create a `demo.py` file in a project where KEYiO is installed:

```python
import time
from keyio import Keyboard, Key

print("Press arrow keys or type. Press Esc to quit.")

with Keyboard() as keyboard:
	while True:
		key = keyboard.read()

		if key is None:
			time.sleep(0.01)
			continue

		if key == Key.ESCAPE:
			break
		elif key == Key.LEFT:
			print("Left arrow")
		elif key == Key.RIGHT:
			print("Right arrow")
		elif key == Key.UP:
			print("Up arrow")
		elif key == Key.DOWN:
			print("Down arrow")
		elif key == Key.ENTER:
			print("Enter")
		else:
			print(f"Key: {key!r}")

print("Terminal settings restored.")
```

Run it from an interactive terminal:

```bash
uv run python demo.py
```

Or use `python demo.py` in the Python environment where the library was installed.

## API

### `Keyboard()`

Constructs the platform-appropriate input backend automatically:

- Linux/POSIX: `PosixKeyboard` using `termios`, `tty` and `select`.
- Windows: `WindowsKeyboard` using `msvcrt`.

### `with Keyboard() as keyboard:`

Calls `setup()` when entering and `restore()` when leaving the context. **This is the recommended way** to use the library because it restores terminal settings even if the loop raises an exception.

### `keyboard.read()`

Non-blocking read of one keypress. Returns:

- A `Key` value for a recognized special key.
- A one-character `str` for an ordinary character.
- `None` if no keypress is waiting, or the input is not recognized.

Because this is non-blocking, add a small sleep when polling in a loop to avoid using unnecessary CPU.

### `keyboard.setup()` / `keyboard.restore()`

You can manage the terminal explicitly when a context manager is not convenient:

```python
from keyio import Keyboard, Key

keyboard = Keyboard()
keyboard.setup()
try:
	key = keyboard.read()
	print(key)
finally:
	keyboard.restore()
```

### Special keys (`Key`)

| Value | Meaning |
| --- | --- |
| `Key.LEFT` | Left arrow |
| `Key.RIGHT` | Right arrow |
| `Key.UP` | Up arrow |
| `Key.DOWN` | Down arrow |
| `Key.ENTER` | Enter |
| `Key.ESCAPE` | Escape |
| `Key.SPACE` | Spacebar |
| `Key.TAB` | Tab |
| `Key.BACKSPACE` | Backspace |
| `Key.HOME` | Home |
| `Key.END` | End |
| `Key.INSERT` | Insert |
| `Key.DELETE` | Delete |
| `Key.PAGE_UP` | Page Up |
| `Key.PAGE_DOWN` | Page Down |

`Key` is a `StrEnum`, so these values are also strings (for example, `Key.LEFT == "LEFT"`). Prefer the enum constants rather than hard-coded strings.

## Source layout

```text
src/keyio/
├── __init__.py   # Public Keyboard and Key imports
├── keyboard.py   # Cross-platform interface and context manager
├── keys.py       # Special-key enum
├── _posix.py     # Linux/POSIX backend
└── _windows.py   # Windows backend
```

## Current limitations

- KEYiO reads keys sent to the **active terminal**, not keyboard activity in other applications. It does not require X11 or Wayland specifically.
- The POSIX backend reads one input byte at a time. Some multibyte UTF-8 characters (including Finnish letters) may not currently decode correctly.
- The POSIX backend recognizes common terminal escape sequences; some terminals may emit different sequences, especially for modified key combinations.
- `keyboard.read()` is a polling operation, not a blocking call; code should handle `None`.
- Windows key recognition relies on console input via `msvcrt`.

## Development

The package is built with `uv_build` and declares no runtime dependencies. Use `uv sync` to set up the project. When adding functionality, keep `Keyboard` and `Key` as the stable public API and add platform-specific implementations in the appropriate backend.

## Repository

https://github.com/shS83/keyio
