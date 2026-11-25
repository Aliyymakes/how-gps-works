# config.js, line by line

Source: `web/config.js`

## What this file is for
This file is a list of settings. It holds the numbers the first screen and the relativity section share: where the phone is, where the four satellites are, how big the map is, and how far the sliders go. It contains no calculations. Keeping every number in one place means the team can change one number here and the page follows.

## Which files it talks to
- [`web/first-screen.js`](first-screen.js.md): imports everything here (`import * as config from "./config.js"`) to place the phone and satellites, size the map and set the clock slider.
- [`web/step-relativity.js`](step-relativity.js.md): imports it too, for the receiver, the satellites, the error colour limits, the hours slider and the phone clock error.
- `docs/interface.md`: defines what the mechanism expects for a receiver and a satellite (`lat_deg`, `lon_deg`, `azimuth_deg`, `elevation_deg`). The names below match it.
- [`mechanism/mapview.py`](../mechanism/mapview.py.md) (see [mapview.py](../mechanism/mapview.py.md)): receives `mapHalfWidthM` and `lineSamples` when the page asks it for distance lines.
- It uses no other file and nothing from outside.

## In three lines
1. `receiver` says where the phone really is (Jakarta), and `satellites` lists four satellites by compass direction and height in the sky.
2. The map and the clock slider each have a size or range here.
3. The colour limits and the relativity section settings are here too. All are marked placeholder, provisional: they stay until Icarus confirms them.

New to code? See [how to read code](../how-to-read-code.md).

## The code, line by line

```js
// Every placeholder number for the first screen lives here (design.md 2b).
// All of these are provisional until Icarus confirms them.
```
Two comments (lines starting with `//` are notes for people; the computer skips them). They say that every placeholder number lives in this file and that none is final. Without them nothing breaks.

```js
// Where the phone really is. Jakarta.
```
A comment: the next line is the phone's true position, in Jakarta.

```js
export const receiver = { lat_deg: -6.2, lon_deg: 106.8 }; // placeholder, provisional
```
`const receiver` makes a named, unchangeable value. `export` lets other files import it. The curly brackets make an object: labelled values. `lat_deg: -6.2` is the latitude in degrees (how far north or south of the equator; the minus sign means south), and `lon_deg: 106.8` is the longitude in degrees (how far east of the zero line through Greenwich). The text after `//` is a comment. Where it is used: `buildScene` in [`web/first-screen.js`](first-screen.js.md) passes these two numbers to `coords.latlon_to_xyz` (a Python function) to get the phone's position in space, and [`web/step-relativity.js`](step-relativity.js.md) does the same when it sets up its section. Without this line the page would not know where the phone is, and the other files would fail when they ask for `config.receiver`.

```js
// Four satellites spread around the sky. Elevation stays between 15 and 65 degrees.
// Chosen so no two distance lines are parallel and PDOP stays under 4 (decisions.md, #43).
```
Two comments. Elevation is the height of a satellite above the horizon (0 is on the horizon, 90 is straight up). A distance line is the map line of places that are the same measured distance from one satellite. If two of those lines are parallel they never cross, so the position would be unclear. PDOP is a number that says how much the layout of the satellites magnifies errors; smaller is better. `decisions.md` is the project's record of choices. Nothing breaks without the comments.

```js
export const satellites = [ // placeholder, provisional
```
Starts a list (square brackets) called `satellites` and shares it with other files. The comment says the values are provisional. Without it the page would have no satellites.

```js
  { id: "1", azimuth_deg: 10, elevation_deg: 60 },
```
Satellite number 1. `id` is its name (text, so it is in quotes). `azimuth_deg: 10` is its compass direction in degrees, where 0 is north and 90 is east (this is how `docs/interface.md` defines it), so 10 is almost due north. `elevation_deg: 60` means it is high in the sky. The comma ends this item so the next can follow.

```js
  { id: "2", azimuth_deg: 100, elevation_deg: 35 },
```
Satellite 2: a little south of east (100 degrees) and about a third of the way up the sky (35 degrees).

```js
  { id: "3", azimuth_deg: 235, elevation_deg: 20 },
  { id: "4", azimuth_deg: 325, elevation_deg: 20 },
```
Satellites 3 and 4. Satellite 3 is in the south-west (235 degrees) and satellite 4 in the north-west (325 degrees). Both are low (20 degrees). Together the four are spread around the compass, which is what lets the distance lines cross at a single point. Satellites that were all in one direction would give a poor result.

```js
];
```
Closes the list.

```js
// Ground map: it shows a square from -half to +half metres, east and north.
```
A comment: the map covers a square. "Half" is the next number: the map reaches that far to each side of the phone, in both the east and north directions.

```js
export const mapHalfWidthM = 1000; // placeholder, provisional
```
The map reaches 1000 metres each way from the phone. Worked example: from -1000 to +1000 is 2000 m, so the square is 2 km wide, and the page's map note says "about 2 km wide". Without this the map would have no size.

```js
export const lineSamples = 40; // points per distance line, placeholder
```
The mechanism spreads 40 points along the part of each distance line near the map, then keeps only the points that land inside the map, so a drawn line has 40 points or fewer (with the numbers in this file, 26 to 32). If too few land inside, it tries again with more. More points give a smoother curve but more work. The number is sent to the mechanism when the page asks for the lines.

```js
// Clock error slider, stored in seconds. 0 to 3 microseconds in steps of 0.05 microseconds.
```
A comment. A microsecond is one millionth of a second. The clock error is how wrong the phone's clock is. It is kept in seconds.

```js
export const clockSlider = { min_s: 0, max_s: 3e-6, step_s: 5e-8 }; // placeholder, provisional
```
The slider's start, end and step, all in seconds. `3e-6` is scientific writing for 0.000003 s (3 microseconds). `5e-8` is 0.00000005 s (0.05 microseconds). Worked example: the slider has (3e-6 - 0) / 5e-8 = 60 steps. Light covers 299,792,458 m each second, so one step of 5e-8 s is 5e-8 x 299,792,458, about 15 m of extra distance, and the full 3 microseconds is about 899 m. Without this line the first screen could not build its clock slider.

```js
// Error colour thresholds in metres: below ok is "ok", below warn is "warn", else "bad".
```
A comment explaining the next line: a position error under `ok_m` counts as "ok", under `warn_m` as "warn", and anything bigger as "bad". The page uses these three words to choose a colour.

```js
export const errorLimits = { ok_m: 10, warn_m: 100 }; // placeholder, provisional
```
The two limits, in metres. Worked example: an error of 4 m is "ok"; 50 m is "warn"; 250 m is "bad". An error of exactly 10 m is not below 10, so it counts as "warn". Without this line the page could not colour the error.

```js
// Rung 4 (relativity) section. The satellites and receiver above are reused.
```
A comment: the relativity section (the fourth step of the story) has its own settings below, and it reuses the receiver and satellites above.

```js
export const relativitySlider = { min_h: 0, max_h: 24, step_h: 1, start_h: 24 }; // placeholder, provisional: hours of drift. Starts at one day so the effect is already showing.
```
The relativity slider counts hours of drift. It runs from 0 to 24 hours in steps of 1 hour (so there are 24 steps). It now starts at 24, one full day, so a visitor sees the effect of the drift straight away instead of a slider at zero. Without it the relativity section would have no slider range.

```js
// The two maps in this section show a square 40 km wide (-20000 to +20000 m). With the clock trusted at 24 h all four
// distance lines stay on a map this wide; on a 20 km wide map two would leave it.
```
Two comments explaining the next number. The relativity section draws two maps. Each shows a square area 40 km wide, running from 20,000 m west or south of the phone to 20,000 m east or north. When the phone's clock is trusted after a full day of drift, all four distance lines still fit on a map that wide. On a map only 20 km wide, two of the lines would run off the edge. Nothing breaks without the comments.

```js
export const relativityMapHalfWidthM = 20000; // placeholder, provisional
```
The half-width of those maps, in metres (`M` at the end of the name means metres): 20000 m from the centre to each edge, so 40 km across. Half-width is the distance from the middle to one side. Without it the relativity section would not know how big to draw its maps.

```js
// Zero, so at 0 hours both ways of solving agree and show 0 m. A 1 microsecond phone clock error would put
// about 500 m on the "trusted clock" result before any drift happens.
```
Two comments explaining the next number. The relativity section solves twice: once trusting the phone's clock and once working out the clock error. With a clock error of zero, both agree at 0 m at 0 hours. A 1 microsecond clock error would already give a result about 500 m out on the "trusted clock" side before any drift, which would hide the effect the slider is meant to show. Recomputed with the mechanism and the receiver and satellites above: a 1 microsecond clock error puts the trusted-clock result about 520 m out, so "about 500 m" holds.

```js
export const relativityPhoneClockErrorS = 0; // placeholder, provisional: the phone's own clock error
```
The phone's own clock error in this section, in seconds. It is 0, for the reason above. Without it the relativity section would have no value to hand to the mechanism.
