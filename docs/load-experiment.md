# Load experiment: Pyodide on GitHub Pages instead of jsDelivr

Issue #79, plan 005 item 7. This branch is an experiment and is not meant to be merged.
Question: would hosting the Pyodide files in this repo (served by GitHub Pages) make cold loads faster than jsDelivr?

Short answer: **this experiment cannot show that it would.** The only honest end-to-end number for the branch is a local lower bound (about 2.2 to 2.4 s) that has no network in it. The one real measurement of GitHub Pages speed from this machine (below) says Pages is much slower than jsDelivr for the same bytes. Nothing here supports merging.

## What the page fetches from jsDelivr

Found by a Playwright network log against the live site (`https://cdn.jsdelivr.net/pyodide/v314.0.8/full/`):

| File | Size (decoded) | jsDelivr on the wire (brotli) |
|---|---|---|
| pyodide.asm.wasm | 9 597 892 | 3 439 687 |
| numpy-2.4.6-cp314-cp314-pyemscripten_2026_0_wasm32.whl | 2 960 568 | 2 929 885 |
| python_stdlib.zip | 2 545 550 | 2 505 155 |
| pyodide.asm.mjs | 1 250 259 | 262 080 |
| pyodide-lock.json | 119 077 | 24 708 |
| pyodide.mjs | 17 758 | 7 220 |
| Total | 16 491 104 (16.5 MB) | 9 168 735 (9.2 MB) |

Branch change: the six files are copied unchanged into `vendor/pyodide/v314.0.8/full/`; `web/bridge.js` (`PYODIDE_BASE`) and the `modulepreload` link in `index.html` point there; the jsDelivr `preconnect` is removed.

Repo size cost: 16.5 MB more in the working tree and about 9.3 MiB (9.8 MB) more in git (measured: loose objects grew from 2.76 to 12.10 MiB after `git add`). Every clone pays it for ever, and a Pyodide upgrade adds another copy to history.

## Method

Script: Playwright (Python), a fresh browser context per visit, no cache. Time runs from `page.goto(..., wait_until="commit")` to the `#solve` button becoming enabled (polled every 50 ms). 10 visits per setup per browser, the three setups interleaved in each round so slow network periods hit all of them.

Setups:

- **A. live (jsDelivr):** the real site, `https://aliyymakes.github.io/how-gps-works/`, Pyodide from jsDelivr. Measures: this machine's real network to GitHub Pages plus jsDelivr.
- **B. local-main (control):** the page files of `origin/main` answered from disk by `page.route()`, Pyodide still really fetched from jsDelivr. Measures: jsDelivr only (the page files cost about nothing). It shows how much the network alone moves the number.
- **C. local-branch:** this branch's files, including the Pyodide files, all answered from disk by `page.route()`. Measures: **a lower bound with zero network** (disk read, no compression, no latency). It is what an infinitely fast host would give. It is not what GitHub Pages would give.

## Cold load times (seconds, navigation to solve button enabled, n = 10 each)

| Browser | Setup | Median | Min | Max |
|---|---|---|---|---|
| Chromium | A live (jsDelivr) | 5.20 | 3.99 | 18.96 |
| Chromium | B local-main (jsDelivr only) | 5.43 | 3.51 | 28.91 |
| Chromium | C local-branch (no network) | 2.42 | 2.28 | 2.58 |
| WebKit | A live (jsDelivr) | 35.33 | 4.96 | 50.42 |
| WebKit | B local-main (jsDelivr only) | 19.08 | 4.98 | 54.19 |
| WebKit | C local-branch (no network) | 2.21 | 2.13 | 2.44 |

Raw values (visit 1 to 10):

- Chromium A: 8.12, 4.56, 4.32, 5.24, 3.99, 5.16, 18.96, 17.99, 11.73, 5.11
- Chromium B: 4.92, 3.51, 4.66, 3.60, 3.70, 5.93, 25.33, 22.69, 28.91, 26.55
- Chromium C: 2.55, 2.39, 2.30, 2.35, 2.55, 2.58, 2.45, 2.35, 2.54, 2.28
- WebKit A: 35.41, 35.26, 39.27, 50.42, 4.96, 46.91, 39.25, 6.77, 6.14, 5.72
- WebKit B: 31.17, 6.99, 33.97, 44.59, 54.19, 46.65, 4.98, 5.58, 5.19, 5.73
- WebKit C: 2.39, 2.20, 2.28, 2.20, 2.44, 2.22, 2.24, 2.16, 2.13, 2.15

What this tells us:

- jsDelivr loads are bimodal. About 4 to 6 s when the connection is good, 18 to 54 s during slow periods (Chromium visits 7 to 10, WebKit visits 1 to 7). The slow periods hit setup B as well as A, so they come from the Pyodide download (or this machine's connection), not from the page files on GitHub Pages.
- Setup C is flat at about 2.2 to 2.4 s: that is the fixed cost of starting Pyodide and numpy with the bytes already in hand. So the most any host change could save is the gap between a host's download time and zero, and the download is 9.2 MB.
- Setup C does **not** say self-hosting is faster. It says nothing about GitHub Pages.

## Real GitHub Pages speed versus jsDelivr (same bytes, same machine)

We could not deploy the branch (no push to main, no Pages changes), so Pyodide cannot be fetched from Pages. As a substitute, three PNGs that are already served from Pages (`docs/ux-audit/01-ready-1200.png`, `02-ready-390-webkit.png`, `04-offline-390.png`, 303, 331 and 237 KB) were fetched from Pages and, byte for byte the same files, from jsDelivr's GitHub mirror (`cdn.jsdelivr.net/gh/Aliyymakes/how-gps-works@main/...`). Chromium `fetch` with `cache: 'no-store'`, one warm-up fetch discarded, 10 rounds, 30 fetches per host, all HTTP 200:

| Host | Median ms | Min | Max | Median time to first byte (ms) | Median throughput (MB/s) |
|---|---|---|---|---|---|
| GitHub Pages | 1613 | 459 | 4536 | 94 | 0.18 |
| jsDelivr (gh mirror) | 190 | 108 | 777 | 52 | 1.52 |

For comparison, jsDelivr's own Pyodide files in the same page (5 fetches each, median): `pyodide.asm.wasm` 9.6 MB decoded (3.4 MB brotli) 2.3 s; `python_stdlib.zip` 2.5 MB 2.1 s; numpy wheel 2.96 MB 1.7 s. That is roughly 1.2 to 1.8 MB/s on the wire.

What this tells us, and what it cannot:

- Pages was about 8 times slower than jsDelivr per 300 KB file from this machine (about 0.18 MB/s against about 1.5 MB/s). If that rate held for 9.2 MB it would be about 50 s. It will not hold exactly: 300 KB files are dominated by connection start-up (TCP slow start), so the per-byte rate for a long transfer would be better than this. Treat 0.18 MB/s as a pessimistic bound, not a forecast.
- It is one machine, one network, one region (the GitHub edge answered from Southeast Asia in a header check). A visitor elsewhere may see a different ratio.
- PNGs are already compressed, so wire bytes equal file bytes here. This test does not check compression.
- `@main` on jsDelivr's mirror can lag the repo by hours; only files present in both places were used.

## Compression on Pages (not verified)

jsDelivr serves the wasm, stdlib and numpy files brotli-compressed (9.2 MB total). We did not find out whether GitHub Pages compresses `.wasm`, `.zip` and `.whl` files. Pages did gzip `index.html`. A public `.wasm` on github.io that we checked (102 bytes) was too small to show anything. If Pages sends them uncompressed, the branch would download the full 16.5 MB (7.3 MB more than now); if it gzips them, about 9.3 MB, the same as now. Only a real deployment can settle this.

## Other things that change if this were merged

- `tests/ui/conftest.py` routes `https://cdn.jsdelivr.net/**` to a cache; this branch does not touch tests, and the UI tests were not run on it. They would need changing.
- Pages sends `cache-control: max-age=600`, so a repeat visit after 10 minutes revalidates the big files. jsDelivr's caching headers for versioned paths are much longer.
- Pyodide would no longer be a "pinned CDN address" in `bridge.js` and `index.html` but a vendored copy to keep in step by hand.
- The 1 GB soft limit for Pages sites and the repo size growth are small here (9.3 MiB), but not zero.

## What would settle it

Deploy the branch to a throwaway Pages site (a second repo or a branch deployment), then run the same script against that URL, 10 visits, both browsers. That was out of bounds here.
