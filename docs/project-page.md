# [Project name TBA]

Draft for Icarus. Wording not approved.

Live link: https://aliyymakes.github.io/how-gps-works/

## What it is

An interactive web page that shows how a phone works out where it is from GPS satellite signals. Everything you see is computed in your browser, by the team's own code, from the settings you change.

The one idea: the phone finds its position by measuring time. A signal travels at the speed of light, so a travel time is a distance. The satellites are about 20,200 km up (20,189 km above our sphere model).

## How it works, one rung at a time

**Rung 1, the first screen.** The page opens with a small drawing of a signal travelling from a satellite to a phone ("travel time × speed of light = distance", "one distance = one line on the map"), a line that says what you are looking at ("a map of the ground around the phone. Each line is one satellite's distance to you. Where the lines meet is where your phone thinks you are."), a key for the map, and three hints that walk you through it. On a phone the map and its result stay at the top of the screen while you use the controls. It starts with four satellites and a good fix. A small ground map shows one "distance line" per satellite: the places on the ground that are the measured distance from that satellite. You make the phone's clock wrong with a slider. The phone still trusts its clock, so the lines pull apart and the solved position moves. The readout always shows the position error the solver computes, not a fixed figure, because the error depends on where the satellites are. Then you press a button and the phone solves for its clock as well. The lines meet again and the page says how fast or slow the clock was. A switch per satellite lets you turn one off. With too few satellites on, the page refuses and says why (four unknowns, east, north, up and the clock, but only as many measurements as satellites that are on) and still draws the lines of the satellites that are on. It needs four satellites with the clock solved and three with the clock trusted. The readout shows metres in one format: 520.3 m appears as "520 m" (one decimal only under 100 m). A clock error of one microsecond makes each measured distance about 300 m too long (a derived figure: one microsecond times the speed of light).

**Rung 2, geometry.** The same measurement errors give a much worse fix when the satellites are bunched together in the sky. The page shows the dilution of precision (DOP) the mechanism computes: how much the layout multiplies measurement errors, and the position error that results.

**Rung 3, the C/A code.** Each satellite sends a known pattern of 1023 chips that repeats every 1 millisecond (the C/A code). The page shows 40 steps of it in three rows: what the satellite sends, what the phone hears (the same pattern a little later, with noise added) and the phone's own copy. You slide the copy by hand until it lines up with what the phone hears. A "Match score" shows how well it fits, and how far you slid is the delay (14 chips here). Then "Let the phone try every shift" makes the phone do the same search at all 1023 shifts, and two charts show the scores. You add noise and watch the best match hold, then fail. The page shows the real delay, the phone's best match and how many times bigger the best score is than the runner-up. The score and the best match come from the mechanism's `signal.correlate`. The page only works out, for each step, whether the copy and the heard value are on the same side of zero, and uses that to light the step or dim it.

**Rung 4, satellite clock drift.** One slider, "Time since the satellite clocks were last corrected" (0 to 24 hours, starting at 24), adds the same drift to every satellite (about 38 microseconds a day if uncorrected, about 11 km of range). The first card shows two clocks as digits, one on the ground and one on a satellite, and how far ahead the satellite clock is. The second card shows the ground map twice, each 40 km wide. "The phone trusts its clock": the position goes wrong, about 20 km off after 24 hours with our four satellites (19,767 m; more than the range error, because the layout multiplies it; most of it is height, which a flat map cannot show). "The phone solves for its clock": the position error stays 0 m, because a shared drift looks exactly like the phone's own clock error. In this section the phone's own clock error is set to 0, so at 0 hours both read 0 m.

**Rung 5, reflections off buildings.** Not built.

## What is simplified

- The Earth is a sphere with one radius (about 6371 km). The real Earth is slightly flattened. Reason: the conversions are a few lines the team can explain, and the simulated truth and the solver use the same model, so the solver recovers the simulated position to far below a millimetre. This is agreement with our own sphere model, not real-world accuracy. The README says so; the page itself does not yet.
- The ground map is a flat square about 2 km wide, centred on the true position. Reason: at that size the curved distance lines look almost straight, and a flat map is simple to draw.
- In the signal step the delay is a whole number of chips, 0 to 1022, and the page's real delay is 14 chips so it fits in the 40 steps shown. Reason: it keeps the code-sliding demonstration simple. One chip is about 293 m of travel.
- The noise in the signal step is random noise added by our Python (`mechanism/signal.py`). It is not a recording of a real receiver.
- The satellites are placed at example positions in the sky, not read from real orbit data. The browser cannot read which satellites a phone is really using, so the page does not claim to.

## Components we did not write

- **Pyodide** (Python in the browser; numpy loads together with it). Two of the four teammates code only in Python and own the mechanism, so the mechanism is Python and runs in the user's browser. The page, in JavaScript, only draws and calls it.
- **numpy.** Approved by Icarus for the mechanism's array maths.
- **jsDelivr.** The CDN (<https://www.jsdelivr.com/>) that serves Pyodide 314.0.8 to the page, from cdn.jsdelivr.net.
- **Google Fonts.** The page's theme fonts load from Google Fonts.
- **Hosting.** GitHub Pages, served from the repository's main branch.

## How AI was used

Team to fill in.

## The team

| GitHub | Area |
|---|---|
| aliyymakes (Icarus) | Page; spec, reviews, final calls |
| jstnstyad10 | Page |
| tw-2866 | Mechanism |
| scoobertfan | Mechanism |

The Area column is proposed and can change.

## Sources

Every GPS fact on the page and in this text is listed with its source in [docs/facts.md](facts.md). Figures our code computes (such as 520 m and 19,767 m) are not in that file; they come from running the code with the page's settings.
