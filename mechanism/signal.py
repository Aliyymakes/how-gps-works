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
import numpy as np

CODE_LENGTH = 1023

# Table 3-Ia, column "C/A (G2i)": the two G2 stages (numbered 1 to 10) added together, per PRN.
G2_TAPS = {
    1: (2, 6), 2: (3, 7), 3: (4, 8), 4: (5, 9), 5: (1, 9), 6: (2, 10), 7: (1, 8), 8: (2, 9),
    9: (3, 10), 10: (2, 3), 11: (3, 4), 12: (5, 6), 13: (6, 7), 14: (7, 8), 15: (8, 9),
    16: (9, 10), 17: (1, 4), 18: (2, 5), 19: (3, 6), 20: (4, 7), 21: (5, 8), 22: (6, 9),
    23: (1, 3), 24: (4, 6), 25: (5, 7), 26: (6, 8), 27: (7, 9), 28: (8, 10), 29: (1, 6),
    30: (2, 7), 31: (3, 8), 32: (4, 9),
}


def _bad_prn(prn):
    """True if prn is not a whole number from 1 to 32 (bool is rejected too)."""
    return isinstance(prn, bool) or not isinstance(prn, int) or prn not in G2_TAPS


def _logic_bits(prn):
    """The 1023 chips of the C/A code as logic bits 0 and 1 (before mapping to +1/-1)."""
    g1 = [1] * 10  # stage 1 is g1[0] ... stage 10 is g1[9]; all ones at the start
    g2 = [1] * 10
    tap_a, tap_b = G2_TAPS[prn]
    bits = []
    for _ in range(CODE_LENGTH):
        # G1 output is stage 10. G2 output is stage tap_a added (XOR) to stage tap_b.
        g1_out = g1[9]
        g2_out = g2[tap_a - 1] ^ g2[tap_b - 1]
        # The chip is G1 output added (XOR) to the G2 output.
        bits.append(g1_out ^ g2_out)
        # G1 feedback: stages 3 and 10 added together.
        g1_new = g1[2] ^ g1[9]
        # G2 feedback: stages 2, 3, 6, 8, 9 and 10 added together.
        g2_new = g2[1] ^ g2[2] ^ g2[5] ^ g2[7] ^ g2[8] ^ g2[9]
        # Shift each register one place (stage 1 to 2, 2 to 3, ...) and put the feedback in stage 1.
        g1 = [g1_new] + g1[:9]
        g2 = [g2_new] + g2[:9]
    return bits


def ca_code(prn):
    """The C/A code of satellite prn (1 to 32): a list of 1023 values, each +1 or -1."""
    if _bad_prn(prn):
        return {"error": "prn must be a whole number from 1 to 32."}
    # Logic 0 -> +1, logic 1 -> -1 (see Table 3-IV note above).
    return [1 - 2 * b for b in _logic_bits(prn)]


def make_received(prn, delay_chips, noise_std, seed=0):
    """What the receiver hears: the code shifted by delay_chips whole chips, plus random noise."""
    code = ca_code(prn)
    if isinstance(code, dict):
        return code
    if isinstance(delay_chips, bool) or not isinstance(delay_chips, int) or not 0 <= delay_chips <= 1022:
        return {"error": "delay_chips must be a whole number from 0 to 1022."}
    if isinstance(noise_std, bool) or not isinstance(noise_std, (int, float)) or not noise_std >= 0 or noise_std == float("inf"):
        return {"error": "noise_std must be a number that is 0 or more."}
    if isinstance(seed, bool) or not isinstance(seed, int):
        return {"error": "seed must be a whole number."}
    # Shift the code later by delay_chips; the chips pushed off the end wrap round to the start.
    shifted = np.roll(np.array(code, dtype=float), delay_chips)
    noise = np.random.default_rng(seed).normal(0.0, noise_std, CODE_LENGTH)
    return [float(x) for x in shifted + noise]


def correlate(received, prn):
    """Try every shift of satellite prn's code against received and score how well each fits.

    Score 1.0 means a perfect match (no noise). peak_to_next is the best score divided by the
    second best score; a big number means a clear winner. If the second best score is 0 or
    negative the division is meaningless, so we return 1e9 ("extremely clear"). A plain big number is
    used instead of infinity because infinity is not valid JSON.
    """
    code = ca_code(prn)
    if isinstance(code, dict):
        return code
    try:
        values = np.array(received, dtype=float)
    except (TypeError, ValueError):
        return {"error": "received must be a list of 1023 numbers."}
    if values.shape != (CODE_LENGTH,) or not np.all(np.isfinite(values)):
        return {"error": "received must be a list of 1023 finite numbers."}
    code_array = np.array(code, dtype=float)
    scores = []
    for shift in range(CODE_LENGTH):
        # Shift our copy of the code by this many chips, multiply chip by chip, then average.
        scores.append(float(np.dot(values, np.roll(code_array, shift)) / CODE_LENGTH))
    best = int(np.argmax(scores))
    others = sorted(scores[:best] + scores[best + 1:], reverse=True)
    next_best = others[0]
    # If the runner-up is not positive there is no meaningful ratio: report a very large number.
    peak_to_next = scores[best] / next_best if next_best > 0 else 1e9
    return {"scores": scores, "best_delay_chips": best, "peak_to_next": float(peak_to_next)}
