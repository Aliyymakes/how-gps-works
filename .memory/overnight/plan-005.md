# Plan 005: the UI overhaul (written 2026-11-24 21:20 WIB)

Plan-004 finished before it picked up Icarus's overhaul requests, which were left as inbox notes. This plan carries them out. The notes are copied in full in the appendix below and are part of this plan.

Log to `.memory/overnight/state-005.md`. Before each item re-read this plan and `.memory/review/inbox.md`; act on any note dated after 2026-11-24 21:20.

## Deadlines
- Before/after screenshots ready for Icarus: as soon as possible, at the latest **25 Nov 10:00 WIB**. Write "UI REDESIGN READY FOR ICARUS: PR #<n>" at the top of state-005.md.
- The approved redesign merges by **25 Nov 18:59 WIB** (feature freeze). If Icarus has not answered by 16:00, merge only the changes that fix the two sections that failed user testing (signal and relativity) and the phone layout, and leave the rest of the branch unmerged.

## Models and speed (same rules as plan-004)
Main session: Opus, medium effort, lean (subagents read files, the main session reads summaries). Fable: design lead for the redesign (Icarus asked for it by name): writes docs/ui-redesign.md, reviews every built improvement with screenshots, builds the hardest pieces itself. Sonnet: research notes, implementation, doc updates. Haiku: tests, checklists, the screenshot-only reader test. Run independent work in parallel worktrees.

## Approved for this run
Branches, issues, PRs, comments; Playwright via `.venv` (and the page.route() method from state-004, since a local server is refused); merging under the usual rule **after Icarus approves the screenshots** (or the 16:00 fallback above). Not approved: editing design.md, his-words.md, directives.md, decision-map.md, start.md; changing interface.md without listing it in the PR; copying layouts, drawings, wording or code from any site.

## The list
1. Research (appendix 19:40 B and 19:45). Sonnet subagents in parallel, notes in docs/ui-research/.
2. Fable writes docs/ui-redesign.md (appendix 19:40 C), with the user-testing items (appendix 20:00) and the per-section labels and illustrations (appendix 20:05) ranked first, then the 19:30 fixes, then report-2026-11-24c questions 1 (phones: map and controls never on screen together; a compact sticky map on phones is in scope now) and 5 (phone step-1 hint below the fold).
3. Build on branch `ui-redesign`, one improvement at a time, Fable reviewing each with screenshots at 390 and 1200 px in Chromium and WebKit. Every tests/ui test passes; add tests for new behaviour. The annotation test will fail for changed web files: update docs/annotated/ for every changed line in the same branch (Sonnet), and re-run the reader test for those files.
4. Screenshot-only reader test per section (appendix 20:00, last line). Redo any section a Haiku reader cannot explain from its screenshot.
5. Open the PR with a before/after pair (desktop and phone) for every improvement. Then the approval gate.
6. Credit jsDelivr (the Pyodide CDN) in README and the project page (report question 4). Can merge separately, now.
7. Load speed experiment, on a separate branch, not merged without Icarus: host the Pyodide files on GitHub Pages instead of jsDelivr and compare cold loads (10 visits each, Chromium and WebKit). Report the numbers and the repo size cost.
8. After merge: update docs/onboarding, interview prep, project page and demo script for the new page; Opus accuracy pass; merge.
9. Report: `.memory/overnight/report-2026-11-25.md`. Then stop.

## Appendix: the inbox notes (verbatim)

## 2026-11-24 19:30 WIB (orchestrator UI review of the live site, after #69)
Page changes; all must merge before 25 Nov 18:59 WIB. Do these after the current docs item, one small PR, before/after screenshots for each:
1. Phone (390 px): the first action is below the fold. On first load the screen shows the title, intro and map, and the "Make the phone's clock wrong" slider is a scroll away. Make the first action visible without scrolling on a 390x844 screen (for example a compact map height on phones, or the slider card above the map on narrow screens). Highest priority.
2. Uneven empty space inside cards on desktop: the clock slider card has a tall empty band under the slider; the "Step 2" box has empty space under its button; the right column of the signal section has an extra outer card so its top does not line up with the left card. Tighten to the theme's spacing scale; tops of side-by-side cards align.
3. Text hierarchy: the but/therefore bridge paragraphs between sections are larger than the section headings' subtitles and compete with the headings. Make bridges read as quieter connective text, headings as the strongest element of each section.
4. Between the geometry and signal sections there are two bridge paragraphs in a row saying nearly the same thing ("...next: how does the phone measure it at all?" and "Good geometry only helps if..."). Keep one.
5. Signal section: the received-signal barcode is too dense to read at 1200 px and 390 px, and the dashed "where the signal really is" line is hidden under the solid line when they match. Make the true-delay marker visible even when it coincides (for example a small label or a marker above the plot), and consider showing a zoomed window around the peak.
6. Relativity section starts at 0 h with every number 0 m, so the point is invisible until the user drags. Consider a hint that tells the user to drag, or a starting value that already shows the effect (taste: list for Icarus).
Items 3 to 6 change wording or layout: build them as drafts and list them in the report for Icarus to veto.

## 2026-11-24 19:40 WIB (orchestrator): UI OVERHAUL, Icarus's request. Highest priority after the step you are on.
Icarus: "tell it to reaserch about good ui and let fable make it 100x better". This replaces the six fixes in the 19:30 note (fold them in).

A. Order change: pause annotating web/ and index.html (they will change). Python annotations, the coverage test and the primer continue.

B. Research (Sonnet subagents, in parallel, each writes notes with links to docs/ui-research/<topic>.md):
   - The best interactive explainers and what they do well: Bartosz Ciechanowski's articles (including his GPS article), Red Blob Games, Nicky Case's explorables, Distill.pub, Bret Victor's "Explorable Explanations" and "Up and Down the Ladder of Abstraction".
   - Motion and feel: Emil Kowalski's animation standards, Apple's Human Interface Guidelines on feedback and motion.
   - Layout and hierarchy: Refactoring UI principles, Laws of UX, Vercel Web Interface Guidelines.
   For each source: the patterns that would make OUR page clearer, with one concrete example each. Analyse, never copy: no layouts, drawings, wording or code taken from any of them (plagiarism disqualifies the entry). Do not reuse Ciechanowski's GPS article's structure or visuals; note what it does and do something of our own.

C. Fable is the design lead (Fable subagent; Icarus asked for it by name):
   1. Read the research, the live page, docs/ux-audit.md and the 19:30 note. Write docs/ui-redesign.md: the target experience in one paragraph, the 10 to 15 biggest improvements ranked by how much they help a first-time judge understand in two minutes, and for each: what changes, why, and how we will know it worked.
   2. Keep: the depth ladder and its order, every computed result, no silent actions (ui-guide 6), dark-first, colour only for state, Instrument Sans + JetBrains Mono. Anything that changes the look beyond that is a proposal.
   3. Implementation: Sonnet subagents implement each improvement on branch `ui-redesign` (one worktree), Fable reviews each one with screenshots at 390 and 1200 px before the next starts, and may implement the hardest pieces itself.
   4. Every Playwright test in tests/ui must still pass; add tests for new behaviour.

D. Approval gate. Do NOT merge ui-redesign until Icarus approves. Open it as a PR with a before/after screenshot pair for every improvement (desktop and phone) by 25 Nov 10:00 WIB at the latest, earlier if ready, and write "UI REDESIGN READY FOR ICARUS: PR #<n>" at the top of state-004.md. The orchestrator relays it to him. Keep the live site on main unchanged until then. Freeze still applies: the approved redesign must merge by 25 Nov 18:59 WIB.

E. After the redesign merges: annotate web/ and index.html, then items 10 to 12 as planned.

## 2026-11-24 19:45 WIB (orchestrator): the target feel for the UI overhaul (adds to the 19:40 note)
Icarus: "a combination of how good Vercel's UI is, how fluid and reactive Apple's UI is, and the best things from all good examples it can find."
Add to the research (B):
- Vercel: vercel.com, the Geist design system (typography, spacing, greys, components) and the Web Interface Guidelines. What makes it feel precise: restraint, tight type scale, exact alignment, crisp borders, quiet greys, fast and subtle hover/press states.
- Apple: Human Interface Guidelines (motion, feedback, materials), apple.com product pages, and Emil Kowalski's animation standards. What makes it feel fluid: everything reacts to the finger immediately, spring motion that can be interrupted mid-way, direct manipulation (drag the thing itself, not a remote control), continuous rather than stepped changes.
- Plus any other example the research finds that does one of these better (for example Linear, Stripe, Raycast), noting exactly which quality.
Fable's docs/ui-redesign.md must name, for each improvement, which of these qualities it brings and from where. Ideas worth testing for our page: dragging satellites directly in the sky view; distance lines that glide (spring) to their new place instead of jumping; the dot easing toward each solver step so the user watches the solve converge; the readout counting smoothly to the new number; a precise Geist-like type and spacing scale. All motion must respect reduced motion and never delay the computed result.
Same rules as before: analyse and learn, never copy layouts, drawings, wording or code; colour only for state; before/after screenshots for Icarus before merging.

## 2026-11-24 20:00 WIB (orchestrator): USER TESTING RESULT, top of the redesign list
Icarus showed the page to several people. Two sections failed: nobody understood them until he explained.

1. Signal section, "What the phone hears": the 1023-chip barcode reads as "a glitchy texture block". Nobody sees a signal in it.
   Direction for Fable (proposal, screenshots for Icarus):
   - Show a readable window, not all 1023 chips: about 30 to 40 chips drawn as a clean square wave (up/down steps) big enough to see each step.
   - Three stacked rows with plain labels: "What the satellite sends" (the pattern), "What the phone hears" (the same pattern, later and noisier), "The phone's own copy" (clean).
   - Direct manipulation: the user drags the phone's copy left and right. Where the copy agrees with what is heard, those chips light up; where it disagrees, they dim. A live score (agreements minus disagreements) rises and falls under the finger. When it lines up, the score jumps and the match lights up: the user finds the delay by hand before the page finds it automatically.
   - Then "let the phone search every shift": the score graph builds from shift 0 to 1022 in about a second (reduced motion: instantly), and the peak appears. Mark the true delay so it is visible even when it coincides with the found one.
   - Noise slider: what is heard gets fuzzy while the copy stays clean, so the user sees why the peak survives and then sinks.
   - The right-hand card currently has a big empty top area; fix with the rest.

2. Relativity section: people did not get it. It tries to say two things at once (satellite clocks drift, and the solve hides a shared drift) with a table of numbers.
   Direction for Fable (proposal, screenshots for Icarus): split it into two small steps, one picture each.
   a. "Satellite clocks run fast." Two clocks side by side, one on the ground and one on a satellite, running live; a "time in orbit" control (hours to days). The gap grows in microseconds, and under it the same gap as distance ("every distance is now wrong by N km"). A small breakdown of why: weaker gravity up there makes the clock run faster, its speed makes it run slower, the net is faster. Every number from docs/facts.md; if facts.md lacks the gravity and speed parts, research them from official sources and add them there first.
   b. "So why doesn't your position drift?" Two small maps side by side for the same drift: "phone trusts its clock" (the dot runs away kilometres) and "phone solves for its clock" (the dot stays). One sentence: every satellite is off by the same amount, which looks exactly like the phone's own clock being wrong, and the fourth satellite already fixes that.
   c. Only if a reliable source confirms it (add to facts.md first): one sentence that real GPS satellites have their clocks set to tick slightly slower before launch to cancel this. If not confirmed, leave it out.
   Note: the effect is mostly general relativity (gravity), partly special relativity (speed). The page should not call it "special relativity" alone.

Both go first in the redesign order. Test each with the least-experienced-reader idea: a Haiku subagent sees only screenshots and the on-page words and must explain what the section shows; if it cannot, the section is not done.

## 2026-11-24 20:05 WIB (orchestrator): every section says what it shows, with an illustration
Icarus: "just make what each part is illustrating clearer, and maybe add an illustration to depict it". Applies to EVERY section (first screen, geometry, signal, relativity), part of the redesign:
- Each section opens with a one-line "What you're looking at" label in plain words above the interactive picture (for example: "Each line is one satellite's distance to you. Where the lines meet is where your phone thinks you are.").
- Each section gets a small explanatory illustration next to or above the interactive part, showing the idea in its simplest form before the user touches anything:
  - First screen: a satellite, a signal travelling to a phone, and "travel time x speed of light = distance"; then one distance becomes one line.
  - Geometry: two tiny skies side by side, satellites spread vs bunched, with the zone of uncertainty small vs large.
  - Signal: the pattern, the same pattern arriving late, the phone sliding its copy until they line up.
  - Relativity: a ground clock and a satellite clock, the satellite one ahead.
- Illustrations are drawn by our own code as simple SVG in the Instrument style (white lines on dark, colour only for state), labelled in plain words, never images from the web, never copied from other sites. They may animate gently once (reduced motion: still).
- Test: a Haiku subagent sees only the screenshot of a section and must say what it shows. If it cannot, redo the label or the illustration.
