# gotchas.md

Traps that cut across areas. One line per entry, added at the end:
`- YYYY-MM-DD | source | X fails; do Y`. Date = last verified.

- 2026-11-22 | external | A web page cannot read satellite count or signal strength from the phone; the browser location API has no such fields. Compute satellites overhead from orbit data instead and label it as computed.
- 2026-11-22 | external | Antigravity has a size limit on rule files (reported as 12,000 characters, unverified). Keep AGENTS.md short and put detail in .memory/.
- 2026-11-22 | .gitattributes | `merge=union` keeps both sides' lines but can leave a duplicate or an odd order. Only add lines at the end of union files; never edit or reorder existing lines on a branch.
- 2026-11-22 | external | Pyodide downloads when the page first opens and that takes a few seconds (unverified how many). Show a loading message so the two-minute clock does not start on a blank page.
- 2026-11-22 | .github/workflows/tests.yml | The test workflow uses Python 3.12. Pyodide ships its own Python version; when the Pyodide version is chosen, match the workflow to it (unverified).
