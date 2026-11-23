# design.md: the spec

Source of truth. Work that disagrees with this file is wrong until Icarus changes it. Sections are numbered and dated. A later section that overrides an earlier one says so in both places.

Fixed words:
- **Placeholder** = a number to tune in testing. It lives in one config file per area, never inline.
- **TBA** = Icarus decides later. Do not invent; leave a clearly named placeholder.
- **Proposed** = suggested, not confirmed. Use it, but it can change.

## 1. The challenge (2026-11-22, from the organisers' brief)

Theme: Unveiling Technology. Pick a technology people use daily without knowing how it works, find the mechanism inside it, and build a working interactive version that runs in a web browser. One idea, taken as far as possible.

What the brief requires:
1. Judges open the live link first, with nobody from the team present. Everything a user needs is in the project itself.
2. Interactive: the user changes something and the project responds. No videos, slideshows or pages of text as the project.
3. Runs in a current web browser at a public link. No sign-in, download or API key. Online until judging ends.
4. A first-time user understands the main idea within two minutes. Extra depth beyond that is welcome.
5. Outputs are computed by our code from the user's inputs. Simulations must really compute. No pre-recorded animations or prepared results.
6. The mechanism runs in our own code. Hosted AI may be used elsewhere, not for the part being explained.
7. Work started 19 November. Open-source components and AI tools are allowed under the Terms. The team must be able to explain all of its own code, and why it chose any component it did not write.
8. Submissions close 25 November 23:59 AoE (26 November 18:59 WIB). Submit: live link, public repository, project page, short demo video.
9. A fairness page sets out how AI use, authorship and each round are assessed. Nobody on the team has reported reading it yet (see section 6).

Judging looks above all at: a first-time user quickly understands the idea; the work underneath is correct and goes deep; the team can explain and defend it in its own words.

Not allowed as a topic: how phone calls compress voice (the organisers' reference project).

## 2. The idea (2026-11-22, Icarus)

GPS: how your phone knows where you are. Icarus picked "GPS: real satellites above the user + your own position solver" on 2026-11-22 (his-words.md).

Known limit, checked 2026-11-22: a web page cannot read how many satellites the phone is really using. The browser location API returns only latitude, longitude, accuracy, altitude, altitude accuracy, heading and speed. So the page computes which GPS satellites are above the user from public orbit data, and says clearly that this is computed, not read from the phone's chip.

Section 2a overrides this section on where the real-satellites view sits. What the user changes on the first screen and how it is shown is TBA. See section 6.

## 2a. Depth ladder (proposed by the orchestrator 2026-11-22 16:04; confirmed by Icarus 2026-11-23 08:01, "looks right")

One idea throughout: the phone finds its position by measuring time. Build in this order and cut from the bottom if time runs short.

1. Two-minute idea: distance is signal travel time, the phone's clock is wrong, and a fourth satellite solves for the clock error. One microsecond of error is about 300 m.
2. Geometry: the same satellites and the same error give a far worse fix when the satellites are bunched together in the sky.
3. How the time is measured: the signal arrives weaker than the background noise, and the phone finds it by sliding a known code along it until it lines up. The user adds noise and watches the match peak hold, then fail.
4. Relativity: satellite clocks run fast (about 38 microseconds a day, from memory, unverified). Turn the correction off and watch the position drift.
5. Reflections off buildings.

This section overrides section 2 on one point: the "real satellites above the user" view is a late extra, built only after rung 5, or cut (confirmed by Icarus 2026-11-23). Reason: predicting orbits is hard to explain in the interview and a library for it is code the team did not write.

Every number shown on the page is verified against a source before it ships.

## 3. How it is built (2026-11-22)

- The mechanism is written in Python and runs in the user's browser through Pyodide (Icarus, 2026-11-22). Reason: two of the four teammates code only in Python, and they own the mechanism.
- The page is HTML, CSS and JavaScript. It draws, takes input, calls the Python functions and shows what they return.
- docs/interface.md is the contract between the two sides.
- Hosting: Proposed GitHub Pages, served from the repo root of `main`. Nobody has turned this on yet.

Folders:
- `mechanism/` Python mechanism. `tests/` its tests.
- `index.html` and `web/` the page.
- `docs/interface.md` the contract.
- `.memory/` team memory. `.github/` issue and pull request templates, test workflow.

## 4. How the team works (2026-11-22, Icarus)

Goals, bugs and progress are tracked with GitHub Issues and a Projects board (Icarus, 2026-11-22). The repo is Aliyymakes/how-gps-works. The loop is in CONTRIBUTING.md.

Roster (Icarus, 2026-11-23):

| GitHub | Agent | Can code | Area |
|---|---|---|---|
| aliyymakes (Icarus) | Claude Code | JavaScript, HTML, Python | Page; spec, reviews, final calls |
| jstnstyad10 | Codex | JavaScript | Page |
| tw-2866 | Codex | Python | Mechanism |
| scoobertfan | Claude Code | Python | Mechanism |

The Area column is Proposed by the orchestrator from the skills; Icarus can change it.

Division: senior (Icarus, 2026-11-22).

## 5. What gets submitted

Live link, public repository, project page, short demo video. Who makes the project page and the video: TBA.

## 5a. The fairness page (2026-11-22, read by the orchestrator from gvhackathon.com/fairness through a page summary; Icarus has not read it himself yet)

- AI tools are allowed for building. The page asks for no log or disclosure of AI use.
- The team must understand and be able to explain its own work. Disqualifying: plagiarism, work the team cannot account for, pre-built or off-theme projects, outside help in the interview, anything but a genuine live recording.
- Round 2 is a recorded team interview: all four on camera together, one continuous take, up to 10 minutes of answers in a 40-minute window, one attempt. Questions are written from our submission and source code. It opens about 30 minutes after we submit and must be started within 24 hours.
- Round 3 (finalists) is a live interview with the judges.
- AI reads the submission text and source code to prepare notes and interview questions for the judges. People do the scoring.
- The public repository needs an open-source licence that we choose.
- Signed parent or guardian consent for every member is uploaded by the supervising teacher before submission.

## 6. Still open

Each line is detailed in decision-map.md.
- Project name: TBA.
- What the user changes on the first screen and how the sky and the position are drawn: TBA.
- Look of the page (colours, fonts, style): TBA. Ask Icarus; do not choose.
- When the repo turns public (it is `how-gps-works`, private for now; Icarus 2026-11-22): TBA. It must be public by submission.
- The name on the MIT licence's copyright line: TBA. (Licence is MIT, Icarus 2026-11-22. Consent forms: done for all four, Icarus 2026-11-22.)
- When all four are free together for the Round 2 interview: TBA.
- Where satellite orbit data comes from and how positions are computed: TBA (technical, orchestrator recommends).
