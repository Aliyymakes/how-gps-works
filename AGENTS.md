# AGENTS.md

This repo is a hackathon entry: an interactive web page that shows how a phone works out its position from GPS satellite signals. Four people work on it, each with their own AI agent (Claude Code, Codex or Antigravity). Submissions close 26 Nov 2026 18:59 WIB (25 Nov 23:59 AoE).

This file is the one instruction file every agent reads. Keep it short. Detail lives in `.memory/`.

## Before you do anything

Read `.memory/start.md` and follow it. It names the other files to read.

## Rules that never bend

1. One issue per session. The work is the GitHub issue you were given (`gh issue view <number>`). Do that, open a pull request, then stop.
2. Never push to `main`. Work on a branch named `<issue number>-<short-name>` and merge through a pull request.
3. Stay in your area. `mechanism/` is Python. `web/` and `index.html` are the page. `docs/interface.md` is the contract between them. Do not change the contract without an issue that says so.
4. `.memory/design.md` is the spec. Work that disagrees with it is wrong until Icarus changes it. Only Icarus (or his orchestrator chat) edits `design.md`, `his-words.md`, `directives.md`, `decision-map.md` and `start.md`.
5. Add nothing the issue and the spec do not ask for. Never guess. If something cannot be known, say so in the pull request under "Questions for Icarus".
6. Stage files by name. Never `git add .` or `git add -A`. Never force push. Never rewrite history.
7. The mechanism must be the team's own code and must compute its outputs from the user's inputs. No prepared results, no hosted AI in the mechanism.
8. Every teammate must be able to explain the code they merge. Write simple code, and fill in the "Explain it" part of the pull request in plain words.
9. Say plainly what you verified and what you could not.
10. Any work on the page (`index.html`, `web/`) follows `docs/ui-guide.md`. Read it before writing page code.
