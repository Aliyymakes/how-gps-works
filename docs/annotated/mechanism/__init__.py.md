# __init__.py, line by line

Source: `mechanism/__init__.py`

## What this file is for
This file is empty on purpose. In Python, a folder that holds code files is treated as a "package" (a named bundle of files) when it contains a file called `__init__.py`. That is what lets other files write lines such as `from mechanism.coords import latlon_to_xyz`.

## Which files it talks to
- Every file in `mechanism/` (such as `coords.py`, `mapview.py` and `constants.py`): the empty file marks the folder as the `mechanism` package, so they can import each other by that name.
- `web/bridge.js`: copies it into the browser together with the other mechanism files, so the `mechanism` package also exists there.
- It imports nothing, and no code uses anything from inside it (there is nothing inside).

## In three lines
1. The file exists only so Python knows `mechanism/` is a package.
2. It has no lines of code, so there is nothing to run.
3. Deleting it could break `from mechanism.xxx import ...` lines in some setups, so it stays.

## The code, line by line
The file has no lines, so there is nothing to explain here.
