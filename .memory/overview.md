# overview.md

What is built. One dated line per merged issue, added at the end: `- YYYY-MM-DD | #issue | what now exists`.

## Area map
- `mechanism/` Python mechanism (runs in the browser through Pyodide). Owners: tw-2866, scoobertfan.
- `tests/` tests for the mechanism.
- `index.html`, `web/` the page. Owners: jstnstyad10, aliyymakes. Neither exists yet.
- `docs/interface.md` the contract between the two.

## Built
- 2026-11-22 | setup | Team system only: AGENTS.md, CLAUDE.md, CONTRIBUTING.md, .memory/, issue and pull request templates, test workflow, one smoke test. No project code yet. Not yet pushed to GitHub.
- 2026-11-23 | #11 | docs/project-page.md: draft project page text (idea, rungs, simplifications, components, team); numbers only from docs/facts.md.
- 2026-11-23 | #6 | docs/facts.md: every number the page and documents use, each with a source link and exact quoted value, re-checked by a second reviewer. Use only rows not marked unconfirmed.
- 2026-11-23 | #1 | mechanism/solver.py matches docs/interface.md: satellites and results as x_m/y_m/z_m dicts, steps from the Earth's centre; tests use satellites above the horizon. Duplicate mechanism/test_solver.py and the zip removed.
