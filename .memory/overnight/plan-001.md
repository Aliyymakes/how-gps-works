# Plan 001: away run for aliyymakes (written 2026-11-23 15:40 WIB)

Icarus is away. Work through the items below in order, as far as you get, then stop. Everything here can be done without the other three teammates. Log every item to `.memory/overnight/state-001.md` (what you did, branch, pull request link, verified / not verified). Re-read this plan before each item.

## How to run it cheaply

You (Opus) plan, review and integrate. You do not write long code yourself. For each item, hand the work to a subagent with only the context it needs:
- **Sonnet** subagent: writing code, tests, research with sources, drafting documents.
- **Haiku** subagent: running tests, checking a pull request against its "Done when" list, checking files against docs/ui-guide.md, formatting, small fixes.
- **Opus** (you): reviewing maths in mechanism code, deciding when a subagent's result is wrong, and any bug a Sonnet subagent failed to fix twice.
Give each subagent the item text, the exact files to read and touch, and the done checks. Never pass this whole plan. The subagent that built something never grades it: a separate Haiku or Sonnet subagent checks it.

## Rules for this run

- Follow .memory/start.md. Away rules in directives.md apply: technical calls marked `provisional` in decisions.md, taste calls (wording on the page, layout choices the spec does not settle) listed as Questions for Icarus with a recommendation.
- Each item: create its GitHub issue if it has none (`gh issue create`, labels `goal` and its area, assign `@me`), branch from up-to-date `origin/main` named `<issue>-<short-name>`, open a pull request (draft if anything is waiting on teammates). Never merge. Never push to main.
- Approved for this run: creating issues, branches, pull requests and issue comments in Aliyymakes/how-gps-works; web searches for facts. Not approved: merging, making the repo public, GitHub Pages, adding a LICENSE, new dependencies beyond numpy and Pyodide, editing design.md, his-words.md, directives.md, decision-map.md, start.md or docs/interface.md.
- Never touch the teammates' files: mechanism/solver.py, mechanism/coords.py, mechanism/scenario.py, mechanism/mapview.py, web/bridge.js, web/bridge-test.html, and their tests. You may read them on `origin/main` if they have merged.
- Every number shown on the page or in a document needs a source listed in docs/facts.md (item 2).
- If a check needs something you do not have (a phone, a person), add it to the at-home list at the end of state-001.md and move on. Do not loop.
- If usage runs low, stop at a clean point and write where to resume in state-001.md.
- Stop when the list is done or 10 hours after the paste, whichever comes first.

## The list

1. **First screen (the existing "Goal: first screen" issue).** Find it with `gh issue list`. Claim it, comment the split: "aliyymakes builds the whole first screen; jstnstyad10 reviews." Build everything the issue allows before its dependencies merge: index.html, web/config.js, web/first-screen.js, layout, styling with web/theme.css, the map SVG, controls, states and wording, all written against docs/interface.md and calling `callPython`. Do not write a stand-in for bridge.js and do not fake results. Run `git fetch` and check `origin/main`: wire in any mechanism function that has merged. Open a draft pull request listing what still waits. Sonnet builds, Haiku checks it against docs/ui-guide.md, you review.

2. **Fact sheet (docs/facts.md, new).** Every number the page and the documents will use, each with a source link and the exact value from that source: speed of light, GPS orbit radius and period, number of satellites in the constellation, C/A code length and chip rate, received signal power at the ground and the thermal noise level (so the page can say "below the noise"), the relativistic clock offsets (special, general, net per day), the range error that offset equals per day. Prefer official sources (gps.gov, the IS-GPS-200 interface spec, NIST) over blogs. Mark anything you could not confirm as `unconfirmed`. Sonnet researches, a second Sonnet subagent re-checks every number against its link.

3. **Rung 2 maths (mechanism/geometry.py, tests/test_geometry.py).** `dop` exactly as docs/interface.md says. Method in words: build a table with one row per satellite (the direction to it, plus a 1 for the clock), and DOP comes from the inverse of that table times itself. Tests with hand-built satellites (do not import coords.py): 4 well-spread satellites give PDOP under 3; 4 satellites bunched within 10 degrees of each other give PDOP over 10; fewer than 4 return an error dict; outputs survive `json.dumps`. Then comment on the bridge issue: "Please also load geometry.py." Sonnet writes, you review the maths.

4. **Rung 3 maths (mechanism/signal.py, tests/test_signal.py).** The three functions in docs/interface.md. `ca_code` must follow the shift-register method and tap table in IS-GPS-200; test it against the first 10 chips the spec lists for at least PRN 1, 2 and 3 (look them up, do not use memory). Other tests: every code has 1023 values of +1 or -1; with noise 0 `correlate` finds the exact delay for 5 different delays; with noise_std 3 it still finds it (seed fixed); with very high noise it fails and `peak_to_next` drops near 1; correlating PRN 1 against PRN 2's code gives no clear peak. Sonnet writes, you review.

5. **Rung 2 page section (web/step-geometry.js).** A self-contained section the first screen can drop in later: a "bunch the satellites" control, the DOP number, and the computed position error (from scenario and solver when merged). Works by itself on web/dev/step-geometry.html. Only uses functions in docs/interface.md. Same draft rule as item 1. Sonnet builds, Haiku checks against the ui-guide.

6. **Rung 3 page section (web/step-signal.js).** A noise slider, the received signal drawn as a line, the 1023 correlation scores drawn underneath with the peak marked, and a plain sentence when the peak is lost. web/dev/step-signal.html to try it. Same rules as item 5.

7. **Project page draft (docs/project-page.md).** What the project is, the one idea, how each rung works in plain words, what is simplified (sphere Earth, the 2D ground map, whole-chip delays), the components the team did not write (Pyodide, numpy, Google Fonts) and why each was chosen, and the team. Numbers only from docs/facts.md. Mark wording as a draft for Icarus. Sonnet.

8. **Demo video script (docs/demo-script.md).** A shot list for a short screen recording that shows the first screen's two-minute idea first, then rungs 2 and 3. Do not choose a length; leave it as a question for Icarus. Sonnet, short.

9. **Interview prep (docs/interview-prep.md).** Questions a judge would ask from this code, with short plain answers, grouped: the solver loop, the bridge, coordinates and the map lines, DOP, the C/A code and correlation, the simplifications, why Python in the browser, what AI tools did and did not do. For files not merged yet, write the questions and leave the answers to be filled in. Every teammate must be able to answer every section. Sonnet.

10. **Relativity check, only if mechanism/solver.py and mechanism/scenario.py are merged on origin/main.** A small script (scripts/check_relativity.py) that adds the same daily clock drift to all satellites and compares the solved position with and without clock solving. Write the result and what it means for rung 4 into the pull request. If they are not merged, add it to the at-home list and skip.

11. **Final check.** A Haiku subagent confirms: every pull request from this run passes its own done list, `.memory/` updates landed (decisions, gotchas, overview, commands, INDEX.md if files were added), and no forbidden file was touched (`git diff --name-only origin/main...<branch>` for each branch). Write the report to `.memory/overnight/report-2026-11-23.md`: what was done with links, what was verified and what was not, Questions for Icarus (each with a recommendation), the at-home list. Then stop.
