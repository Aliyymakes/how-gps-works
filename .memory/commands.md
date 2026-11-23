# commands.md

One line per entry, added at the end: `- YYYY-MM-DD | source | purpose: command`. Anything nobody has run is marked `(unverified)`.

- 2026-11-22 | requirements-dev.txt | install test tools: `pip install -r requirements-dev.txt` (unverified)
- 2026-11-22 | tests/ | run the tests: `python -m pytest -q`
- 2026-11-22 | external | read an issue: `gh issue view <number>` (unverified)
- 2026-11-22 | external | open a pull request: `gh pr create --fill` (unverified)
- 2026-11-22 | external | report a bug: `gh issue create --template bug.md` (unverified)
- 2026-11-22 | scripts/setup-github.sh | one-time repo setup, run by Icarus in his own terminal: `bash scripts/setup-github.sh <repo-name> <public|private>` (unverified)
- 2026-11-22 | external | serve the page locally from the repo root: `python -m http.server 8000` then open http://localhost:8000 (unverified, no page exists yet)
- 2026-11-23 | scripts/create-issues-wave1.sh | invite teammates and create the first three goals, run once by Icarus: `bash scripts/create-issues-wave1.sh` (unverified)
- 2026-11-23 | scripts/create-issues-wave2.sh | create the map and first-screen goals, run once by Icarus: `bash scripts/create-issues-wave2.sh` (unverified)
- 2026-11-23 | web/ | try the bridge: `python3 -m http.server 8000` from the repo root, open http://localhost:8000/web/bridge-test.html (unverified)
