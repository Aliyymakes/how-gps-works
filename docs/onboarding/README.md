# Onboarding: start here

This folder teaches a new teammate the whole codebase before the interview. You need basic Python or basic JavaScript, not both. Every claim names a real file and function so you can open it.

## What the project does

1. It is one web page ([index.html](../../index.html)) that shows how a phone works out where it is from GPS satellite signals.
2. A signal's travel time is a distance, so the phone finds its position by measuring time.
3. You make the phone's clock wrong on a slider and watch the distance lines on a small ground map pull apart.
4. The page has four parts, each labelled "Part N of 4". Part 1 opens with a small drawing and walks you through three steps (drag the slider, press the solve button, switch a satellite off). Parts 2 to 4 show why satellite layout (DOP), noise in the signal (C/A code matching; you slide the phone's copy of the code by hand, then let the phone search) and satellite clock drift (relativity, as two clocks and two maps) matter. The ground map, the sky diagram, the signal's three rows and both relativity cards each have a "What you're looking at" line above them.
5. The maths is the team's own Python in [mechanism/](../../mechanism/), run in your browser through Pyodide. The JavaScript in [web/](../../web/) only draws and calls Python.

## Reading order

Do these in order. Each one assumes the ones before it.

1. This file. Then, to read the code itself line by line, [../annotated/how-to-read-code.md](../annotated/how-to-read-code.md).
2. [architecture.md](architecture.md): every folder and file, and how the page and Python connect.
3. [follow-one-click.md](follow-one-click.md): one slider drag and one button press, from browser event to pixels.
4. [code-tour.md](code-tour.md): each code file, its key lines, and the question a judge will ask about it.
5. [decisions.md](decisions.md): why we chose what we chose, and what each choice costs.
6. [glossary.md](glossary.md): look terms up here at any point. Keep it open while you read the others.
7. [self-check.md](self-check.md): questions with hidden answers, to test yourself.

## Run it locally

From the repository root. Commands come from [.memory/commands.md](../../.memory/commands.md) and [README.md](../../README.md).

- Tests: `pip install -r requirements-dev.txt` (unverified), then `python -m pytest -q`. Run it from the repo root: [pytest.ini](../../pytest.ini) sets `pythonpath = .` so `import mechanism` works.
- The page: `python3 -m http.server 8000`, then open <http://localhost:8000/>. commands.md says first paint was checked. Opening `index.html` straight from a file (`file://`) does not work, because module imports and `fetch` need http (gotchas.md, 2026-11-23, written about bridge-test.html; index.html uses the same module imports and `fetch`, so the same holds).
- The page loads Pyodide and numpy from a CDN, so it needs an internet connection. A first visit downloads about 9 MB (9.7 s to 44.8 s measured in the audit; later visits 2.4 s to 3.0 s; gotchas.md, 2026-11-24). While it loads, the page says "Step 1 of 2: downloading Python and numpy. This is the slow step on a first visit…", and under it the first screen adds "The first visit can take up to a minute on a phone." (the `load-note` line in `index.html`, hidden by `first-screen.js` once Python is ready). If the download fails it offers "Try again". I did not run the page in a browser to write this folder; the browser checks are in `tests/ui/` (Playwright, run with `UI_TESTS=1`, see [architecture.md](architecture.md)).
- Bridge test page: `http://localhost:8000/web/bridge-test.html` (unverified).
- Relativity check script: `python scripts/check_relativity.py` (commands.md lists it without an "unverified" mark).

## Rules to know

[AGENTS.md](../../AGENTS.md) and [CONTRIBUTING.md](../../CONTRIBUTING.md) say how the team works: one issue per branch, never push to `main`, merge through a pull request, stage files by name. The contract between Python and the page is [docs/interface.md](../interface.md).
