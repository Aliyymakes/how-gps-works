# signal.py, line by line

Source: `mechanism/signal.py`

## What this file is for
Every GPS satellite sends its own long repeating pattern of +1 and -1 values, called its C/A code. This file makes that pattern, makes a noisy copy of it that arrives late (like a phone would hear it), and then works out how late the copy is by trying every possible delay. That delay is what later turns into a distance. If you have never read code, start with [how to read code](../how-to-read-code.md).

## Which files it talks to
- `numpy` (an add-on library for fast number lists): used for shifting lists, random noise and multiplying lists together.
- `web/bridge.js`: lists `signal.py` among the files it loads into the browser, so the page can call it.
- `web/step-signal.js` and `web/dev/step-signal.html`: the page step that calls `ca_code`, `make_received` and `correlate` and shows the results (the page uses satellite 7, delay 300 chips, seed 1).
- `docs/interface.md`: the contract that says what each function takes and returns. This file must keep to it.
- `tests/test_signal.py`: the tests that check the code against the public GPS specification.
- It does not import any other file in `mechanism/`.

## In three lines
1. `ca_code(prn)` runs two 10-slot "shift registers" for 1023 steps and combines them into 1023 values of +1 or -1.
2. `make_received(...)` slides that code later by a whole number of chips and adds random noise.
3. `correlate(...)` tries all 1023 shifts, scores each one, and reports the best shift and how clearly it beats the runner-up.

## The code, line by line

### The top note

```python
"""GPS C/A code, a noisy received copy of it, and the correlator that finds its delay.

Source (looked up, not from memory): IS-GPS-200 Revision N (01-AUG-2022, "NAVSTAR GPS
Space Segment/Navigation User Segment Interfaces"), file IS-GPS-200N.pdf downloaded from
https://www.gps.gov/sites/default/files/2025-07/IS-GPS-200N.pdf
  - section 3.3.2.3 "C/A-Code Generation": G1 = X10 + X3 + 1, G2 = X10 + X9 + X8 + X6 + X3 + X2 + 1,
    both 10-stage registers start as 1111111111, both are clocked once per chip.
  - Table 3-Ia "Code Phase Assignments" (sheets 1 and 2): for each PRN, the two G2 stages whose
    outputs are added (the "two-tap coder" / phase selector), and the "First 10 Chips Octal".
  - Table 3-IV: code state 0 is the reference carrier phase, code state 1 is turned 180 degrees.
    So we map logic 0 -> +1 and logic 1 -> -1.
  - Octal note under Table 3-Ia: the first octal digit (always 1 in the table) is ONE bit, the
    first chip; the other three digits are 3 bits each for chips 2 to 10. Example, PRN 1:
    octal 1440 -> chips 1 100 100 000 = 1100100000 (logic bits).
The taps for PRN 1 to 32 are all taken from Table 3-Ia.
"""
```

Everything between the two sets of three quote marks is a note to humans. Python ignores it. Without it the code would still run, but nobody would know where the numbers came from.

- The first line says what the file holds: the code, a noisy copy, and the "correlator" (the part that finds the delay).
- The `Source` lines name the official GPS document, IS-GPS-200 Revision N, and where it was downloaded. The team looked it up rather than remembering it. That matters because a wrong tap number would give a code that no real GPS receiver would recognise.
- `G1 = X10 + X3 + 1` and `G2 = ...` describe the two registers. Each `X` followed by a number is a slot in the register (slot 3, slot 10 and so on). The "+ 1" at the end is just how the specification writes the formula; the code below applies it as "XOR slot 3 and slot 10" (explained at the `g1_new` line).
- "both start as 1111111111" means all ten slots begin holding 1. "clocked once per chip" means each register moves one step for every chip produced.
- Table 3-Ia gives, for each satellite number (PRN), which two slots of the second register to read.
- Table 3-IV says the logic value 0 means the wave is unchanged, and 1 means the wave is flipped upside down (turned 180 degrees). That is why logic 0 becomes +1 and logic 1 becomes -1 later.
- The octal note is a trap. The specification prints the first 10 chips as an octal (base 8) number such as 1440. The first digit is only ONE bit, not three. So 1440 means `1`, then `100`, `100`, `000`, which is the ten bits 1100100000. The code produces exactly those bits for PRN 1 (checked by running it). Compare against these 0/1 bits, not against the +1/-1 values.

### Imports and the length of the code

```python
import numpy as np
```

This brings in numpy, a library of fast tools for lists of numbers, and gives it the short name `np` so later lines can write `np.roll` instead of `numpy.roll`. Without it, `make_received` and `correlate` would fail with "name np is not defined".

```python
CODE_LENGTH = 1023
```

A named number: the C/A code is exactly 1023 chips long (2 to the power 10, minus 1, which is the longest pattern a 10-slot register can run through before repeating). Writing it once, with a name, stops the number 1023 being retyped in many places. If it were wrong, every list in this file would have the wrong length.

### The two taps table

```python
# Table 3-Ia, column "C/A (G2i)": the two G2 stages (numbered 1 to 10) added together, per PRN.
```

A comment (a line starting with `#`; Python skips it). It says the table below comes from Table 3-Ia and that the two numbers are stage (slot) numbers from 1 to 10.

```python
G2_TAPS = {
    1: (2, 6), 2: (3, 7), 3: (4, 8), 4: (5, 9), 5: (1, 9), 6: (2, 10), 7: (1, 8), 8: (2, 9),
    9: (3, 10), 10: (2, 3), 11: (3, 4), 12: (5, 6), 13: (6, 7), 14: (7, 8), 15: (8, 9),
    16: (9, 10), 17: (1, 4), 18: (2, 5), 19: (3, 6), 20: (4, 7), 21: (5, 8), 22: (6, 9),
    23: (1, 3), 24: (4, 6), 25: (5, 7), 26: (6, 8), 27: (7, 9), 28: (8, 10), 29: (1, 6),
    30: (2, 7), 31: (3, 8), 32: (4, 9),
}
```

This is a lookup table (a Python "dictionary"): the thing before each colon is the satellite number (PRN), and the pair of numbers after it is the two "taps". A tap is a slot of the second register that we read from. The curly brackets `{ }` hold the whole table, and the last `}` closes it.

Why it exists: this one pair is the only difference between satellite codes. All 32 satellites use the same two registers, but each reads a different pair of slots from the second one, so each gets a different code. For satellite 7 the pair is `(1, 8)`: read slot 1 and slot 8.

What breaks without it: there would be no way to choose a satellite. The keys of this table (1 to 32) are also how the file decides whether a satellite number is valid (next function).

### Rejecting bad satellite numbers

```python
def _bad_prn(prn):
```

`def` starts a new function, a named, reusable recipe. This one is called `_bad_prn` and receives one input, `prn` (the satellite number). The leading underscore is a habit meaning "only used inside this file".

```python
    """True if prn is not a whole number from 1 to 32 (bool is rejected too)."""
```

A note describing the function. "bool" means `True`/`False`; Python quietly treats `True` as the number 1, so the code has to reject it on purpose.

```python
    return isinstance(prn, bool) or not isinstance(prn, int) or prn not in G2_TAPS
```

`return` hands back the answer. The answer is `True` ("this is bad") if any of three things holds, joined by `or`:
1. `isinstance(prn, bool)`: it is `True` or `False`.
2. `not isinstance(prn, int)`: it is not a whole number (for example `7.5` or the text `"7"`).
3. `prn not in G2_TAPS`: it is a whole number, but not one of the keys 1 to 32 (for example 0 or 33).

The order matters: the third check only runs if the first two did not already decide. Without this function, a bad satellite number would either crash or silently use the wrong code.

### Making the raw 0/1 code

```python
def _logic_bits(prn):
```

Starts the function that does the real work of building the code. It takes the satellite number.

```python
    """The 1023 chips of the C/A code as logic bits 0 and 1 (before mapping to +1/-1)."""
```

A note: the result is a list of 0s and 1s. Turning them into -1 and +1 happens later, in `ca_code`.

The idea, before the lines. A shift register is a row of ten boxes, each holding a 0 or a 1. On every tick, all the values slide one box along, the value in the last box falls out, and a new value, worked out from some of the old boxes, enters the first box. Adding two bits here means XOR (written `^` in Python): the answer is 1 if the two bits differ, 0 if they are equal. So 0^0 = 0, 1^1 = 0, 0^1 = 1, 1^0 = 1. Two registers (called G1 and G2) run side by side. On each tick, one chip is made by XOR-ing the output of G1 with an output taken from G2. Because the feedback rules are chosen well, the pattern does not repeat for 1023 ticks.

```python
    g1 = [1] * 10  # stage 1 is g1[0] ... stage 10 is g1[9]; all ones at the start
```

Creates register G1 as a list of ten 1s (`[1] * 10` repeats the list `[1]` ten times). The comment warns about a counting trap: the specification numbers the slots 1 to 10, but Python lists start counting at 0, so slot 1 is `g1[0]` and slot 10 is `g1[9]`. The start value of all ones is required by the specification. If it started as all zeros, the register would stay zeros forever and the code would be all one value.

```python
    g2 = [1] * 10
```

The same for register G2.

```python
    tap_a, tap_b = G2_TAPS[prn]
```

Looks up this satellite's two taps in the table and gives them names. For satellite 7 this sets `tap_a = 1` and `tap_b = 8`. Without it we would not know which slots of G2 to read.

```python
    bits = []
```

Starts an empty list that will collect the 1023 chips.

```python
    for _ in range(CODE_LENGTH):
```

A loop: do the indented lines below 1023 times. `range(1023)` counts 0 to 1022, and the name `_` is a throw-away name because we do not need the counting number itself. Each pass makes one chip and moves both registers one step.

```python
        # G1 output is stage 10. G2 output is stage tap_a added (XOR) to stage tap_b.
```

A comment saying what the next two lines compute.

```python
        g1_out = g1[9]
```

G1's output is simply its last slot, stage 10 (`g1[9]`). At the start this is 1.

```python
        g2_out = g2[tap_a - 1] ^ g2[tap_b - 1]
```

G2's output is the XOR of the two tapped slots. The `- 1` converts the specification's slot numbers (starting at 1) into Python positions (starting at 0). Worked example, satellite 7, first tick: `tap_a = 1`, `tap_b = 8`, so it reads `g2[0]` and `g2[7]`. Both are 1, and 1 ^ 1 = 0, so `g2_out = 0`.

```python
        # The chip is G1 output added (XOR) to the G2 output.
```

A comment for the next line.

```python
        bits.append(g1_out ^ g2_out)
```

Makes the chip: `g1_out ^ g2_out`, and adds it to the end of the `bits` list (`append`). First tick of satellite 7: 1 ^ 0 = 1. Without this line nothing would be collected and the function would return an empty list.

```python
        # G1 feedback: stages 3 and 10 added together.
```

A comment. "Feedback" means the value that is fed back in at the front of the register.

```python
        g1_new = g1[2] ^ g1[9]
```

The new value for G1 is XOR of stage 3 (`g1[2]`) and stage 10 (`g1[9]`). That is the specification's `G1 = X10 + X3 + 1`: the "+ 1" is the constant term, which just means the new value goes into the first slot. First tick: 1 ^ 1 = 0.

```python
        # G2 feedback: stages 2, 3, 6, 8, 9 and 10 added together.
```

A comment for the next line.

```python
        g2_new = g2[1] ^ g2[2] ^ g2[5] ^ g2[7] ^ g2[8] ^ g2[9]
```

The new value for G2 is the XOR of six slots: stages 2, 3, 6, 8, 9, 10 (positions 1, 2, 5, 7, 8, 9). This is `G2 = X10 + X9 + X8 + X6 + X3 + X2 + 1` from the specification. Six ones XOR-ed give 0 (an even count of ones gives 0), so on the first tick `g2_new = 0`. A wrong slot here would give a code that looks random but is not the real GPS code.

```python
        # Shift each register one place (stage 1 to 2, 2 to 3, ...) and put the feedback in stage 1.
```

A comment for the next two lines.

```python
        g1 = [g1_new] + g1[:9]
```

Builds the next state of G1: the new value first, followed by the first nine old values (`g1[:9]` means "positions 0 to 8"). The old last value (position 9) is dropped, which is the slide along. Without this line the registers would never move and every chip would be the same.

```python
        g2 = [g2_new] + g2[:9]
```

The same slide for G2.

Here is a worked run for satellite 7 (all computed by running the code). Boxes are shown as stage 1 to stage 10, left to right:

```text
tick  G1 before          G2 before          g1_out  g2_out(1^8)  chip
 1    1111111111         1111111111           1        0           1
 2    0111111111         0111111111           1        1           0
 3    0011111111         0011111111           1        1           0
 4    0001111111         1001111111           1        0           1
```

On tick 1 the new G1 value is 1^1 = 0 and the new G2 value is 0, so both registers gain a 0 on the left. On tick 3 the G2 feedback is 0^1^1^1^1^1 = 1 (the six feedback stages 2, 3, 6, 8, 9, 10 hold 0, 1, 1, 1, 1, 1: five ones, an odd count), so on tick 4 G2 starts with a 1. The first chips for satellite 7 are therefore 1, 0, 0, 1, ... (the code goes on 1 0 0 1 0 1 1 0 0 1 1 1 for the first twelve).

```python
    return bits
```

After the loop has run 1023 times, gives back the list of 1023 zeros and ones. This line is outside the loop (it is indented less), so it runs once, at the end.

### Turning bits into +1 and -1

```python
def ca_code(prn):
```

The public function that other files call. It takes the satellite number.

```python
    """The C/A code of satellite prn (1 to 32): a list of 1023 values, each +1 or -1."""
```

A note describing the result.

```python
    if _bad_prn(prn):
```

Asks the checker from earlier whether the satellite number is bad. The line indented under this `if` only runs when it is.

```python
        return {"error": "prn must be a whole number from 1 to 32."}
```

For a bad number, hands back a small dictionary with an `"error"` message instead of crashing. The page can show that message in plain words. The convention (an error comes back as a dictionary with the key `"error"`) is part of `docs/interface.md`. Without it, a bad input would stop the page with a technical crash.

```python
    # Logic 0 -> +1, logic 1 -> -1 (see Table 3-IV note above).
```

A comment explaining the mapping used next.

```python
    return [1 - 2 * b for b in _logic_bits(prn)]
```

Builds the final list in one line (a list of 1023 chips, one per bit): for each bit `b` from `_logic_bits(prn)`, work out `1 - 2 * b`. This is the formula that turns a 0 into +1 and a 1 into -1:
- b = 0: 1 - 2 * 0 = 1 - 0 = +1
- b = 1: 1 - 2 * 1 = 1 - 2 = -1

For satellite 7 the first twelve bits 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1 become -1, +1, +1, -1, +1, -1, -1, +1, +1, -1, -1, -1. Why +1/-1 and not 0/1? Because multiplying two such values gives +1 when they agree and -1 when they disagree, which is exactly what the matching step later needs. Across all 1023 chips of satellite 7, the values add up to -1 (there is one more -1 than +1).

### Making the noisy, late copy

```python
def make_received(prn, delay_chips, noise_std, seed=0):
```

Starts the function that pretends to be the phone's antenna. It takes four inputs: which satellite, how many chips late the signal arrives, how strong the noise is (`noise_std`, the "standard deviation", a typical size of the random wobble), and a `seed`. `seed=0` means that if the caller gives no seed, 0 is used.

```python
    """What the receiver hears: the code shifted by delay_chips whole chips, plus random noise."""
```

A note describing it.

```python
    code = ca_code(prn)
```

Gets the clean +1/-1 code for this satellite by calling `ca_code`, which is defined earlier in this same file. The result may be an error dictionary if `prn` was bad; the next two lines check for that and pass the error straight back.

```python
    if isinstance(code, dict):
```

Checks whether what came back is a dictionary (the error form) rather than a list.

```python
        return code
```

If it was an error dictionary, hands that same error straight back so the caller sees the message. Without these two lines the next lines would try to shift a dictionary and crash.

```python
    if isinstance(delay_chips, bool) or not isinstance(delay_chips, int) or not 0 <= delay_chips <= 1022:
```

Checks the delay. It is rejected if it is `True`/`False`, if it is not a whole number (so `300.0` is rejected too), or if it is outside 0 to 1022. The range is 0 to 1022 because there are 1023 possible shifts, and shifting by 1023 would be the same as shifting by 0.

```python
        return {"error": "delay_chips must be a whole number from 0 to 1022."}
```

The error handed back for a bad delay.

```python
    if isinstance(noise_std, bool) or not isinstance(noise_std, (int, float)) or not noise_std >= 0 or noise_std == float("inf"):
```

Checks the noise size. It is rejected if it is `True`/`False`, not a number at all, not 0 or more, or infinite. Writing the test as `not noise_std >= 0` (rather than `noise_std < 0`) means the odd value "NaN" (not a number), which fails every comparison, is rejected too.

```python
        return {"error": "noise_std must be a number that is 0 or more."}
```

The error for a bad noise size.

```python
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
```

Checks the seed: it must be a whole number, not `True`/`False`, and 0 or more.

```python
        return {"error": "seed must be a whole number that is 0 or more."}
```

The error for a bad seed.

All these checks matter because the page lets people type numbers. Without them, a bad value would crash deep inside numpy or, worse, quietly give a wrong picture.

```python
    # Shift the code later by delay_chips; the chips pushed off the end wrap round to the start.
```

A comment. Imagine the 1023 chips written in a ring: pushing everything later by some steps moves the chips that fall off the end back round to the front.

```python
    shifted = np.roll(np.array(code, dtype=float), delay_chips)
```

`np.array(code, dtype=float)` turns the list into a numpy array of decimal numbers (needed so we can add decimal noise and do fast maths). `np.roll(array, n)` slides everything `n` places later, wrapping round. Small worked example with a 5-chip list: `np.roll([1, -1, -1, 1, 1], 2)` gives `[1, 1, 1, -1, -1]`; the last two values moved to the front. For the page's case, `delay_chips = 300`, so chip number 0 of the code ends up at position 300, and the chip that was at position 723 ends up at position 0 (723 + 300 = 1023, which wraps to 0). Without the shift there would be no delay to find.

```python
    noise = np.random.default_rng(seed).normal(0.0, noise_std, CODE_LENGTH)
```

Makes the random noise. `np.random.default_rng(seed)` creates a random number generator; the seed fixes its starting point, so the same seed always gives exactly the same "random" numbers. `.normal(0.0, noise_std, CODE_LENGTH)` draws 1023 numbers from a bell-curve (normal) distribution centred on 0.0 with width `noise_std`. Most values land within about one `noise_std` of zero. Seed 1 with `noise_std = 1.0` starts 0.3456, 0.8216, 0.3304 (computed by running it); with `noise_std = 0` every value is 0 and the signal is clean. Why a seed? So the page and the tests show the same picture every time, and a person can say "seed 1" and get the same result as everyone else. Without it, every visit would look different and tests could not rely on results.

```python
    return [float(x) for x in shifted + noise]
```

`shifted + noise` adds the two arrays chip by chip. Worked example with PRN 7, delay 300, seed 1, noise 1.0: the first value of the result is the code value at position 723 (which is -1) plus noise 0.3456, giving about -0.654. And at position 300 the code's own first chip (-1) meets noise of about -0.593, giving about -1.593. The `[float(x) for x in ...]` part turns each numpy number into a plain Python decimal number, because the page needs plain numbers it can pass to JavaScript.

### Finding the delay by trying every shift

```python
def correlate(received, prn):
```

Starts the function that plays the receiver's job: given the signal it heard and the satellite number it is looking for, find the delay.

```python
    """Try every shift of satellite prn's code against received and score how well each fits.

    Score 1.0 means a perfect match (no noise). peak_to_next is the best score divided by the
    second best score; a big number means a clear winner. If no score is above 0 there is no
    peak, so we return 1.0. If the best is above 0 but the second best is not, we return 1e9 ("extremely clear"). A plain big number is
    used instead of infinity because infinity is not valid JSON.
    """
```

A long note. Key points: a score of 1.0 is a perfect match; `peak_to_next` is the best score divided by the second best; if there is no positive peak the answer is 1.0 ("nothing stands out"); if the second best is zero or less, the answer is 1e9 (the number 1 followed by nine zeros, written the short way), because infinity cannot be written in JSON, the text format used to pass results to the web page.

```python
    code = ca_code(prn)
```

Gets the clean code for the satellite we are hunting for.

```python
    if isinstance(code, dict):
```

Checks for the error form (bad satellite number).

```python
        return code
```

Passes that error straight back.

```python
    try:
```

Starts a "try this, and if it goes wrong, do something kind instead" block. The indented line below is the thing being tried.

```python
        values = np.array(received, dtype=float)
```

Turns the received list into a numpy array of decimal numbers. If `received` cannot be read as numbers (for example it contains a word such as `"abc"`), numpy raises an error, which the next lines catch. Text that spells a number, such as `"1.5"`, is quietly turned into that number and accepted.

```python
    except (TypeError, ValueError):
```

Says: if that attempt raised one of these two kinds of error, run the indented line below instead of crashing.

```python
        return {"error": "received must be a list of 1023 numbers."}
```

The friendly error handed back in that case.

```python
    if values.shape != (CODE_LENGTH,) or not np.all(np.isfinite(values)):
```

Two checks. `values.shape != (1023,)` means "the list is not exactly 1023 long" (a shape of `(1023,)` means one row of 1023 values). `np.isfinite(values)` marks each number as ordinary (not infinity and not "not a number"), and `np.all(...)` is true only if every one of them is. If either test fails, the input is rejected. Without this, a list of the wrong length would make the later multiplication fail or give nonsense.

```python
        return {"error": "received must be a list of 1023 finite numbers."}
```

The error for that case.

The idea of the next lines. Correlation is a way of asking "how much does this signal look like that pattern?". Multiply the two chip by chip, then average. Where the pattern lines up with the signal, each product is mostly +1 (since +1 times +1 and -1 times -1 both give +1), so the average is near 1. Where it does not line up, the products are a random mix of +1 and -1, so the average is near 0. We slide the pattern through all 1023 possible positions and see where the score is highest; that position is the delay.

```python
    code_array = np.array(code, dtype=float)
```

Turns our clean code into a numpy array of decimals so that it can be shifted and multiplied quickly.

```python
    scores = []
```

An empty list that will hold one score for each of the 1023 shifts.

```python
    for shift in range(CODE_LENGTH):
```

A loop that runs once for each shift, 0 to 1022, with the current shift stored in `shift`.

```python
        # Shift our copy of the code by this many chips, multiply chip by chip, then average.
```

A comment describing the next line.

```python
        scores.append(float(np.dot(values, np.roll(code_array, shift)) / CODE_LENGTH))
```

Reading from the inside out:
1. `np.roll(code_array, shift)`: slide our clean code later by `shift` chips (same wrap-round as in `make_received`).
2. `np.dot(values, ...)`: multiply the received values and the shifted code chip by chip and add up all 1023 products.
3. `/ CODE_LENGTH`: divide by 1023 to get the average.
4. `float(...)` makes it a plain number, and `scores.append(...)` adds it to the list.

Worked example, noise-free signal for PRN 7 with delay 300. At `shift = 300` our shifted code is identical to the received signal, so all 1023 products are (+1)(+1) or (-1)(-1) = +1; the total is 1023 and the score is 1023 / 1023 = 1.0. At `shift = 0` and at `shift = 1` the totals are -1, so each score is -1 / 1023, about -0.001. With seed 1 and noise 1.0, the score at shift 300 is about 1.0096, while shifts 0, 1 and 299 score about 0.022, -0.019 and 0.054: all close to zero. The noise shakes each score a little but does not hide the peak, because random noise averages out over 1023 chips while the real match does not.

This loop is the heavy work of the file: 1023 shifts of 1023 chips each, about a million multiplications. It is the reason numpy is used.

```python
    best = int(np.argmax(scores))
```

`np.argmax(scores)` finds the position of the biggest score, which is the best shift. `int(...)` turns it into a plain whole number. For PRN 7 with delay 300 it gives 300. Because `correlate` shifts forward by the same rule as `make_received`, the best shift equals the delay that was put in.

```python
    others = sorted(scores[:best] + scores[best + 1:], reverse=True)
```

Builds the list of all the other scores: `scores[:best]` is everything before the best one, `scores[best + 1:]` is everything after it, and `+` glues them together. `sorted(..., reverse=True)` puts them in order from highest to lowest. We need this to find the runner-up.

```python
    next_best = others[0]
```

The first item of the sorted list (position 0) is the highest of the others, the "second best score". For the noise-free PRN 7 signal this is about 0.0616 (exactly 63/1023); with seed 1 and noise 1.0 it is about 0.1376.

```python
    if scores[best] <= 0:
```

Checks the unusual case where even the best score is 0 or below.

```python
        # Nothing matches at any shift (for example a silent input): there is no peak at all.
```

A comment explaining that case. A signal of all zeros would score 0 everywhere.

```python
        peak_to_next = 1.0
```

Sets the answer to 1.0, meaning "the best is no better than the rest". Without this branch, dividing by a zero or negative number could give a misleading or invalid ratio.

```python
    elif next_best <= 0:
```

`elif` means "otherwise, if". This is the case where there is a real positive peak but the runner-up is 0 or negative.

```python
        # A real peak and nothing else positive: the ratio would be meaningless, so report a very large number.
```

A comment: dividing by zero is impossible and dividing by a negative number gives a negative ratio, which would be wrong.

```python
        peak_to_next = 1e9
```

Uses 1e9 (1,000,000,000) as "extremely clear" instead of infinity, because infinity is not valid JSON.

```python
    else:
```

Otherwise: the ordinary case, with a positive best score and a positive second best.

```python
        peak_to_next = scores[best] / next_best
```

The ratio of the best score to the second best. Worked examples for PRN 7, delay 300: noise-free, 1.0 / 0.0616 = 16.24; with noise 1.0 and seed 1, 1.0096 / 0.1376 = 7.34. A big ratio means a clear winner. A ratio near 1 means two shifts look almost equally good, so the receiver cannot be sure of the delay (this is what very heavy noise causes).

```python
    return {"scores": scores, "best_delay_chips": best, "peak_to_next": float(peak_to_next)}
```

Hands back a dictionary with three entries, exactly as promised in `docs/interface.md`: the list of 1023 `scores`, the `best_delay_chips` (the winning shift), and `peak_to_next`. The `float(...)` makes the ratio a plain decimal number. The page draws the scores as a graph and shows `peak_to_next` in the "Peak stands out by" figure (for example "7.3×"). It also uses `best_delay_chips` to mark the winning shift and to show it in chips.

## Things worth knowing
- The chips repeat every 1023 steps, which is why shifts wrap round and why only whole-chip delays between 0 and 1022 make sense.
- The delay is found only to the nearest whole chip. One chip is about 293 m of travel (`docs/facts.md`), so this step answers "which chip", not "how many metres exactly".
