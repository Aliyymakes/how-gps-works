# Research note: what makes interactive explainers clear

Purpose: find patterns (ideas about teaching) that would fix our weak sections, signal and relativity.
This note describes ideas only. We copy no layout, drawing, wording or code from any source. Every
idea below must be redrawn and reworded by us for GPS.

## What I could and could not fetch

Fetched through a fetch tool that returns a summary written by a small model, not the raw page. So these are
second-hand descriptions, and I did not see the pages myself.

- Fetched: Ciechanowski's GPS article (https://ciechanow.ski/gps/) and his home page (https://ciechanow.ski/,
  which showed the "Moon" article, last 4.5k characters unread).
- Fetched: Red Blob Games home, "little things" (https://www.redblobgames.com/making-of/little-things/) and the A* introduction
  (https://www.redblobgames.com/pathfinding/a-star/introduction.html).
- Fetched: Nicky Case home (https://ncase.me/), "Parable of the Polygons" (https://ncase.me/polygons/), explorabl.es.
- Fetched: Distill "Why Momentum Really Works" (https://distill.pub/2017/momentum/) and
  "How to Use t-SNE Effectively" (https://distill.pub/2016/misread-tsne/).
- Fetched: Bret Victor's two essays (http://worrydream.com/ExplorableExplanations/,
  http://worrydream.com/LadderOfAbstraction/).
- NOT usable: "The Evolution of Trust" (https://ncase.me/trust/) returned only a title and toggles, so I say nothing
  about how it works. Nicky Case's home page states no design principles.
- Not fetched: the Red Blob "making-of" tutorials beyond "little things", other Ciechanowski articles.
- Nothing was run or tested on our page; the section problems come from the brief (user testing said signal and
  relativity were not understood).

## 1. Bartosz Ciechanowski

Home: https://ciechanow.ski/

### What his GPS article does (description only)
The article builds GPS in layers: positioning from known landmarks, then timing of signals, then the clock
problem, then a move from 2D to 3D, then orbits, then GPS specifics (relativity, atmosphere), then the signal
itself (carrier, data bits, spreading codes, correlation). Each section ends by naming the problem the next one solves.
It uses many small widgets, one per idea. It shows a user clock beside a system clock with a bias control, uses
two bars to exaggerate the relativity effect, and uses sliding-code plots for correlation. Math appears late,
after the intuition.

### We must NOT reuse its structure or visuals
Our page covers the same topics (clock bias, relativity, C/A code correlation), so the risk of lookalike work is
high. Do not copy its section order, its two-clock bias widget, its paired relativity bars, its sliding-replica
correlation plots, or its landmark/rope/tape metaphors. If a design of ours looks like one of those, change it.

Our own alternatives:
- Use our map and satellite lines as the one running scene. Every section changes that scene and does not open a new toy.
- For the signal, use a different picture of "matching": a lock-and-key or a sound-in-a-crowd picture of our own, not sliding plots.
- For relativity, show the *effect on the position* (the map pin drifts) and not two clock bars.

### Patterns worth taking (as ideas)
1. **One idea per widget, and each section ends with the problem the next solves.**
   Apply to: signal. Our signal section probably explains C/A codes and noise in one go. End geometry with
   "but how does the phone measure that time at all?", and open signal with that question only.
2. **Disclose simplifications and exaggeration out loud** (his Moon article says when sizes or heights are scaled up).
   Apply to: relativity. The real drift is tiny. A visible note "drawn 1000x too big so you can see it" stops
   people thinking the effect is huge, and builds trust.
3. **Show the same situation from more than one viewpoint** (space view, ground view).
   Apply to: signal. Show the phone's view (a messy mix of sounds) beside a view that picks out one satellite.
4. **Turn the flaw into the tool.** His clock-bias section frames the error as a shared offset that an extra
   measurement removes. Teach the idea in plain words before any control.
   Apply to: relativity, where the story "solving for the clock hides it" is the hardest to grasp. Lead with the plain
   claim: "every line is wrong by the same amount, so one extra unknown absorbs it."
5. **Brief, late maths, explained in words.** Apply to: all sections. Hide equations behind an optional "show the maths" fold.

## 2. Red Blob Games (Amit Patel)

Home: https://www.redblobgames.com/ . Making-of pages: https://www.redblobgames.com/making-of/little-things/

Patterns:
1. **Diagrams start in a useful state that teaches without any clicking.**
   Apply to: signal. Open with the noise slider already at a value where the match peak is visible and one
   caption says "this peak is satellite 12". Do not start on an empty or flat plot.
2. **Colour the text to match the diagram, and colour each slider like the thing it controls.**
   Apply to: relativity. Give satellite clock drift one colour, used for its words, its slider and its arrows on the map.
   Keep saturated colour for what matters; use few colours at once (he admits his own pathfinding page used too many).
3. **Same data, several views, with stepping.** His A* page steps one tile at a time and shows the same search in different views.
   Apply to: signal. Add a "step" button that tries one time shift of the code at a time and records the match score on a small chart.
4. **Text tells the reader exactly what to try** ("drag the goal until the search stops").
   Apply to: every section. Add one imperative line per widget: "Drag the noise slider to the right and watch for when the peak sinks."
5. **Handle details**: keep the grab offset, large invisible hit areas, controls below the diagram, red for invalid states.
   Apply to: first screen. Our slider and solve button should work on a phone with a thumb, and a bad state (too few satellites) should say so.

## 3. Nicky Case (explorables)

Home: https://ncase.me/ ; hub: https://explorabl.es/ ; example: https://ncase.me/polygons/

Note: the home page states no principles; the explorable hub says play and learning should go together.
"The Evolution of Trust" could not be read.

Patterns (from "Parable of the Polygons"):
1. **Play first, explain after the surprise.** Readers drag things, then see the result, then the lesson is named.
   Apply to: relativity. Let the user press "let the satellite clocks run for a day" and watch the pin walk away
   before any text explains. Then say what it was.
2. **A single named takeaway sentence after the surprise.**
   Apply to: relativity: one plain line such as "A tiny clock error becomes a long position error."
3. **Pose a "what if" and let the next control answer it.**
   Apply to: signal. "What if the noise were as loud as the signal?" then the slider moves there on a button press.
4. **Scenario buttons: set the model to a start state.** He starts from a pre-built world to test a claim.
   Apply to: geometry. Buttons "all satellites overhead" and "satellites spread around" jump to a known layout, so users do not hunt for bad geometry.
5. **Finish with a challenge or sandbox and a short recap of lessons.**
   Apply to: the end of the page: a challenge such as "get the position error under 10 m using only 5 satellites", then three recap lines.

## 4. Distill.pub

Pieces: https://distill.pub/2017/momentum/ and https://distill.pub/2016/misread-tsne/

Patterns:
1. **Prose points at the figure and says what to look for.** Same idea as Red Blob but in sentences with figure names.
   Apply to: signal. Name each plot ("Figure A: what the phone hears") and refer to it.
2. **Show several views of one run** (error plot, state plot, phase plot).
   Apply to: relativity. One slider should move three things together: the satellite clock readout, the line length on the map, and the pin error.
3. **Small multiples: many settings side by side at once.** The t-SNE piece shows one dataset at several settings so one setting does not mislead.
   Apply to: signal. Show a row of three small plots at low, medium and high noise, so users see the trend without dragging.
4. **Known test data so readers can judge a result against truth.**
   Apply to: first screen and geometry. Always draw the true position as a faint marker so the solved position can be compared.
5. **Explicit warnings about likely misreadings** next to the figure.
   Apply to: relativity. Add "This does not mean GPS is inaccurate: the phone removes it by solving for the clock."
   Also: a note that a high peak in the signal plot is not a bigger satellite but a better match.

## 5. Bret Victor, "Explorable Explanations"

Link: http://worrydream.com/ExplorableExplanations/

Patterns:
1. **Reactive document: change an assumption and see the claim change.** In his 2024 note he stresses that the point is
   letting readers test the author's claim, not only play.
   Apply to: relativity. Our claim is "solving for the clock hides the drift." Give a toggle "solve for clock: on/off"
   and let the user see the claim hold or fail. That is a test, not a demo.
2. **Explorable examples reveal behaviour the author did not mention.** Keep controls loose enough to try odd values.
   Apply to: geometry. Let users drag satellites anywhere, not along fixed presets.
3. **Several representations of one system help intuition.**
   Apply to: signal. Show the code as a bar pattern and as a wave, linked, so one edit shows in both.
4. **Contextual information in place.**
   Apply to: all sections. Hover or tap a term like "pseudorange" or "chip" to get a one-line definition without leaving the page.

## 6. Bret Victor, "Up and Down the Ladder of Abstraction"

Link: http://worrydream.com/LadderOfAbstraction/

Patterns:
1. **Take control of the key variable, including time.** Skim, pause, jump, compare.
   Apply to: relativity. Give a time scrubber (hour 0 to 24) for the drift, not a looping animation, so users can pause on a moment.
2. **Step up: show all values at once.** Draw the whole path over time, not one instant.
   Apply to: relativity. Draw a trail of where the pin would be at every hour, then click a point to step down to that single moment.
3. **Step down: pick one case to see why.**
   Apply to: signal. Show the match score for every time shift as one curve (up), then click a point to see the two code
   patterns lined up at that shift (down).
4. **Insight lives in the movement between levels,** so make the two views linked, with a marker on both.
   Apply to: geometry. A plot of DOP over all positions, linked to the map layout at the clicked point.
5. **Stay grounded.** Return to concrete cases to catch surprises.
   Apply to: every section end: a "see it on the map" button that returns to the main scene.

## Strongest patterns for us (short list)

1. Play first, then name the lesson (Case). Fixes relativity: let the pin drift, then explain.
2. Make the claim testable: a "solve for clock" on/off toggle (Victor). Relativity.
3. Step up and step down: whole curve of scores, click to see one shift (Victor). Signal.
4. Start every diagram in a state that already teaches, plus one "try this" line (Red Blob). All sections.
5. Small multiples of noise levels shown at once (Distill). Signal.
6. Misreading warnings beside figures (Distill). Both weak sections.
7. Say what is exaggerated (Ciechanowski, idea only). Relativity.
8. One colour per concept, shared by text, slider and map (Red Blob). All sections.
9. Scenario buttons that set a known state (Case). Geometry.
10. Hide the maths until asked (Ciechanowski, Victor). All sections.

## Reminder on originality
Use these as ideas only. Our drawings, captions and widget designs must be our own. For GPS specifically, avoid
Ciechanowski's structure and visuals as described above. Quotes in this note are none; all points are paraphrased.
