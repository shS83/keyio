# KEYiO UTF-8 input fix

This fix changes `src/keyio/_posix.py` and adds `tests/test_utf8.py`.
It makes non-blocking reads recognize Unicode characters such as
`ä Ä ö Ö å Å`, as well as three- and four-byte UTF-8 characters.
It also avoids swallowing consecutive arrow keys in an escape sequence.
The public `Keyboard` / `Key` interface is unchanged.
Windows already reads umlauts as Unicode via `msvcrt.getwch()` and is not modified.

## Apply

From the root of your existing `shS83/keyio` checkout:

```bash
git apply --check ~/Downloads/keyio_utf8_fix.patch
git apply ~/Downloads/keyio_utf8_fix.patch
uv run python -m unittest discover -s tests -v
```

Use the actual download location instead of `~/Downloads/` if needed.
If the repo differs from the checked public sources, inspect `git diff`
before or after applying the patch.

## Live keyboard test

Copy `examples/test_unicode.py` from this ZIP to the project's
`examples/` directory, then run:

```bash
uv run python examples/test_unicode.py
```

Type `ä Ä ö Ö å Å`, use arrow keys, then Esc to quit.

## Publish

```bash
git diff --check
git add src/keyio/_posix.py tests/test_utf8.py
git commit -m "fix: decode UTF-8 keyboard input on POSIX"
git push
```

Tests: 8 simulated POSIX-input tests pass. A local Linux pseudo-terminal
integration test also passed. Real Windows hardware was not tested.
