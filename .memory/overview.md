# overview.md

What is built. One dated line per merged issue, added at the end: `- YYYY-MM-DD | #issue | what now exists`.

## Area map
- `mechanism/` Python mechanism (runs in the browser through Pyodide). Owners: tw-2866, scoobertfan.
- `tests/` tests for the mechanism.
- `index.html`, `web/` the page. Owners: jstnstyad10, aliyymakes. Neither exists yet.
- `docs/interface.md` the contract between the two.

## Built
- 2026-11-22 | setup | Team system only: AGENTS.md, CLAUDE.md, CONTRIBUTING.md, .memory/, issue and pull request templates, test workflow, one smoke test. No project code yet. Not yet pushed to GitHub.
- 2026-11-23 | #5 (draft) | index.html, web/config.js, web/first-screen.js: the first screen (ground map, clock slider, solve button, satellite switches). Paints without Python; waits on bridge, coords, scenario, solver, mapview to run.
