# Demo video script

**Draft for Icarus.** Shot list for the short screen recording the brief asks us to submit (design.md section 1). About 2 minutes: 2:05 in total. Order follows the depth ladder (2a): the first screen's two-minute idea, then rung 2, then rung 3. Rung 4 (satellite clock drift) is on the page but not in this script; the issue names rungs 2 and 3 only.

Rules for this file:
- Every button label and on-screen sentence in quotes is copied word for word from `index.html`, `web/first-screen.js`, `web/step-geometry.js` or `web/step-signal.js`.
- The voice-over lines are drafts, not page text.
- Numbers on screen: 520.3 m and 0 m on the first screen were computed by replaying the Python with the default satellites (`web/config.js`) and the clock at 1.00 µs. The other numbers the page shows (DOP, position error in rung 2, scores and peak size in rung 3) are computed live and were not read from a run, so they are not quoted: the voice-over points at the readouts instead.
- The timing is read from the code. It has not been recorded or timed in a browser.

## Shot list

| # | Time | Shot | What is on screen | What the user does | Voice-over (draft) |
|---|------|------|-------------------|--------------------|--------------------|
| 1 | 0:00 to 0:10 | Load | Title "How does your phone know where you are?". "Loading the maths…" disappears, then the ground map shows four distance lines meeting at the dot. Readout "Position off by" shows 0 m, badge "Good fix", note "The distance lines meet at the dot." | Nothing. Let it sit | "Your phone finds where it is by timing signals from satellites." |
| 2 | 0:10 to 0:25 | Wrong clock | The highlighted slider "Make the phone's clock wrong", value "0.00 µs" | Drags the slider slowly to "1.00 µs" | "The phone's clock is cheap, and a small time error becomes a long distance error." |
| 3 | 0:25 to 0:40 | Lines pull apart | The distance lines no longer meet. "Position off by" shows 520.3 m, badge "Fix is far off", note "The phone trusts its clock, so the distance lines miss each other." | Holds still | "The lines no longer meet. The readout says how far off the position is." |
| 4 | 0:40 to 0:55 | Solve the clock | Button "Let the phone solve for its clock". Afterwards the lines meet again, "Position off by" shows 0 m, badge "Good fix", sentence "The phone found its clock is 1.00 µs fast." | Presses the button, then holds | "Now the phone treats its own clock as unknown and solves for it too. The lines meet again, and the page says how wrong the clock was." |
| 5 | 0:55 to 1:10 | Take one away | The "Satellites" switches. After the switch the readout shows "–" and the page says "Four things are unknown (east, north, up and the clock), but three satellites give only three measurements." | With the clock still solved, switches "Satellite 4" off, holds, then presses "Reset" | "Take one satellite away and it refuses: four unknowns, only three measurements." |
| 6 | 1:10 to 1:30 | Rung 2: bunch them | Scrolls to the sentence "Solving for the clock works, but only if the satellites are spread across the sky. Therefore where they sit matters as much as how many there are." Then the heading "Does it matter where the satellites are?", the sky diagram, the slider "Bunch the satellites" ("0 % bunched"), "DOP" and "Position off by" | Drags "Bunch the satellites" to "100 % bunched", holds, then drags it back to "0 % bunched" | "Same clock error, same noise, only the layout changes. Bunched together, the fix gets worse. DOP says how much the layout multiplies the error." |
| 7 | 1:30 to 1:50 | Rung 3: clean signal | Scrolls to the heading "How does the phone measure the time?". Top graph "What the phone hears", bottom graph "How well the code matches at each shift". Slider "Add noise" shows "No noise". "Best delay found" and "Real delay" both show 300 chips, badge "Found", sentence "The match stands out clearly from everything else." | Holds on the peak in the bottom graph | "The signal is a known pattern of 1023 chips. The phone slides its own copy along what it hears and scores the match at every shift. The peak is the timing." |
| 8 | 1:50 to 2:05 | Add noise | Same graphs. The slider text changes to "Noise is N× the signal" and the sentence under the readout changes with it | Drags "Add noise" slowly to the right end ("Noise is 12.0× the signal"), pausing where the sentence changes | "Add noise. The peak still shows when the noise is bigger than the signal, until it is lost." |

## What the page does at shot 8 (from `web/step-signal.js`)

The sentence and the badge change by level: "Found", "Barely found", "Lost". The sentences are "The noise is bigger than the signal, yet the match still finds it.", "The match still points to the right place, but only just." and "The phone can no longer find where the signal starts." With the page's settings (PRN 7, real delay 300 chips, seed 1), a Python replay of `signal.make_received` and `signal.correlate` gives "Barely found" first at "Noise is 6.5× the signal" and "Lost" first at "Noise is 10.0× the signal", so "Lost" does show before the slider's end (12.0×). Pause at about 6.5× and at 10.0×. Not yet seen in a browser.

## Questions for Icarus

1. **Total length.** This draft runs 2:05. The spec gives no length; the brief only says "short". Shots 1 to 5 are the part every judge must understand: cut from the end (shots 7 and 8) if the limit is tight.
2. **Who records and narrates.** The spec leaves this TBA. Recommendation: one teammate records and talks, so the voice is steady and that person can explain the page in the interview.
3. **Voice-over or on-screen captions.** Recommendation: spoken voice-over, with the page's own sentences visible on screen.
4. **Rung 4 in the video.** Left out to stay near two minutes. Say if you want a short extra shot on the table "Drift over time".
