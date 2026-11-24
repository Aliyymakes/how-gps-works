# Motion and feel research

Goal: make the page feel as fluid and reactive as Apple's UI. Everything here is analysed and rephrased, not copied. Numbers marked "(source)" were read on the page; numbers marked "(ours)" are my proposal, not from a source.

## What I could and could not fetch

Fetched and used:
- Emil Kowalski, "You don't need animations": https://emilkowal.ski/ui/you-dont-need-animations
- Emil Kowalski, "7 practical animation tips": https://emilkowal.ski/ui/7-practical-animation-tips
- Emil Kowalski, "Good vs great animations": https://emilkowal.ski/ui/good-vs-great-animations
- animations.dev, "The easing blueprint": https://animations.dev/learn/animation-theory/the-easing-blueprint
- Apple WWDC23 "Animate with springs": https://developer.apple.com/videos/play/wwdc2023/10158/
- Apple WWDC18 "Designing Fluid Interfaces": https://developer.apple.com/videos/play/wwdc2018/803/
- MDN prefers-reduced-motion (first 100k of 130k characters): https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion
- Josh Comeau, CSS `linear()` springs: https://www.joshwcomeau.com/animation/linear-timing-function/

Could NOT use:
- Apple HIG Motion page (https://developer.apple.com/design/human-interface-guidelines/motion): fetch returned only the title (page is script-rendered). I give no HIG quotes. The HIG themes (feedback, brevity, optional motion, Reduce Motion) below come from the WWDC talks and general knowledge, flagged as such.
- animations.dev/learn (root): returned only the domain name.
- apple.com product page (iphone-17-pro): returned markup only, no scripts or CSS, so I cannot say how its scroll effects are built. I make no claim about them.
- Linear "How we redesigned the Linear UI": fetched, but it says nothing about motion. Only usable for the "reduce visual noise / speed matters" attitude. Not cited below as a motion source.
- Stripe and Raycast: not fetched. No claims made.

## Source 1: Emil Kowalski (emilkowal.ski, animations.dev)

Quality he does best: restraint and speed. Animation is tuned to how often a thing is seen.

Patterns:
1. Frequency decides whether to animate at all. Things seen many times a day, or driven by keyboard, should skip animation because it reads as lag. Applies to us: the slider and drag are used constantly, so their feedback must be direct (no easing on the finger). Only the "Solve" result and section reveals are occasional enough to deserve visible motion.
2. UI motion under 300ms; a 180ms popup feels snappier than a 400ms one (source). Applies to us: tooltips, hover states, readout tint changes 120-200ms (ours). The solver glide is the one exception (see below) because it is the teaching moment, not chrome.
3. Ease-out for things entering/leaving or responding to the user; ease-in-out for things already on screen that move or morph (source: animations.dev). Built-in CSS curves are often too weak, so use custom ones (source). Applies to us: a distance line that moves to a new place is "already on screen", so it uses an in-out feel or a spring; a callout appearing uses ease-out.
4. Curves the source actually names: `cubic-bezier(0.19, 1, 0.22, 1)` (ease-out-expo style) and `cubic-bezier(0.32, 0.72, 0, 1)` (iOS sheet feel, used with 500ms) (source). Use as defaults in `:root` as `--ease-out` and `--ease-sheet`.
5. Press feedback: `scale(0.97)` on `:active`, about 150ms ease-out (source). Applies to us: the Solve button and the satellite handles.
6. Never animate from `scale(0)`; start at 0.9 or higher (source, example 0.93). Applies to us: when a satellite dot or label appears, fade plus scale from 0.93, not from nothing.
7. Origin-aware: scale from the trigger, not the centre (source). Applies to us: the info popover for a satellite grows from that satellite's position.
8. Tooltips: small delay first time, then none for neighbours (source). Applies to us: hovering satellite labels one after another should switch instantly.
9. Blur of about 2px during a crossfade hides imperfections (source). Applies to us: swapping the readout text between the "before" and "after" state if we cross-fade; optional.
10. Decorative mouse-driven effects can use spring smoothing, but functional displays (his example: a banking graph) may be better with none (source, good-vs-great). Applies to us, and this is the key caution: the position dot and readout are functional. They may glide, but only toward a value that is already computed (see rules at the end).
11. Test at slowed speed or frame by frame to find mismatches (source). Do this on our solve sequence.

Limits: these pages do not discuss springs, interruption or reduced motion. The tips are CSS-transition oriented.

## Source 2: Apple WWDC18 "Designing Fluid Interfaces"

Quality it does best: immediate, interruptible response, where the interface is a continuing conversation with the finger rather than a played clip.

Patterns (all from the talk's summary):
1. Respond with no waiting. Avoid timers that hold the interface; users notice small latency. Applies to us: slider and drag update the drawing on the same frame as `pointermove`. No debounce, no transition on the dragged thing itself.
2. Highlight on touch-down, confirm on touch-up, allow cancel by dragging away. Applies to us: Solve button and satellite handle show pressed state on `pointerdown`; solve fires on `pointerup`/click.
3. One-to-one tracking while the finger is down; rubber-band past limits instead of a hard stop. Applies to us: a dragged satellite below the horizon (elevation under mask) resists rather than snapping or vanishing; the slider thumb at its ends stretches a little.
4. Redirectable mid-motion. A new input must be able to take over a running animation. Applies to us: drag a satellite while the lines are still gliding; the lines retarget, they do not finish first.
5. Springs are described by damping ratio and response, not duration. Start at 100% damping (no overshoot); add bounce only when the gesture carried momentum (examples: tap = 100%, swipe-dismiss = 80%). Applies to us: lines/dot gliding after a drag release may have slight bounce; after a button press, none.
6. Momentum projection: pick the destination from position plus velocity, then spring there. The talk's talk-through formula is velocity/1000 times rate/(1-rate) with rate 0.998 (that code was reconstructed in the summary, not verbatim). Applies to us: if a satellite is flicked, project where it would coast and spring to the nearest valid sky position. Probably too much for the hackathon; mention only as a stretch.
7. About 10 points of movement before a drag starts, to separate tap from drag (source). Applies to us: a satellite handle needs a small slop before drag begins, so tapping to select does not nudge it.
8. Smoothness depends on what is in each frame, not only frame rate. Big per-frame jumps strobe. Applies to us: the solver steps must be interpolated (dot glides), not teleported.

## Source 3: Apple WWDC23 "Animate with springs"

Quality it does best: springs as the one motion type that stays continuous in position AND velocity.

Patterns:
1. Two knobs: `duration` (perceptual, predictable) and `bounce` (-1 to 1). Bounce 0 is the default and most versatile; about 0.15 is a small bounce; about 0.30 is noticeable; above about 0.4 is usually too much for UI (source).
2. Retargeting mid-flight uses the current velocity as the start velocity, so interruptions look smooth. Ease curves cannot carry an initial velocity, so a drag release with them lurches (source). Applies to us: this is the argument for a JS spring (not CSS transitions) on lines, dot and satellites.
3. Conversion given in the talk, mass = 1: stiffness = (2π / duration)^2; damping = 1 - 4π·bounce/duration for bounce >= 0. Implementation detail for us: I did not verify the damping term against Apple's code; treat as a starting point and tune by eye. Practical alternative: choose stiffness and damping directly (see Proposal).
4. Do not wait for a spring to fully settle before acting. Use the perceptual duration for "done" (source). Applies to us: the solver result must not wait for the glide to settle (ties to the rule below).

## Source 4: CSS `linear()` springs (Josh Comeau)

Quality: how to get spring-shaped motion in plain CSS.
1. `linear()` approximates a spring with many points; generate them with a tool rather than by hand (source).
2. Caveat: still time-based, and browsers shorten interrupted transitions, so a reversal mid-flight can feel abrupt compared with a JS spring that keeps velocity (source).
3. Needs a fallback; set it with `@supports (animation-timing-function: linear(0, 1))` (source). Support was about 88% as of Oct 2025 (source).
Applies to us: good for non-interactive pieces (a callout settling, button release). Not for anything the user can interrupt (lines, dots, satellites). Those need the JS spring.

## Source 5: MDN prefers-reduced-motion

Quality: accessible by default.
1. The setting exists because large scaling/panning can trigger discomfort in people with vestibular disorders (source).
2. Pattern: write the full motion as default, then override in `@media (prefers-reduced-motion: reduce)` later in source order. Reduced does not mean none: swap large movement for fades or colour changes (source).
3. JS side: `matchMedia('(prefers-reduced-motion: reduce)')` plus a `change` listener (general knowledge; the JS section of the page was in the truncated part and I did not read it).
Applies to us, concretely:
- Spring animations: if reduce, jump to the target in one frame (or a 100ms fade of the colour state). The result is identical, only the in-between is removed.
- Distance lines, dot glide, number count-up: all use the same `motion.enabled` flag, listened live.
- Keep non-motion feedback: the pressed colour, the residual readout, the state colour change. These carry the meaning, so they stay.
- Parallax, big scale-ins, and looping signal-wave animation: off or replaced by a static frame under reduce.

## Proposals for our ideas

Shared spring helper (ours, one tiny function, no dependency): per animated value keep `x`, `v`, `target`; each frame step `a = k*(target-x) - c*v; v += a*dt; x += v*dt`, with `dt` clamped to about 1/30 s. Retarget by changing `target` only; `v` carries over. Stop when `|x-target|` and `|v|` are tiny and snap to the target. Suggested starting values (ours, tune by eye): k = 170, c = 26 gives roughly critical damping (no overshoot) and settles in about 0.4-0.5 s; k = 170, c = 18 gives a slight bounce for post-drag release.

1. Drag satellites directly in the sky view.
   - The dragged satellite follows the pointer 1:1 with no easing (WWDC18). Use Pointer Events plus `setPointerCapture`, `touch-action: none` on the SVG so the page does not scroll, and about 6-10 px slop before drag starts.
   - On `pointerdown`: handle scales to about 1.08 and gets a ring (ours). On release: a spring settle, no more than a small bounce.
   - Feedback while dragging: DOP, elevation and the lines update on the same frame. The computed numbers use the true pointer position, never the animated one.
   - Add a visible grabbable cue (ring or cursor `grab`) so it is discoverable (WWDC18: hint with visual conventions).
   - Keyboard: arrow keys move the selected satellite with no animation (Emil: keyboard actions should not be animated).
2. Distance lines gliding to new places.
   - Each line endpoint is a spring value. While dragging the clock-error slider, set the lines directly (finger tracked 1:1). After release or after Solve, springs take over with no bounce (100% damping) because the action carries no gesture momentum.
   - Retarget on every new input; never queue.
3. Position dot easing toward each solver step.
   - Show each Gauss-Newton/least-squares step as a target; the dot springs there (about 250-350 ms per step, ours). This is the one place slower-than-300ms is justified since it is the explanation itself.
   - Do NOT delay computation: all steps are computed up front (or immediately); animation only draws them. Let the user skip or scrub to the end instantly; under reduced motion, show the final point plus a faint trail of the steps.
4. Readout counting smoothly to a new number.
   - Prefer a short tween (about 200-300 ms ease-out, ours) on the displayed value only, with the true value in the DOM text or `aria-label` right away so screen readers and tests see it immediately. Use `font-variant-numeric: tabular-nums` (JetBrains Mono already helps) so digits do not jitter.
   - While dragging, show the exact value with no count-up (it would lag the finger). Count only on discrete changes such as Solve.
   - Under reduced motion: no count, just replace.

## Durations and easings, starting table (ours, built from the sources above)

| Thing | Duration | Easing / spring |
|---|---|---|
| Press scale 0.97 | 150 ms | ease-out (source) |
| Hover, colour state | 120-180 ms | ease |
| Popover / callout in | 180-250 ms | ease-out-expo `cubic-bezier(0.19,1,0.22,1)` (source), from scale 0.93 |
| Section reveal | 400-500 ms | `cubic-bezier(0.32,0.72,0,1)` (source) |
| Lines / dot glide | spring | k 170, c 26 (critically damped) |
| Post-drag release | spring | k 170, c 18 (slight bounce) |
| Number tween | 200-300 ms | ease-out |
| Solver step | 250-350 ms per step | spring, no overshoot |

## Rules for this page (non-negotiable, from the brief)

1. Motion respects `prefers-reduced-motion` (CSS override plus one JS flag read live). Reduced means shorter and simpler, not broken.
2. Motion never delays the computed result. The model computes first; the drawing catches up. The true value is in the DOM at once. A skip control or a new input ends any animation instantly.
3. Under pointer drag, the dragged thing has no easing.
4. Animate `transform` and `opacity` where possible; in SVG, update attributes in one `requestAnimationFrame` loop shared by all springs (one loop, not one per element).
5. Colour is only for state; motion should not add colour either.

## Open questions

- Whether we use `linear()` for CSS-only pieces or keep everything in the JS spring (simpler, one pattern). I lean JS only, to match "reuse existing patterns" and avoid fallbacks.
- Apple's own site and the HIG motion page could not be read; if the owner wants citations from them, someone needs to open them in a browser and paste the text.
