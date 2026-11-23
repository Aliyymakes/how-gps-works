# State 002: away run log for plan-002

Started 2026-11-23 by Claude Code (Opus) for aliyymakes. One entry per item: what was done, branch, pull request, verified / not verified.

## Log

- setup | Read start.md, directives, overview, gotchas, plan-002. origin/main cc02d4e. No teammate PR or branch for #1-#4. Test env: scratch venv (Python 3.15, numpy 2.5.5); CI uses 3.12.
- item 1, 2 | Claimed #1 and #2 (assigned, takeover comments). Worktrees .wt/1-solver-fix and .wt/2-coords from origin/main.

- item 5 (started early, independent of 1-3) | Claimed #3 (assigned, takeover comment). Worktree .wt/3-bridge.
- item 1 | Sonnet fixed solver.py/test_solver.py to the contract (12 tests); zip and duplicate test removed. Opus reviewed diff (keys and constant only). PR https://github.com/Aliyymakes/how-gps-works/pull/24.
- item 2 | Sonnet built coords.py, scenario.py, constants (from facts.md rows 3, 33). Opus reviewed maths (ENU vectors, orbit quadratic). PR https://github.com/Aliyymakes/how-gps-works/pull/25.
- item 4 | Haiku reviews: PR #14 PASS against #7 (19 tests, CI pass); PR #16 PASS against #8 (23 tests, CI pass; octals for PRN 20-32 not re-checked).
- item 5 | Sonnet built web/bridge.js + web/bridge-test.html; Pyodide v314.0.8 (Python 3.14.2), CI moved to 3.14. Opus read bridge.js. BLOCKED: starting a local server / browser preview (and a subagent brief that installed Playwright) were refused by the Claude Code auto-mode permission classifier. No browser checks possible this run.
- item 1 | PR #24 Haiku review PASS, CI pass, merged. #1 closed.
- item 2 | PR #25 Haiku review PASS (constants match facts.md), CI pass, merged. #2 closed.
- item 4 | PR #14 and #16 updated with main (union merge of .memory), tests 51/63 pass, CI pass, merged. Comments tag tw-2866 (#14) and scoobertfan (#16). #7, #8 closed.
- item 5 | PR https://github.com/Aliyymakes/how-gps-works/pull/26 opened, NOT merged: its Done-when needs a browser screenshot and load times.
- item 3 | Claimed #4. Sonnet built mapview.py; Opus reviewed maths. Haiku review FAILED (inside with 2-9 points; weak wrong-clock test; KeyError on bad points). Opus fixed all three plus non-number distances; Haiku recheck PASS. PR https://github.com/Aliyymakes/how-gps-works/pull/28 merged. #4 closed.
- item 8 | Issue #27. Opus wrote scripts/check_relativity.py; Haiku review PASS. Result: shared 38 µs/day drift fully absorbed with the clock solved (0.0000 m at 0/1/6/24 h; solved clock 1 → 39 µs); trusted clock 444 m → 17.3 km. PR https://github.com/Aliyymakes/how-gps-works/pull/29 merged. Fable not used for the meaning (global rule: the most expensive model only when asked by name); Opus wrote the reading, listed as a question.
- items 10, 13 | Issues #30 (relativity.py, mechanism part only) and #31 (README) created.
- item 3 follow-up | Codex finding on #28 (corner-only line dropped). Opus fixed with a geometric crossing check; PR https://github.com/Aliyymakes/how-gps-works/pull/32; Haiku confirmed the new test fails on old code; merged. Codex thread replied and resolved.
- items 6, 7 (no browser) | Sonnet updated #17, #18, #19 with main (clean), checked every callPython against the real Python (all OK, no JS changed) and replayed the page call sequences in Python: #17 green on load (0.0 m, lines meet), 1 µs trusted → 480.7 m, solve → 0.0 m and "1.00 µs fast", 3 satellites + solve → refusal. #18 spread layout gives PDOP 28 (question). #19 found up to noise 6, lost at 12. Results posted on each PR. NOT merged: browser checks impossible.
- item 10 (mechanism part) | Sonnet built relativity.drift_over_time (#30); Opus read it; Haiku PASS; PR https://github.com/Aliyymakes/how-gps-works/pull/33 merged. Proposed interface row in the PR. Page section not built (needs browser).
- item 13 | Sonnet wrote README (#31); Opus checked fonts claim; Haiku PASS; PR https://github.com/Aliyymakes/how-gps-works/pull/34 merged. All new sentences listed as drafts.
- item 16 | Hand-off comments posted on #1, #2, #3, #4.
- item 14 | Sonnet filled 19 interview-prep answers from the real code on PR #20 (branch updated with main). Haiku review running. Project-page screenshots not possible (no browser).
- items 9, 11, 12, 15 | Skipped: each needs a real browser. On the at-home list.
- item 14 | Haiku review of #20 FAILED: bridge/page answers come from open PRs (issue #13 says leave blank), 6.6 stale, PR body wrong. Opus fixed 6.6 and the body; #20 left open with a question.
- item 13 follow-up | Codex finding on #34 (README sends readers to a page not on main): notice added in PR https://github.com/Aliyymakes/how-gps-works/pull/35; thread replied and resolved.
- item 17 | Report report-2026-11-24.md on branch overnight-002-report. Run stops after this merges.

## At-home list

- Browser checks: local server and browser preview were refused by the Claude Code auto-mode permission classifier this run (twice). Allow them, or run by hand:
  - #26 bridge: `python3 -m http.server 8000`, open /web/bridge-test.html; screenshot, console, first-visit and reload load times into the PR and gotchas.md; then merge.
  - #17 first screen: after #26 merges, check the four #5 Done-when states at 390 and 1200 px, by mouse, touch and keyboard; screenshots; Haiku ui-guide check; merge.
  - #18, #19: same; retune #18's spread layout (PDOP 28 now).
  - Item 9 (rung 2 and 3 sections in index.html), item 10 page section (rung 4), item 11 (load speed), item 12 (phone and keyboard pass), item 15 (bug sweep), project-page screenshots (item 14).
