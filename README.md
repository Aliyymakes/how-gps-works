# [Project name TBA]

An interactive web page that shows how a phone works out where it is from GPS satellite signals, using code that runs in your browser.

## How to try it

- Live link: https://aliyymakes.github.io/how-gps-works/
- Locally, from the repository root: `python3 -m http.server 8000`, then open <http://localhost:8000/>. The page needs an internet connection to load Pyodide (see below).

## How it works

- A phone finds its position by measuring time. A signal travels at the speed of light, so a travel time is a distance. The satellites are about 20,200 km up (20,189 km above our sphere model).
- The page starts with four satellites and a good fix. A small ground map draws one distance line per satellite. You make the phone's clock wrong, and the lines pull apart. About 1 microsecond of clock error is about 300 m of distance error.
- The solver (`mechanism/solver.py`) then solves for the clock as well as the position, and the lines meet again. With only three satellites and the clock to solve, it refuses and says why: four unknowns (east, north, up, clock) need four measurements.
- Satellites bunched together in the sky give a worse fix than spread-out ones. `mechanism/geometry.py` computes the dilution of precision (DOP) that shows this.
- Each satellite sends a known pattern of 1023 chips that repeats every 1 millisecond (the C/A code). `mechanism/signal.py` slides a copy of the code along a noisy signal and scores the match, so you can watch the peak hold and then fail as you add noise.
- Satellite clock drift: A table adds the same drift to every satellite (about 38 microseconds a day if uncorrected, about 11 km of range) and shows that the position error stays 0 m once the phone solves for its clock: a shared drift looks exactly like the phone's own clock error.

Every GPS number on the page is computed by the team's own Python in `mechanism/` (with numpy); the JavaScript only draws, blends slider positions and takes one length. The numbers come from the settings you change. No results are prepared in advance.

## What is simplified

- The Earth is a sphere with one radius, about 6371 km. The real Earth is slightly flattened.
- The ground map is a flat square centred on the true position, not a curved surface.
- In the signal step the delay is a whole number of chips. One chip is about 293 m of travel.
- The noise in the signal step is random noise added by our code. It is not a recording of a real receiver.
- The satellites are at example positions in the sky, not read from real orbit data. The page does not claim to show which satellites a real phone is using.

## Components we did not write

- **Pyodide** runs Python in the browser. Two teammates code only in Python and own the mechanism, so the mechanism stays Python and the page (JavaScript) only draws it and calls it.
- **numpy** does the array maths in the mechanism.
- **Google Fonts** supplies the page's fonts.
- Hosting: GitHub Pages, served from the main branch.

## The team

| GitHub | Area |
|---|---|
| aliyymakes (Icarus) | Page; spec, reviews, final calls |
| jstnstyad10 | Page |
| tw-2866 | Mechanism |
| scoobertfan | Mechanism |

Every number above is listed with its source in [docs/facts.md](docs/facts.md). How the team works: [CONTRIBUTING.md](CONTRIBUTING.md). Instructions for AI agents: [AGENTS.md](AGENTS.md).
