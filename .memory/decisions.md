# decisions.md

Implementation decisions. One line per entry, added at the end:
`- YYYY-MM-DD | source | text` (source = the file it affects, `user` when Icarus decided, `external` for a tool's behaviour). Date = last verified. A reversed decision is removed. Calls made without Icarus are marked `provisional`.

- 2026-11-22 | AGENTS.md, CLAUDE.md | AGENTS.md is the one instruction file for all agents; CLAUDE.md contains only `@AGENTS.md`. Reason: Codex and Antigravity read AGENTS.md, and Claude Code reads AGENTS.md directly only when no CLAUDE.md exists, so the import makes it certain.
- 2026-11-22 | .gitattributes | decisions.md, gotchas.md, commands.md and overview.md use git's `merge=union`, so lines added on two branches are both kept without a conflict. Reason: four people append to these files at once.
- 2026-11-22 | user | Goals, bugs and progress are GitHub Issues plus a Projects board, not files in .memory/. Reports are the pull request text.
- 2026-11-22 | docs/interface.md | Only plain numbers, strings, lists and dicts cross between Python and JavaScript. Reason: simple to convert in Pyodide and simple to explain. provisional
