# [Project name TBA]

Draft for Icarus. Wording not approved.

## What it is

An interactive web page that shows how a phone works out where it is from GPS satellite signals. Everything you see is computed in your browser, by the team's own code, from the settings you change.

The one idea: the phone finds its position by measuring time. A signal travels at the speed of light, so a travel time is a distance. The satellites are about 20,200 km up.

## How it works, one rung at a time

**Rung 1, the first screen.** The page starts with four satellites and a good fix. A small ground map shows one "distance line" per satellite: the places on the ground that are the measured distance from that satellite. You make the phone's clock wrong with a slider. The phone still trusts its clock, so the lines pull apart and the solved position moves. The readout always shows the position error the solver computes, not a fixed figure, because the error depends on where the satellites are. Then you press a button and the phone solves for its clock as well. The lines meet again and the page says how fast or slow the clock was. A switch per satellite lets you turn one off. With only three satellites and the clock unknown, the page refuses and says why: four unknowns (east, north, up, clock) and three measurements. A clock error of one microsecond makes each measured distance about 300 m too long (a derived figure: one microsecond times the speed of light).

**Rung 2, geometry.** The same satellites and the same clock error give a much worse fix when the satellites are bunched together in the sky. The page shows the dilution of precision (DOP) values from the mechanism: how much the layout multiplies measurement errors. The page shows the values.

**Rung 3, the C/A code.** Each satellite sends a known pattern of 1023 chips that repeats every 1 millisecond (the C/A code). The signal arrives below the background noise. The phone slides its own copy of the code along the received signal and scores the match at every shift. You add noise and watch the match peak hold, then fail. The page shows the scores and the peak.

**Rung 4, relativity.** Planned. It is being tested first, because a drift shared by all satellites may be absorbed by the clock solve and show no position drift. If so, the page will show the range error and say why the solver hides it.

**Rung 5, reflections off buildings.** Planned.

## What is simplified

- The Earth is a sphere with one radius (about 6371 km). The real Earth is slightly flattened. Reason: the conversions are a few lines the team can explain, and the simulated truth and the solver use the same model, so results stay exact. The page says this is a simplification.
- The ground map is a flat square about 2 km wide, centred on the true position. Reason: at that size the curved distance lines look almost straight, and a flat map is simple to draw.
- In the signal step the delay is a whole number of chips, 0 to 1022. Reason: it keeps the code-sliding demonstration simple. One chip is about 293 m of travel.
- The noise in the signal step is random noise added by the page's code. It is not a recording of a real receiver.
- The satellites in the demo are placed by the user's settings, not read from real orbit data. The browser cannot read which satellites a phone is really using, so the page does not claim to.

## Components we did not write

- **Pyodide** (Python in the browser). Two of the four teammates code only in Python and own the mechanism, so the mechanism is Python and runs in the user's browser. The page, in JavaScript, only draws and calls it.
- **numpy.** Approved by Icarus for the mechanism's array maths.
- **Google Fonts.** The page's theme fonts load from Google Fonts.
- **Hosting.** Proposed: GitHub Pages, served from the repository. TBA.

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

Every number on the page and in this text is listed with its source in [docs/facts.md](facts.md).
