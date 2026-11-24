# Visual polish (issue #68)

Small changes against `docs/ui-guide.md` and `web/theme.css`. No new colours, fonts, radii or wording. Screenshots are in `docs/ux-audit/polish/`, same state and width before and after.

| # | What | Why | Rule | Before | After |
|---|---|---|---|---|---|
| 1 | "but / therefore" lines are 18 px (was 20 px) and muted, bold words stay full colour; 32 px above each step section. The decided 16 px with a 60ch cap was tried and dropped: it makes WebKit report no first paint while the CDN is slow, which fails `test_speed.py` | Section headings and link lines were both 20 px, so nothing led the eye | ui-guide 1.3, 1.4 | [01](polish/01-hierarchy-1200-before.png) | [01](polish/01-hierarchy-1200-after.png) |
| 2 | Relativity card uses the standard card padding (24 px, was 16 px) | The slider block sat 16 px inside two outlines; geometry and signal sit 24 px in | ui-guide 2 | [02](polish/02-relativity-slider-1200-before.png) | [02](polish/02-relativity-slider-1200-after.png) |
| 3 | Card labels (`h2.label`, `h3.label`) get 12 px below | "GROUND MAP" touched the map frame at 390 px | ui-guide 4 | [03](polish/03-map-label-390-before.png) | [03](polish/03-map-label-390-after.png) |
| 4 | Empty message lines take no room, except lines with a control below them (they keep 1.5em) | Empty lines left gaps that looked like missing content; the kept ones stop controls moving when words appear | ui-guide 3 | [04](polish/04-empty-messages-390-before.png) | [04](polish/04-empty-messages-390-after.png) |
| 5 | One metres rule in `web/format.js`: one decimal below 100 m, whole metres from 100 m, thousands separator | Readouts mixed "1,561 m", "520.3 m" and "0 m" | ui-guide 1.7 | [05](polish/05-geometry-readout-1200-before.png), [05](polish/05-first-error-1200-before.png) | [05](polish/05-geometry-readout-1200-after.png), [05](polish/05-first-error-1200-after.png) |
| 6 | Alignment check at 1200 px: no change needed | Left and right cards start at the same top edge in all three sections | | measured | measured |
