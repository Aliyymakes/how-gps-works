# State log, plan 004

Live link: https://aliyymakes.github.io/how-gps-works/

- 2026-11-24 17:00 | start | Session began plan-004 from item 1 (Fable main session). Inbox read: latest note is 2026-11-23 23:35, nothing new for this plan. No open pull requests; open issue #47 only.
- 2026-11-24 17:05 | browser | `python3 -m http.server 8000` REFUSED by the permission check (tried once, not retried). Playwright from `.venv` works against the live site in Chromium and WebKit. Branch testing without a server also works: a Playwright `page.route()` handler answers the live URL's requests from the working tree and lets the Pyodide CDN through. So branches are checked in real browsers before merge.
- 2026-11-24 17:10 | item 1 | First measurement, cold cache, headless, live site at 1200 px: controls stay off for 32.5 s in Chromium and 44.8 s in WebKit after opening the page. Three of the four sections show only "Loading the maths…" for all of it.
- 2026-11-24 18:05 | item 1 | Audit run: Chromium and WebKit, 1200 and 390 px, mouse, touch emulation, keyboard, slow network, Pyodide blocked, one Python file missing. Cold load 9.7 to 44.8 s (about 9 MB), warm 2.4 to 3.0 s; interactions freeze at most 68 ms; start-up freezes 1.1 s once. 6 blocking, 14 confusing, 6 polish findings in docs/ux-audit.md on #54/54-ux-audit. Main bugs: stale map lines and wrong refusal words with fewer than 3 satellites, invisible solve mode, three sections never show load progress, no map legend.
- 2026-11-24 18:20 | item 1 | Haiku reviewer on PR #55: links, causes in B2/B4, C11 and diff scope PASS; B5 wording was unclear about which mode shows which sentence, fixed.
