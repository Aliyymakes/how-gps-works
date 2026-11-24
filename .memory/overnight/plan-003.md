# Plan 003: finish, go live, onboarding docs (written 2026-11-24 16:00 WIB)

Get the page onto main and live at a public link, then write onboarding documentation so every teammate can learn the whole codebase before the interview. Log to `.memory/overnight/state-003.md`. Before each item re-read this plan and `.memory/review/inbox.md` (orchestrator notes; never commit the inbox). Feature freeze is 25 Nov 18:59 WIB: items 1 to 4 must be merged before it.

## Models (Icarus's ladder)

The main session (Opus) plans, reviews and merges, and writes little itself.
- **Fable** subagent: the hardest calls only (a bug Opus and Sonnet both failed to fix; the docs' accuracy check in item 7). Icarus has asked for Fable by name for these.
- **Opus**: maths review, debugging page and Python together.
- **Sonnet**: code, tests, docs drafts.
- **Haiku**: running tests, done-list checks, link checks, small fixes.
The subagent that built something never checks it.

## Approved for this run (Icarus, 2026-11-24)

- Branches, issues, pull requests, comments, and merging under plan-002's rule (tests pass + separate reviewer passes + Opus reviewed any maths).
- Making the repo public and turning on GitHub Pages (item 4), after the scan in item 4 passes.
- Adding the MIT LICENSE (item 3).
- Not approved: editing design.md, his-words.md, directives.md, decision-map.md, start.md; new repo dependencies; changing docs/interface.md (propose changes in a PR description instead).
- Local web servers and browser tools were blocked by Claude Code's permission check last run. Do not retry them. The orchestrator chat runs browser checks on the live link and reports through the inbox and PR comments.

## The list

1. **Fix #40 and get the page onto main.** On branch `37-layers` (PR #38, which already contains the bridge, first screen and layer sections): when the page refuses to solve, the readout shows no metres value and no badge, and the map shows no solved dot. Prove it by reading the code path and by a small test if one fits. Merge #26, then update and merge #38. Close #17, #18, #19 as included in #38, and close issues #3, #5, #9, #10, #37, #40 with a one-line note.

2. **New default satellites.** In web/config.js set azimuths to 10, 100, 235, 325 (keep elevations between 15 and 65). Check in Python by replaying the page's call sequence: starts at 0 m with the clock trusted; 1 µs trusted gives a clearly non-zero error; solving gives 0 m and 1.00 µs; PDOP of the default set under 4; the four distance lines have four clearly different directions (no two within 20 degrees). Merge.

3. **LICENSE.** MIT licence text, copyright line: `Copyright (c) 2026 aliyymakes, tw-2866, scoobertfan, jstnstyad10`. Merge.

4. **Go public and live.** First scan the whole repo on main for secrets, tokens, personal emails or phone numbers, private paths and stray files; fix or list anything found and stop this item if something sensitive cannot be removed. Then `gh repo edit Aliyymakes/how-gps-works --visibility public --accept-visibility-change-consequences`, then turn on Pages from `main`, root folder (`gh api -X POST repos/Aliyymakes/how-gps-works/pages -f "source[branch]=main" -f "source[path]=/"`). Wait for the first Pages build, then check with curl that the live URL returns 200 for index.html, web/bridge.js and every mechanism file the bridge loads. Put the live link in README.md and docs/project-page.md. Merge. Write the link at the top of state-003.md.

5. **Finish the submission docs.** PR #15 (demo script): retime to about 2 minutes, using the real screen states. PR #20 (interview prep): fill the bridge and page answers from the now-merged code, fix what the last review failed. Merge both.

6. **Onboarding docs: `docs/onboarding/`.** Written for a new teammate who knows basic Python or basic JavaScript, not both. Every claim names the real file and function. Plain words, short sections, code quoted only a few lines at a time.
   - `README.md`: start here. What the project does in 5 lines, the reading order of the files below, and how to run it locally.
   - `architecture.md`: every folder and file with one line on its job; a diagram (Mermaid) of how the page, the bridge, Pyodide and the mechanism modules connect; what crosses the Python/JavaScript line and in what shape (from docs/interface.md).
   - `follow-one-click.md`: trace one drag of the clock slider from the browser event to the pixels: which JS function runs, what it sends to Python, which Python functions run in order, what comes back, how the map is drawn. Then the same for "Let the phone solve for its clock".
   - `code-tour.md`: each mechanism and web file in reading order, with its 3 to 6 key lines explained, and the one question a judge is most likely to ask about it.
   - `decisions.md`: the main choices as short records ("We chose X over Y because Z; the cost is W"): Python in the browser, a sphere Earth, the 2D ground map, solving for the clock, whole-chip code delays, the relativity result, no frameworks. Take them from .memory/decisions.md and design.md; add nothing new.
   - `glossary.md`: every term used on the page or in the code (pseudorange, clock bias, DOP, C/A code, chip, PRN, correlation, ENU, ECEF, Pyodide, and others found in the code), one or two plain sentences each.
   - `self-check.md`: 10 questions per area (solver, coordinates and map, geometry, signal, relativity, bridge and page) with answers in a collapsed `<details>` block, built from docs/interview-prep.md.
   Sonnet writes; an Opus subagent checks every file/function name and every explanation against the code on main; Haiku checks links and Mermaid syntax. Merge.

7. **Accuracy pass.** A Fable subagent reads docs/onboarding/, docs/interview-prep.md, docs/project-page.md and README.md against the code and docs/facts.md, as a sceptical judge would, and lists anything wrong, overstated or unexplained. Fix, merge.

8. **Keyboard and phone review by reading code.** Haiku runs docs/ui-guide.md section 4 against index.html and web/*.js (focus, labels, 44 px targets, reduced motion). Sonnet fixes clear failures. Merge before the freeze.

9. **Teammate hand-off.** One comment on each of #1, #2, #3, #4 and one in a new issue "Interview prep: read docs/onboarding" pointing each teammate to their reading order and their self-check section.

10. **Report.** `.memory/overnight/report-2026-11-24b.md`: live link, what was merged, verified / not verified, Questions for Icarus with a recommendation each, at-home list. PR and merge. Then stop.

Stop when the list is done or 10 hours after the paste. If time or usage runs short, items 1 to 4 and 6 come first.
