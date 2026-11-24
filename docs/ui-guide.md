# UI guide

Rules for every goal that builds or changes the page (`index.html`, `web/`). Agents read this before writing any page code. Written 2026-11-23 from the sources at the bottom.

The page has one job: a judge who has never seen it, with nobody from the team there, understands the main idea within two minutes. Every rule below serves that.

## 1. Layout: guide, don't dump

An interactive widget alone is not an explanation. The page leads the user's attention to one thing at a time.

1. **Open with a question, not a title screen.** The first thing on screen is a question the user cares about, for example "How does your phone know where you are?", and something they can touch right away.
2. **Start concrete.** The first interaction is hands-on: switch a satellite off, drag the clock-error slider, watch the dot move. Explanations come after the user has felt the effect, not before.
3. **One idea per step.** Each step of the depth ladder (design.md 2a) is its own section with one control that matters and one result to watch. Hide or grey out controls that are not part of this step.
4. **Link steps with "but" and "therefore".** Each step ends on a twist that makes the next step necessary. "With 3 satellites it works, BUT the phone's clock is cheap. THEREFORE we need a fourth." No unconnected facts.
5. **Let them go too far.** Let the user push a control until it breaks (too much clock error, too few satellites, too much noise), show the failure clearly, then show what fixes it.
6. **Words are short and sit next to what they describe.** One or two sentences per step, placed beside the control or the result, never a paragraph above the whole page.
7. **Numbers carry units and meaning.** "Position off by 300 m" beats "error: 300". Put the number where the eye already is.
8. **End with a sandbox.** The last section has every control unlocked so the user can explore their own questions.
9. **Depth is opt-in.** The two-minute path works without opening anything extra. Extra explanation sits behind a clearly labelled "how does this work?" control.
10. **First paint within 1 second.** Pyodide takes seconds to load. The question, the layout and a loading line show immediately; the controls switch on when Python is ready. Never a blank screen.

## 2. Look: the Instrument system

Icarus chose his Instrument system for this project (2026-11-23). The files are `web/theme.css` and `web/theme.js`; `web/theme-preview.html` shows every component. Use its variables and classes as they are; do not invent new colours, fonts or radii. If something is missing, add it to theme.css through its own issue. The theme is a first draft: colours are approved (2026-11-23), other values may change.

What the system holds, as Icarus described it:
- Dark first, with a light theme.
- Instrument Sans for text, JetBrains Mono for numbers and code.
- Interactive elements are white. Colour is reserved for state only: ok, warn, bad.
- Corner radii are derived from `--r-card` (nested corners stay concentric).
- Pointer-tracked light through `--px` / `--py`.

For the GPS page this means: satellites, signal lines and the solved position use white and greys; ok/warn/bad colours appear only for how good the fix is (for example green within a few metres, amber off by tens, red off by hundreds). The exact thresholds are placeholders in the page's config file.

## 3. Motion: lively, never slow

Motion explains what changed. It must never make the user wait.

**Should it animate?**

| How often the user does it | Decision |
|---|---|
| Constantly (dragging a slider) | The result updates instantly, every frame. No easing on the value itself |
| Often (toggling a satellite) | Short transition, 150 to 250 ms |
| Occasionally (opening a "how does this work?" panel) | Standard animation, 200 to 500 ms |
| Once (first load, reaching the final sandbox) | A little delight is allowed |

Keyboard actions are never animated.

**Durations**

| Element | Duration |
|---|---|
| Button press feedback | 100 to 160 ms |
| Tooltips, small popovers | 125 to 200 ms |
| Dropdowns, selects | 150 to 250 ms |
| Panels, drawers | 200 to 500 ms |
| Explanatory motion (the solver stepping toward the answer) | Can be longer, and the user can skip or replay it |

Everyday UI stays under 300 ms.

**Easing**
- Entering or leaving: `cubic-bezier(0.23, 1, 0.32, 1)` (strong ease-out).
- Moving across the screen: `cubic-bezier(0.77, 0, 0.175, 1)` (ease-in-out).
- Hover and colour changes: `ease`.
- Constant motion (a signal travelling, a loading bar): `linear`.
- Never `ease-in` on UI. It starts slow and feels sluggish.
- Springs only for drag with momentum: duration 0.5 s, bounce 0.2. Keep bounce between 0.1 and 0.3.

**Rules**
- Animate only `transform` and `opacity`. Never animate `width`, `height`, `top`, `left`, `margin` or `padding`.
- Use CSS transitions, not keyframes, for anything the user can trigger again mid-animation, so it retargets instead of restarting.
- `prefers-reduced-motion`: keep opacity and colour changes and anything that aids understanding; remove movement.
- Drawing (canvas or SVG) runs on `requestAnimationFrame`. A Python call never blocks a frame: if a call takes over 16 ms, show the last result until the new one arrives.

## 4. Friendly by default

- Every control works with mouse, touch and keyboard, and has a visible focus ring.
- Touch targets are at least 44 by 44 px. Test on a phone-width screen (390 px): judges may open the link on a phone.
- Every control has a text label. Sliders show their current value with units.
- A "reset" control returns each step to its starting state.
- Errors from Python are shown as one plain sentence near the control that caused them, never as a raw stack trace.

## 5. Review before the pull request

Before opening a web pull request, the agent reviews its changed files against Vercel's Web Interface Guidelines. Fetch the current rules from:

https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md

Fix what applies to the changed files. Write anything left unfixed under "Not verified" in the pull request. Then list in the pull request which rules of sections 1 to 4 the change was checked against.

## Sources

- Bret Victor, "Explorable Explanations": https://worrydream.com/ExplorableExplanations/
- Nicky Case, "How I make an explorable explanation": https://blog.ncase.me/how-i-make-an-explorable-explanation/
- Emil Kowalski, animation standards: https://github.com/emilkowalski/skills (skills/review-animations/STANDARDS.md)
- Vercel, Web Interface Guidelines: https://github.com/vercel-labs/web-interface-guidelines
- Icarus's Instrument system (his own; files to be added by him)

## 6. Every action answers (Icarus, 2026-11-24)

No silent actions. A user must never press, drag or type something and see nothing happen without knowing why.

- Every control gives visible feedback within 100 ms of being used, even if the real result takes longer (a pressed state, a "working" line, the value updating).
- When something cannot happen, the page says why, in one plain sentence next to the control the user just used, and what to do instead. Example: "Can't solve: four things are unknown and only three satellites are on. Turn one back on."
- A disabled control always explains itself: a visible line near it saying why it is off and what turns it on (not only a tooltip, which phones do not show).
- Loading, failure and empty states each have their own words. If Python fails to load, the page says so and what to try (reload, another browser), and nothing pretends to work.
- Messages are announced to screen readers (`aria-live="polite"`).
- Every message is short, specific to what just happened, and goes away or changes when the situation changes. A message never contradicts what is on screen.
