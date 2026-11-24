# Plan 004: perfect the UI/UX and document every line (written 2026-11-24 17:00 WIB)

Icarus: "perfect the imperfect". Two outcomes, both required:
1. The page is as clear, responsive and forgiving as it can be. Above all: **no silent actions**. If something does not work, the page tells the user why (docs/ui-guide.md section 6).
2. Documentation that explains **every line of code** so that someone who has never programmed can follow it.

Log to `.memory/overnight/state-004.md`. Before each item re-read this plan and `.memory/review/inbox.md` (orchestrator notes; never commit the inbox).

## Models

The main session runs on **Fable**. Icarus asked for it by name and removed limits on model, effort and length for this run.
- Fable (you, or a Fable subagent): the UX audit judgement, every design decision, the final review of docs and page.
- Opus subagent: maths review, page-and-Python debugging, checking that docs match code exactly.
- Sonnet subagent: implementing fixes, writing doc drafts, tests.
- Haiku subagent: running tests and checklists, and acting as the "least experienced reader" in item 10.
The subagent that built something never checks it.

## Approved for this run (Icarus, 2026-11-24)

- Branches, issues, pull requests, comments, and merging under the usual rule (tests pass + separate reviewer passes + maths reviewed by Opus).
- Playwright (Chromium and WebKit) as a **dev-only** test tool: add it to requirements-dev.txt, keep browser UI tests in `tests/ui/`, and keep the normal CI fast (UI tests may run in a separate optional workflow). Running a local web server for testing.
- Not approved: editing design.md, his-words.md, directives.md, decision-map.md, start.md; changing the Instrument look (colours, fonts) beyond fixing contrast failures; changing docs/interface.md without listing the change in the PR as a proposal; anything that turns the page into a video or removes interactivity.
- Taste calls (new wording, layout changes, new animations): build them as drafts, merge if they pass every check, and list each one in the report with before/after screenshots so Icarus can veto it.
- Feature freeze 25 Nov 18:59 WIB: every change to the page must be merged before then. Documentation (items 8 to 11) can continue after it, until 26 Nov 12:00 WIB.

## Browser access

Icarus installed Playwright in a virtual environment in the repo: use `.venv/bin/python` (for example `.venv/bin/python -m pytest tests/ui`), never the system Python, and never commit `.venv/`.

Last runs could not start a local server or a browser (Claude Code's permission check). First, try once: `python3 -m http.server 8000` in the background and a Playwright screenshot of http://localhost:8000. If it is refused, do not retry: test against the live site https://aliyymakes.github.io/how-gps-works/ instead (a branch's changes are then checked after merge), and if browsers are refused entirely, write it in state-004.md and rely on the orchestrator's browser checks through the inbox.

## The list

1. **UX audit (Fable).** Use the live page as a first-time judge would, at 390 px and 1200 px, by mouse, touch emulation and keyboard only, in Chromium and WebKit, on a throttled slow network, and with Pyodide blocked (offline). Try every control in every state, including silly inputs (all satellites off, rapid repeated clicks, slider at both ends, Reset mid-calculation, resizing the window). For each moment write: what the user did, what they expected, what happened, the gap, severity (blocks understanding / confuses / polish). Write `docs/ux-audit.md` with screenshots in `docs/ux-audit/`. Merge.

2. **No silent actions.** Fix every "blocks understanding" and "confuses" finding about feedback first: each control answers within 100 ms; every refusal and every disabled control says why and what to do; loading, failure and offline states have their own words; messages use `aria-live`; no message contradicts the screen. Add a Playwright test per rule in `tests/ui/` (for example: every button press changes something visible or shows a message within 1 s; switching off a satellite with the clock solved shows the reason and no badge). Merge.

3. **The first two minutes.** Make the opening path impossible to miss: one obvious first action, a gentle hint that disappears once used, the "but/therefore" thread between steps, and the moment the lines snap together made unmistakable (motion per ui-guide section 3, respecting reduced motion). Time a fresh first visit: the main idea must be reachable in under 2 minutes without reading anything long. Merge.

4. **Every layer, same standard.** Repeat items 2 and 3 for the geometry, signal and relativity sections: what to touch first, what to watch, why it matters, clear feedback at every extreme. Merge.

5. **Robustness and speed.** Pyodide load failure and slow loads (progress words, a retry button that explains itself); no calculation ever freezes the page (if any interaction takes over 100 ms, measure and fix, for example by moving Python into a Web Worker); no console errors; works in Chromium and WebKit at 390 px and 1200 px. Record the numbers in gotchas.md. Merge.

6. **Accessibility.** Keyboard order and focus, labels on every control, contrast measured (fix failures within the Instrument palette and list them), screen reader announcements, reduced motion, 44 px targets, nothing that relies on colour alone. Merge.

7. **Visual polish.** Spacing, alignment, hierarchy and motion against docs/ui-guide.md and web/theme.css. Small, careful changes; before/after screenshots for each. Merge. **Items 1 to 7 must be merged by 25 Nov 18:59 WIB.**

8. **Line-by-line documentation: `docs/annotated/`.** Write after the page is final.
   - `how-to-read-code.md`: a primer for someone who has never programmed: what a file, a function, a variable, a list, a dict/object, an `if`, a loop, an import, a return value are, with tiny Python and JavaScript examples side by side; how to read the annotated files.
   - One file per source file: every file in `mechanism/`, every file in `web/` (theme.css may group rules by purpose), and `index.html`. Each file quotes the code in order, a line or a few lines at a time, and explains **every line**: what it does in plain words, why it is there, and what would break without it. Maths lines also get the idea behind them with a small worked example using real numbers. No line skipped, nothing assumed.
   - Every annotated file starts with: what this file is for, which files it talks to, and a 3-line summary.
   Sonnet drafts each file; an Opus subagent checks each explanation against the code; Fable reviews the whole set for clarity.

9. **Keep the docs true: a test.** `tests/test_annotations.py`: for every annotated file, (a) every quoted code line appears in the named source file, and (b) every non-blank line of the source file is quoted somewhere in its annotation (coverage). It runs in normal CI, so the docs cannot silently fall behind the code. Merge items 8 and 9 together.

10. **The least-experienced-reader test.** A Haiku subagent gets only `docs/annotated/` and `docs/onboarding/`, no code. Ask it 5 questions per source file about specific lines ("what does line N of solver.py do and why"). Every wrong or vague answer means the docs failed: improve that part and ask again until it passes. Record the questions and results in `docs/annotated/reader-test.md`.

11. **Update everything else.** docs/onboarding/, docs/interview-prep.md, docs/project-page.md, docs/demo-script.md and README.md reflect the final page; links to docs/annotated/ added where they help. A Fable accuracy pass reads them all as a sceptical judge. Merge.

12. **Final review and report.** Fable re-runs the item 1 audit on the live site: every finding closed or explained. Write `.memory/overnight/report-2026-11-24c.md`: what changed with before/after screenshots, the taste calls for Icarus to keep or veto, verified / not verified, Questions for Icarus with a recommendation each, the at-home list. PR and merge. Then stop.

Stop when the list is done. If usage runs low, stop at a clean point and write where to resume.
