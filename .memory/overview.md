# overview.md

What is built. One dated line per merged issue, added at the end: `- YYYY-MM-DD | #issue | what now exists`.

## Area map
- `mechanism/` Python mechanism (runs in the browser through Pyodide). Owners: tw-2866, scoobertfan.
- `tests/` tests for the mechanism.
- `index.html`, `web/` the page. Owners: jstnstyad10, aliyymakes. Neither exists yet.
- `docs/interface.md` the contract between the two.

## Built
- 2026-11-22 | setup | Team system only: AGENTS.md, CLAUDE.md, CONTRIBUTING.md, .memory/, issue and pull request templates, test workflow, one smoke test. No project code yet. Not yet pushed to GitHub.
- 2026-11-23 | #7 | mechanism/geometry.py: `dop(receiver, satellites)` gives GDOP, PDOP, TDOP from the satellite directions; tests in tests/test_geometry.py.
- 2026-11-23 | #11 | docs/project-page.md: draft project page text (idea, rungs, simplifications, components, team); numbers only from docs/facts.md.
- 2026-11-23 | #6 | docs/facts.md: every number the page and documents use, each with a source link and exact quoted value, re-checked by a second reviewer. Use only rows not marked unconfirmed.
