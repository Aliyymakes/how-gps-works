# decisions.md

Implementation decisions. One line per entry, added at the end:
`- YYYY-MM-DD | source | text` (source = the file it affects, `user` when Icarus decided, `external` for a tool's behaviour). Date = last verified. A reversed decision is removed. Calls made without Icarus are marked `provisional`.

- 2026-11-22 | AGENTS.md, CLAUDE.md | AGENTS.md is the one instruction file for all agents; CLAUDE.md contains only `@AGENTS.md`. Reason: Codex and Antigravity read AGENTS.md, and Claude Code reads AGENTS.md directly only when no CLAUDE.md exists, so the import makes it certain.
- 2026-11-22 | .gitattributes | decisions.md, gotchas.md, commands.md and overview.md use git's `merge=union`, so lines added on two branches are both kept without a conflict. Reason: four people append to these files at once.
- 2026-11-22 | user | Goals, bugs and progress are GitHub Issues plus a Projects board, not files in .memory/. Reports are the pull request text.
- 2026-11-22 | docs/interface.md | Only plain numbers, strings, lists and dicts cross between Python and JavaScript. Reason: simple to convert in Pyodide and simple to explain. provisional
- 2026-11-23 | docs/interface.md, mechanism/coords.py | The Earth is a sphere of one radius, not the real slightly flattened shape. Reason: the conversions are a few lines anyone on the team can explain, and the simulated truth and the solver use the same model so results stay exact. The page must say this is a simplification. provisional
- 2026-11-23 | docs/interface.md | mechanism file names are fixed up front (constants, coords, scenario, solver, later signal and relativity) so the page's loader can list them once and two mechanism goals never edit the same file.
- 2026-11-23 | web/theme.css, web/theme.js | Instrument theme built new for this project from docs/ui-guide.md section 2 (no earlier files existed here). Fonts load from Google Fonts. Colours approved by Icarus 2026-11-23 as a first draft; radii, spacing and the switched-off satellite style are still open.
- 2026-11-23 | web/step-geometry.js | Rung 2 solves the clock (`solve_clock=true`) with fixed measurement noise and seed, so the position error shown is the noise multiplied by the layout, which is what DOP measures. The satellite angles are a straight blend between a spread set and a bunched set in `geometryConfig`. provisional
- 2026-11-23 | web/step-geometry.js, web/step-signal.js | Each rung section exports a `mount...Step(container)` function and injects its own scoped `<style>` once, so the first screen can drop it in later; a dev page under web/dev/ mounts it alone. provisional
