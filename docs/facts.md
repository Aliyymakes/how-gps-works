# Fact sheet: numbers used by the page and documents

Every number the page and documents use, with the exact value as the source states it. Values were read from fetched pages on 2026-11-23. Status: `confirmed` (read on a fetched official page), `derived` (our arithmetic, shown below the table), `unconfirmed` (not read on a fetched page, or only a non-official page states it).

IS-GPS-200 means Revision N (01-AUG-2022), the latest revision on gps.gov: <https://www.gps.gov/sites/default/files/2025-07/IS-GPS-200N.pdf>. Short names used below: SPS PS = GPS Standard Positioning Service Performance Standard, 4th Edition, Sept 2008: <https://www.gps.gov/sites/default/files/2025-07/2008-SPS-performance-standard.pdf>.

| # | Quantity | Value as the source states it | Unit | Source (link, section/table) | Used for | Status |
|---|----------|-------------------------------|------|------------------------------|----------|--------|
| 1 | Speed of light in vacuum | 299 792 458 (exact, standard uncertainty zero) | m s^-1 | NIST CODATA, <https://physics.nist.gov/cgi-bin/cuu/Value?c> | distance = c x time | confirmed |
| 2 | Speed of light used by GPS | c = 2.99792458 x 10^8 "which is the official WGS 84 speed of light. The user shall use the same value for the speed of light in all computations." | m/s | IS-GPS-200N, section 20.3.4.3 "Speed of Light" (also used in the clock-correction equation, section 20.3.3.3.3.1) | pseudorange to distance | confirmed |
| 3 | Orbit semi-major axis | 26,559.7 (nominal, "Reference Orbit Parameters", eccentricity 0.0, inclination 55.0 deg) | km | SPS PS (2008), Table 3.2-3 | orbit radius from Earth centre | confirmed |
| 4 | Orbit altitude above Earth | "approximately 20,200 km (12,550 miles)" | km | gps.gov Space Segment, <https://www.gps.gov/space-segment> | satellite height | confirmed |
| 5 | Orbital period | "Repeating ground tracks (11 hours 58 minutes)"; gps.gov: "Each satellite circles the Earth twice a day." | h min | NASA GSFC slides (Moreau, 2012), slide 8, <https://ntrs.nasa.gov/api/citations/20120010317/downloads/20120010317.pdf>; gps.gov Space Segment | orbit speed / period | confirmed |
| 6 | Period from Kepler (check) | 43 077 s = 11.966 h (about 11 h 58 min) | s | derived from rows 3 and 15 (D1) | cross-check of row 5 | derived |
| 7 | Half a sidereal day | sidereal day 86 164.0905 s (not read on a fetched page) | s | none fetched (IERS value from memory) | "about half a sidereal day" | unconfirmed |
| 8 | Orbital planes and baseline slots | "six equally-spaced orbital planes ... Each plane contains four 'slots' occupied by baseline satellites"; 24-slot baseline; "now effectively operates as a 27-slot constellation" | count | gps.gov Space Segment | constellation size | confirmed |
| 9 | Operational satellites (gps.gov page) | "As of July 3, 2023, there were a total of 31 operational satellites in the GPS constellation, not including the decommissioned, on-orbit spares." | count | gps.gov Space Segment (page is stale; points to NAVCEN for current status) | constellation size | confirmed |
| 10 | Operational satellites (newer) | "Current: 32 Presented (+7 residuals)"; "Required: 24 ops-ready satellites"; slide dated "As of: 4/13/2026" | count | Space Force, CGSIC briefing 21 Apr 2026, slide "Space Segment (Satellites)", <https://www.gps.gov/sites/default/files/2026-04/Mediate%2020260421_CGSIC%20MD%2031_FINAL.pdf> | constellation size, newest | confirmed (briefing slide, not a spec; NAVCEN page returned 403, so not cross-checked) |
| 11 | C/A code length | "each of which is a 1023 chip long linear pattern" (Gold code Gi(t), 1 ms long) | chips | IS-GPS-200N, section 3.2.1.3 | code length | confirmed |
| 12 | C/A chip rate | "chipping rate of 1023 kbps"; "G1 and G2 registers are clocked at 1.023 MHz" | kbps / MHz | IS-GPS-200N, sections 3.2.1.3 and 3.3.2.3 (C/A-Code Generation) | chip rate | confirmed |
| 13 | C/A code period | "of 1 millisecond in length" | ms | IS-GPS-200N, section 3.2.1.3 | code repeats every 1 ms | confirmed |
| 14 | Chip length in time and distance | 977.5 ns; 293.05 m | ns; m | derived (D2) | what one chip is worth | derived |
| 15 | Earth gravitational parameter | mu = 3.986005 x 10^14 "value of Earth's universal gravitational parameters" | m^3/s^2 | IS-GPS-200N, section 20.3.3.4.3 | Kepler check (row 6) | confirmed |
| 16 | L1 carrier frequency | "1575.42 MHz" | MHz | IS-GPS-200N, section 3.3.1.1 | signal band | confirmed |
| 17 | Minimum received power, L1 C/A | -158.5 (Table 3-Va, column "C/A or L2C", row L1, Block IIR, IIR-M/IIF, GPS III/IIIF; P(Y) is -161.5). Measured at "the output of a 3 dBi linearly polarized user receiving antenna (located near ground) ... when the SV is above a 5-degree elevation angle" | dBW | IS-GPS-200N, section 3.3.1.6, Table 3-Va; SPS PS section 2.2.1 repeats "-158.5 dBW for L1 C/A-code" | signal strength at the ground | confirmed |
| 18 | Specified receive bandwidth | "20.46 MHz" (Table 3-Va heading); two 20.46 MHz bands centred on L1 and L2 | MHz | IS-GPS-200N, sections 3.3.1.1 and 3.3.1.6 | noise bandwidth (D4) | confirmed |
| 19 | C/A main-lobe bandwidth | about 2.046 (2 x 1.023) | MHz | derived from row 12 (D4) | "about 2 MHz" noise bandwidth | derived |
| 20 | Boltzmann constant k | 1.380 649 x 10^-23 (exact) | J K^-1 | NIST CODATA, <https://physics.nist.gov/cgi-bin/cuu/Value?k> | thermal noise | confirmed |
| 21 | Reference noise temperature T | 290 (convention; no fetched page states it) | K | none fetched | thermal noise | unconfirmed |
| 22 | Thermal noise density kT | about -204 (D3 gives -203.98) | dBW/Hz | derived from rows 20 and 21 (D3); sources quoting -204 were only search summaries of arXiv/Safran pages, not fetched | "below the noise" | derived (T unconfirmed) |
| 23 | Thermal noise over 2.046 MHz | about -140.9 (D4); over 20.46 MHz about -130.9 | dBW | derived (D4) | signal vs noise | derived (T unconfirmed) |
| 24 | Course-slide noise figure (reference only) | "noise power at receiver: 1.413*10-14 W (or -138.5 dBW) in 2 MHz bandwidth"; C/A signal "-157.6 dBW"; "well below noise level" | dBW | TU Delft GNSS receivers lecture 3, <https://ocw.tudelft.nl/wp-content/uploads/Lecture_3_-_GNSS_receivers.pdf>. University slides, not official. -138.5 is higher than D4 because it includes receiver noise (about 512 K implied) | cross-check only | unconfirmed (non-official) |
| 25 | Special relativity effect on satellite clocks | "should fall behind earthbound clocks by seven microseconds ... per day" | us/day | NIST Taking Measure blog "Putting Einstein to the Test With the World's Most Accurate Clocks" (page dated 25 Feb 2026), <https://www.nist.gov/blogs/taking-measure/putting-einstein-test-worlds-most-accurate-clocks> | clock slow part | confirmed |
| 26 | General relativity effect | "should speed them up by 45 microseconds per day" | us/day | same NIST page | clock fast part | confirmed |
| 27 | Net relativistic offset | "GPS clocks run 38 microseconds per day faster than Earth clocks." NASA: "~38 microseconds per day relative to clocks on the ground (~11 km range error)" | us/day | same NIST page; NASA GSFC slides (Moreau 2012), slide 27 | net clock drift | confirmed |
| 28 | Factory fractional frequency offset | "-4.4647E-10" (IS-GPS-200N); NASA slide: "-4.46475x10-10" | dimensionless | IS-GPS-200N section 3.3.1.1; NASA slides slide 27 | factory offset | confirmed |
| 29 | Factory frequency offset in Hz | 10.23 MHz offset by "f = -4.5674E-3 Hz. This is equal to 10.2299999954326 MHz." | Hz / MHz | IS-GPS-200N, section 3.3.1.1 | factory setting | confirmed |
| 30 | Net daily offset from the factory offset | 38.58 | us/day | derived (D5) | check vs "about 38" | derived |
| 31 | Range error equal to the net daily offset | 11.39 km (38 us x c); 11.56 km (38.58 us x c) | km | derived (D6); NASA slide 27 says "~11 km" | error per day if uncorrected | derived |
| 32 | 1 microsecond as distance | 299.792458 m (about 300 m) | m | derived from row 1 (D7) | "1 us is about 300 m" | derived |
| 33 | Earth mean radius R1 | R1 = 6 371 008.7714 m "mean radius", R1 = (2a+b)/3. GRS 1980 adopted by IUGG, Canberra, Dec 1979, Resolution 7 | m | H. Moritz, "Geodetic Reference System 1980", section 1 Definition, <https://ciencias.ulisboa.pt/sites/default/files/fcul/dep/dqb/doc/GRS80_Moritz.pdf> | sphere model radius (6371.0088 km) | confirmed |
| 34 | Earth equatorial radius a (GRS 80) | 6378137 (semi-major axis) | m | same Moritz paper (value seen in search summary; not located in the extracted text) | ellipsoid, not used by the sphere model | unconfirmed |
| 35 | Orbit radius above the sphere | 20 188.7 km (26 559.7 - 6371.0088) | km | derived (D8) | sanity check vs 20,200 km | derived |

## Derived arithmetic

- D1 (row 6): T = 2 pi sqrt(a^3 / mu), a = 26 559 700 m, mu = 3.986005 x 10^14 m^3/s^2. T = 43 077.02 s = 11.9658 h = 11 h 57 min 57 s. NASA's "11 hours 58 minutes" agrees to the minute. Ratio to 86 164.0905 s is 0.49994 (uses the unconfirmed sidereal day, row 7).
- D2 (row 14): 1 / 1.023 x 10^6 Hz = 977.52 ns. 977.52 ns x 299 792 458 m/s = 293.05 m.
- D3 (row 22): 10 log10(k T) = 10 log10(1.380649 x 10^-23 x 290) = 10 log10(4.004 x 10^-21) = -203.975, about -204 dBW/Hz.
- D4 (rows 19, 23): B = 2 x 1.023 MHz = 2.046 MHz. 10 log10(k T B) = -203.975 + 10 log10(2.046 x 10^6) = -203.975 + 63.11 = -140.87 dBW. For B = 20.46 MHz: -203.975 + 73.11 = -130.87 dBW. Signal at -158.5 dBW is 17.6 dB below the 2.046 MHz noise (1 / 58) and 27.6 dB below the 20.46 MHz noise. All of this assumes T = 290 K and an ideal receiver; a real receiver adds noise, so it is a little worse.
- D5 (row 30): 4.4647 x 10^-10 x 86 400 s = 3.8575 x 10^-5 s = 38.575 us/day. Also 45 - 7 = 38 (rounded inputs). 10.23 x 10^6 x (1 - 4.4647 x 10^-10) = 10 229 999.9954326 Hz, matching row 29.
- D6 (row 31): 38 x 10^-6 s x 299 792 458 m/s = 11 392.1 m. 38.575 x 10^-6 s x 299 792 458 m/s = 11 564.6 m. Components: 7 us = 2 098.5 m, 45 us = 13 490.7 m.
- D7 (row 32): 1 x 10^-6 s x 299 792 458 m/s = 299.792458 m.
- D8 (row 35): 26 559.7 km - 6371.0088 km = 20 188.69 km. The 20,200 km altitude on gps.gov is "approximately".

## Notes and traps

- The spec says "about 38 microseconds a day". The exact IS-GPS-200 factory offset gives 38.58 us/day, which rounds to 39, not 38. NIST and NASA both say 38 (45 minus 7, rounded). Use "about 38" with the range figure "about 11 km"; do not print 38.0 as exact.
- IS-GPS-200 states the offset as 10.2299999954326 MHz. The shorter 10.22999999543 MHz is the same number cut after 11 decimals; both appear in popular sources.
- The IS-GPS-200 receive band is 20.46 MHz, not 2 MHz. The "about 2 MHz" noise figure is the C/A main lobe (2.046 MHz), our derivation, not a spec number.
- -158.5 dBW is a minimum for the whole satellite block at end of life, measured with a 3 dBi antenna at 5 degrees elevation. Many sources quote -160 dBW or -130 dBm for the same quantity; that is the older Block II figure, not what Revision N states.
- gps.gov's Space Segment page still shows the July 2023 count (31). The April 2026 Space Force slide says 32 and 7 more "residuals". Say which date you quote.
- gps.gov no longer serves the old /technical/icwg/ path (returns 404); the live PDF is under /sites/default/files/2025-07/.
- The NIST page date and the TU Delft slides were read from fetched pages; the Ashby review (Living Reviews in Relativity 2003) states these offsets only inside equations, so it was not used as a source.
