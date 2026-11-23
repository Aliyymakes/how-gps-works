# State 001: away run log for plan-001

Started 2026-11-23 15:37 WIB by Claude Code (Opus) for aliyymakes. One entry per item: what was done, branch, pull request, verified / not verified.

## Log

- 15:37 | setup | Read start.md, directives, overview, gotchas, design.md, ui-guide.md, interface.md. origin/main at 19e7ff1: no mechanism code merged (only constants.py), no bridge.js, no open pull requests. Open goals #1 to #5.
- 15:37 | item 1 | Claimed #5 (assigned aliyymakes), commented the split.
- 15:45 | items 2-9 | Created issues: #6 facts, #7 geometry, #8 signal, #9 step-geometry, #10 step-signal, #11 project page, #12 demo script, #13 interview prep. All assigned aliyymakes.
- 15:50 | items 1-4, 8 | Worktrees under .wt/ (excluded locally). Sonnet builders started for #5, #6, #7, #8 and #12. Test env: scratch venv (Python 3.15, numpy 2.5.5, pytest 9.2.0); CI uses 3.12.
- 16:05 | item 3 | #7 done: branch 7-geometry-dop, PR https://github.com/Aliyymakes/how-gps-works/pull/14. Verified: 9 tests pass locally (3.15); spread PDOP 2.08, bunched 351; maths reviewed by Opus. Not verified: Python 3.12/Pyodide, bridge. Commented "Please also load geometry.py." on #3.
- 16:10 | item 8 | #12 done (out of order, it was independent): branch 12-demo-script, PR https://github.com/Aliyymakes/how-gps-works/pull/15. Opus fixed shots 8 and 10 (removed a sky view and a play control the plan does not have). Length left to Icarus.
- 16:25 | item 4 | #8 done: branch 8-signal-code, PR https://github.com/Aliyymakes/how-gps-works/pull/16. Verified: 11 tests pass; first 10 chips match IS-GPS-200N Table 3-Ia for PRN 1-19; shift registers reviewed by Opus. Not verified: PRN 20-32 octals (PDF text garbled), ±1 mapping inferred from Table 3-IV, 3.12/Pyodide.
- 16:35 | item 1 | Sonnet built index.html, web/config.js, web/first-screen.js on 5-first-screen (commit 5627638). Opus reviewed: calls match interface.md, no fakes, bridge import fails safely. Haiku ui-guide check running. Sonnet builders started for #9 and #10 (items 5, 6).
- 16:55 | item 1 | #5 draft PR https://github.com/Aliyymakes/how-gps-works/pull/17 (branch 5-first-screen). Haiku ui-guide check: 3 FAILs; fixed 28px font → --text-xl and uncaught Python rejection; theme.css colour/keyboard transitions listed as a question. Verified: first paint, failure sentence, disabled controls, 390/1200 px layout, call names/args. Not verified: everything needing Python (nothing merged).
- 17:10 | item 4 | PR #16 Codex review: 2 valid findings fixed (negative seed → error dict; flat/silent input → peak_to_next 1.0), tests added (13 pass), threads replied and resolved.
- 17:15 | items 5, 6 | Sonnet built web/step-geometry.js (+dev page) and web/step-signal.js (+dev page). Opus fixed rung 2 to solve the clock (it trusted the clock, so the error shown did not match what DOP measures). Haiku ui-guide check running on both. Interview prep (#13) builder started; fact sheet (#6) still researching.
- 17:40 | items 5, 6 | Haiku ui-guide check: literal font sizes fixed to theme tokens in both. Draft PRs: #9 → https://github.com/Aliyymakes/how-gps-works/pull/18 (9-step-geometry), #10 → https://github.com/Aliyymakes/how-gps-works/pull/19 (10-step-signal). Not verified: anything needing the bridge.
- 17:45 | item 9 | #13 → https://github.com/Aliyymakes/how-gps-works/pull/20 (13-interview-prep). 57 questions; solver/bridge/coords/mapview answers left to owners.
- 17:50 | item 2 | #6 → https://github.com/Aliyymakes/how-gps-works/pull/21 (6-fact-sheet). Second Sonnet re-check: 32 ok, 3 corrected, 0 unopened. Unconfirmed: sidereal day, 290 K.
- 17:50 | item 7 | #11 → https://github.com/Aliyymakes/how-gps-works/pull/22 (11-project-page). Numbers only from confirmed facts rows; Opus fixed two statements.
- 17:52 | item 10 | Skipped: origin/main has no solver.py or scenario.py. Added to at-home list.
- 18:00 | item 9 | PR #20 Codex finding fixed (DOP is transpose × table), thread replied and resolved.
- 18:00 | item 11 | Haiku final check: all 9 PRs' templates filled, no forbidden files, memory lines present, tests and CI pass; drafts #17-#19 wait on the bridge and mechanism. Report: report-2026-11-23.md. Run finished; nothing merged.

## At-home list
- #5: once #1-#4 merge, run the page: green fix on load, slider at 1 µs, solve → ~1.00 µs sentence, 3-satellite refusal; take 390 px and 1200 px screenshots for PR #17; try on a real phone (touch).
- #9, #10: once the bridge (#3) and #14/#16 merge, run web/dev/step-geometry.html and web/dev/step-signal.html; check the bunched fix is clearly worse and where the signal peak is lost; tune config.
- Item 10 (relativity check): once solver.py and scenario.py merge, write scripts/check_relativity.py (same daily drift on all satellites, solve with and without clock) and report what it means for rung 4.
