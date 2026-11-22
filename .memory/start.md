You're continuing the GPS hackathon entry: an interactive web page that shows how a phone works out its position from satellite signals, in this folder. overview.md says what is built.

Start by reading .memory/INDEX.md, directives.md, overview.md and gotchas.md. Read decisions.md, commands.md, docs/interface.md and design.md only in the parts the issue names; INDEX.md says which file holds what. design.md is the source of truth, in dated sections where later ones override earlier ones: "TBA" means Icarus decides later (leave a clearly named placeholder), "Proposed" means use it but it can change, placeholder numbers live in one config file per area, never inline.

Your work is one GitHub issue: `gh issue view <number>`. If `gh` is not installed or not signed in, stop and tell your human.

Before you write anything, claim the work and check for overlap:
1. `gh issue view <number> --json assignees,state`. If it is closed or assigned to someone other than your human, stop and say so.
2. `gh issue edit <number> --add-assignee @me` so everyone can see it is taken.
3. `git pull` on main, then `gh pr list --state open`. For each open pull request run `gh pr diff <pr> --name-only`. If one touches a file your issue lists under "Files this will touch", stop and tell your human before editing it.
4. Edit only the files the issue lists. If you need another file, comment on the issue first (`gh issue comment <number> --body "..."`), then go on.
Agents never talk to each other directly. The issue, its comments and the open pull requests are how everyone knows who is doing what.

Rules:
- Work on a branch named `<issue number>-<short-name>`. Never commit to main. Open a pull request that closes the issue, fill in every part of the template, then stop.
- Stay in the issue's area. mechanism/ is Python (numpy allowed), run in the browser later through Pyodide. index.html and web/ are the page. Do not change docs/interface.md unless the issue says so.
- The mechanism is the team's own code and computes its outputs from the user's inputs. No prepared results. No hosted AI service in the mechanism.
- Write code a beginner on the team can explain: short functions, plain names, a comment only where the reason is not obvious.
- Smallest correct change, existing patterns, no new dependencies without asking Icarus, no refactors outside the issue.
- Taste calls the spec does not settle (looks, names, layout, wording, sounds): ask, don't decide. Technical calls: decide, and write what you decided in decisions.md.
- Add nothing the issue and the spec do not show. Never guess or make things up.
- Only Icarus edits design.md, his-words.md, directives.md, decision-map.md and start.md. If you think the spec is wrong or contradicts itself, stop and say so in the pull request under "Questions for Icarus".
- Keep .memory/ current before you finish: decisions.md (date and reason), gotchas.md, one dated line in overview.md, commands.md. Each file states its line format at the top. Add lines at the end of the file; do not reorder or rewrite other people's lines.
- Stage files by name only. Never `git add .` or `-A`. Never force push. Never rewrite history.
- Say plainly what you verified and what you could not. If a check needs something you don't have (a phone, a real browser, another person), don't retry or loop: write it under "Not verified" and finish.
- A found bug that is not part of your issue becomes a new issue (`gh issue create`, Bug template). Do not fix it in this branch.

Then wait for the issue number.
