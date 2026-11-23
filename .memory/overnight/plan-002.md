# Plan 002: takeover run for aliyymakes (written 2026-11-23 21:10 WIB)

The teammates' goals #1 (solver fix), #2 (coordinates and measurements), #3 (bridge) and #4 (map lines) have not moved and everything on the page waits on them. This run builds them, merges them, and gets the first screen running on real results. Log to `.memory/overnight/state-002.md`. Re-read this plan before each item.

## How to run it cheaply

The main session (Opus) plans, hands out work, reviews and merges. It writes little code itself. Pick the cheapest model that can do each piece well (Icarus, 2026-11-23 21:20):
- **Fable** subagent: the hardest decisions and tasks only. A bug that Opus and Sonnet both failed to fix; deciding what the relativity result (item 8) means and how to show it honestly; any case where the spec, the contract and the code disagree and a call has to be made.
- **Opus** (you, or an Opus subagent): hard work. Reviewing the maths in solver.py, coords.py, scenario.py, mapview.py, geometry.py and signal.py; debugging a failing integration between the page and Python.
- **Sonnet** subagent: regular work. Writing code and tests, wiring the page, drafting the README and interview answers, the bug sweep.
- **Haiku** subagent: easy work. Running tests, checking a pull request against its "Done when" list, checking page files against docs/ui-guide.md, small fixes, formatting.

The subagent that built something never checks it. Give each subagent only its item, the files to read and touch, and the done checks; never pass this whole plan.

## Approved for this run (Icarus, by pasting this plan)

- Creating branches, issues, pull requests and issue comments in Aliyymakes/how-gps-works.
- **Merging pull requests** that meet all of: GitHub's test run passed, a separate reviewer subagent passed it against its issue's "Done when" list, and for mechanism code you reviewed the maths. Use `gh pr merge <n> --merge`. Never force push, never push straight to main.
- Installing a browser tool on this machine only (for example `pip install playwright` and its Chromium) to take screenshots. Never add it to the repo or requirements files.
- Not approved: making the repo public, GitHub Pages, a LICENSE, any new dependency in the repo, editing design.md, his-words.md, directives.md, decision-map.md, start.md. docs/interface.md is the contract: code changes to match it, not the other way round.

## Rules for this run

- Follow .memory/start.md and the away rules in directives.md. Taste calls go in the report as Questions for Icarus with a recommendation.
- Before each takeover item: `gh pr list --state open` and `git ls-remote --heads origin`. If a teammate has opened a pull request or pushed a branch for that issue since 21:00, do not build it: review theirs against its issue instead, write the review as a PR comment, merge it if it passes, otherwise list what to fix and move on.
- When you take an issue: assign @me and comment "Taken over by aliyymakes's agent so the page is not blocked. @<owner>, please read the pull request line by line before the interview; you may be asked about it."
- Branch from up-to-date origin/main after each merge (`git fetch` then branch from `origin/main`).
- If a merge conflicts only in `.memory/` log files, merge origin/main into the branch locally (the union driver keeps both sides), push the branch, then merge the pull request. Never delete other people's lines.
- If a check needs something you do not have, add it to the at-home list in state-002.md and move on. Do not loop. If usage runs low, stop at a clean point and write where to resume.
- Stop when the list is done or 12 hours after the paste. Items 1 to 7 come first; if time or usage runs short, cut from the bottom.

## The list

1. **Clean main and fix the solver (issue #1).** On branch `1-solver-fix`: change mechanism/solver.py and tests/test_solver.py to match docs/interface.md exactly (satellites as `{"id","x_m","y_m","z_m"}`, result and every step with `x_m`, `y_m`, `z_m`, `clock_error_s`, plus `converged` and `steps`). Keep tw-2866's method and comments; change only what the contract needs. Move the test satellites above the receiver's horizon. Delete `gnss_solver_standalone (1).zip` and `mechanism/test_solver.py`. All #1 done checks pass. Merge, close #1.

2. **Coordinates and measurements (issue #2).** mechanism/coords.py, mechanism/scenario.py, the two constants, tests, exactly as issue #2 says (look the constants up in a reliable source, record it in decisions.md). Merge.

3. **Map lines (issue #4).** mechanism/mapview.py and tests, exactly as issue #4 says, on top of merged coords.py. Merge.

4. **Rung 2 and 3 maths.** A reviewer subagent checks PR #14 and PR #16 against issues #7 and #8; update each branch with origin/main if needed; merge. Comment on each tagging the absent reviewer (tw-2866 for #14, scoobertfan for #16) to read it before the interview.

5. **Bridge (issue #3).** web/bridge.js and web/bridge-test.html exactly as issue #3 says. The file list loads: `__init__.py`, `constants.py`, `coords.py`, `scenario.py`, `solver.py`, `mapview.py`, `geometry.py`, `signal.py`, `relativity.py` (missing files: one console warning). Prove it in a real browser: serve with `python -m http.server 8000`, open web/bridge-test.html, screenshot it, record the measured load time in gotchas.md. Merge.

6. **First screen live (PR #17, issue #5).** Update the branch with origin/main. Remove anything waiting-related; wire every call to the real functions. In a real browser at 390 px and 1200 px, check every #5 done item: green on load with lines meeting; slider at 1 µs pulls the lines apart and shows the solver's error; "Let the phone solve for its clock" makes them meet within 1 m and says about 1.00 µs; one satellite off with the clock solved gives the refusal sentence. Screenshots in the pull request. A Haiku subagent checks it against docs/ui-guide.md. Merge.

7. **Layer sections live (PR #18 and PR #19).** Same as item 6 for each: update, wire to real functions, check in a browser, screenshots, merge. If wiring them into index.html is not in their issues, leave index.html alone and list "add sections to index.html" as a question for Icarus.

8. **Relativity check.** scripts/check_relativity.py on a new issue: add the same daily clock drift (the value in docs/facts.md) to every satellite's measurement, solve with the clock solved and with the clock trusted, and print both position errors. Put the result and what it means for rung 4 in the pull request. Merge.

9. **Put the layers on the page.** On a new issue: add the rung 2 and rung 3 sections to index.html below the first screen, in ladder order, each opening with a "but" or "therefore" line that links it to the step before (docs/ui-guide.md section 1). Wording is a draft: list every new sentence under Questions for Icarus. Check in a browser at 390 px and 1200 px, screenshots, merge.

10. **Rung 4 on the page, only if item 8 gives a clear result.** A small section that shows what item 8 found, honestly: if the shared drift is absorbed by the clock solve, show the range error growing per hour and the position staying put when the clock is solved, with one sentence saying why. Uses mechanism code from item 8 moved into mechanism/relativity.py with tests. Add its functions to the pull request description as a proposed docs/interface.md change for Icarus (do not edit interface.md). Merge only if all checks pass.

11. **Load speed and first two minutes.** Measure the time from opening index.html to controls working, on a cold load and a reload. If over 8 seconds, find the cheapest cut (for example loading only the mechanism files the first screen needs before the rest). Make sure the question and one sentence are readable within 1 second. Record numbers in gotchas.md. Merge.

12. **Phone and keyboard pass.** At 390 px and 1200 px: every control reachable by Tab, visible focus, touch targets at least 44 px, nothing overflows sideways, reduced-motion respected. A Haiku subagent runs the checklist from docs/ui-guide.md section 4; fix what fails. Merge.

13. **Judge-facing README.** Rewrite README.md for a judge: one line on what it is, how to try it (the live link: write `LIVE LINK TBA`), how it works in five short bullets, what is simplified, the components we did not write and why, the team. Numbers only from docs/facts.md. Merge.

14. **Fill the interview prep and project page.** Now that the code is merged, fill every empty answer in docs/interview-prep.md from the real code (file and function names), and update docs/project-page.md with real screenshots. Merge.

15. **Bug sweep.** A Sonnet subagent uses the page like a first-time judge for 10 minutes in the browser: every control, every extreme (all satellites off, slider at max, noise at max, fast repeated clicks). Each bug becomes an issue with the Bug template; fix the ones that are cheap and clear, merge, leave the rest listed.

16. **Teammate hand-off.** Comment once on each of #1, #2, #3, #4 summarising what was built and what the owner should be able to explain on camera (3 to 5 bullet points each).

17. **Report.** `.memory/overnight/report-2026-11-24.md`: what was done with links, what was verified (with screenshots) and what was not, Questions for Icarus with a recommendation each, the at-home list. Open it as a pull request and merge it. Then stop.
