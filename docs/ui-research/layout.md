# Layout and hierarchy research

Purpose: ground the redesign of the GPS page (dark, Instrument Sans + JetBrains Mono, colour only for state) in sources. Target: feels as precise as Vercel's UI.
Known page problems: (P1) on 390x844 the first control is below the fold; (P2) uneven empty space inside cards; (P3) the "but/therefore" connective paragraphs compete with section headings; (P4) side-by-side cards do not align at the top.

Method note: the fetch tool returns a summary, not raw CSS. Where a source gave no number I say so. Items marked "inferred" are my reading, not source text. Nothing here is copied; examples are my own application.

## Fetch status

Fetched OK: vercel.com/design (brand guidelines page), /design/typography, /geist/colors, /geist/materials, /design/guidelines, vercel-labs web-interface-guidelines (raw `command.md`), lawsofux.com (index, Common Region, Fitts, Proximity, Hick), refactoringui.com (landing only), Linear "How we redesigned the Linear UI", Stripe "Accessible color systems", one web search for Refactoring UI summaries.
Fetched but no numbers: /geist/grid (no gutters or breakpoint px), /geist/button (no heights, radii or state values).
Could not get: Refactoring UI book text (paid; only chapter titles and one border tip seen; the rest comes from third-party summaries, treat as secondary). Geist spacing scale in px, grey hex values and button heights were not exposed. Not fetched: Stripe layout pages, Linear sidebar specifics beyond the one post, Laws of UX pages for Miller, Doherty, Von Restorff, Serial Position (index definitions only).

## 1. Vercel Geist and Vercel brand guidelines

### 1.1 Type scale and hierarchy
Sources: https://vercel.com/design/typography , https://vercel.com/design
- Geist type is named by role and size: Heading 72/64/56/48/40/32/24/20/16/14, Button 16/14/12, Label 20/18/16/14/13/12 (plus mono variants 12/13/14), Copy 24/20/18/16/14/13. The number is probably px (inferred; page does not say).
- Two rules matter more than the sizes: Label is for single lines, Copy has more leading for multiple lines. A "strong" variant is made by nesting `<strong>`, so emphasis is a weight shift inside one size, not a new size.
- Mono is a labelled variant at small sizes only (Label 12/13/14, Copy 13). The brand page says mono is for code, paths, timestamps, identifiers, and tabular numerals for comparisons; prose about 60-68 characters per line.
- Applies to us: use few steps. Suggested: section title 24 (Heading 24 analogue), card title 16 strong, body 14 on 1.55 leading, label 12-13 Instrument Sans, readouts and units in JetBrains Mono 12-13 with `font-variant-numeric: tabular-nums`. Measure cap about 62ch on the connective paragraphs. This addresses P3: the "but/therefore" paragraph should sit at body 14 in the secondary grey, with the heading carrying size and weight, so the ranking is never ambiguous.

### 1.2 Spacing scale
Source: https://vercel.com/design (brand-guidelines tokens `space-1,2,3,4,5,6,8,10,12,16`; px values not shown).
- Rule given: within a group use steps 2-4, between groups 6-8, between major sections 8-12, chapter breaks 16. If the token is n x 4px (inferred, standard for such scales) that is 8-16px inside groups, 24-32 between groups, 32-48 between sections, 64 for chapters.
- Applies to us: adopt a 4px base with tokens 4/8/12/16/24/32/48/64 and ban everything else. Proximity (section 5) says the gap inside a card must be clearly smaller than the gap between cards; set card padding 16 (mobile) / 20 (desktop), intra-card gap 12, inter-card gap 16-24, section gap 48. That directly cures P2: uneven space comes from ad hoc margins, so give every card the same padding and let content stack with one gap token (`display:grid; gap:12px`) rather than per-element margins.

### 1.3 Greys, borders and surfaces on dark
Source: https://vercel.com/geist/colors , https://vercel.com/design
- Geist's 10-step scale has fixed jobs: 100 default background, 200 hover background, 300 active background, 400 default border, 500 hover border, 600 active border, 700 high-contrast background, 800 its hover, 900 secondary text and icons, 1000 primary text and icons.
- Brand page groups the same idea as tokens: surface primary/secondary/contrast, text primary/secondary, border subtle/default/strong. "Design in monochrome, colour only for meaningful state, paired with a non-color cue."
- Applies to us: define one 10-step neutral ramp as CSS variables and give each step a single job. Page = 100, card = 200 (one step lighter, not a big jump), hover = 300, borders 400/500/600, secondary text 900, primary 1000. Colour stays reserved for state (valid, error, selected), and each state also gets a text or icon cue. The owner's "colour only for state" rule already matches Geist; the gain is the discipline of naming steps.
- Borders: 1px solid at the 400 step on cards; hover raises to 500. Because greys on dark are close together, one border step (not a shadow) is the separator. Source also says semi-transparent borders improve edge clarity when combined with shadows (/design/guidelines). We skip shadows and use a 1px border plus one surface step.

### 1.4 Radii and nesting
Sources: https://vercel.com/geist/materials , https://vercel.com/design/guidelines
- Surface materials: 6px radius (base/small), 12px (medium/large). Floating: tooltip 6, menu 12, modal 12, fullscreen 16. Child radius must be less than or equal to parent radius (concentric).
- Applies to us: cards 12px, controls and inputs 6px, chips 6px, nothing above 12 except modals. Inner element radius = outer radius minus padding, never larger.

### 1.5 Hover, press, focus
Sources: https://vercel.com/design/guidelines , https://vercel.com/geist/colors , https://vercel.com/geist/button
- Hover, active and focus must be more prominent than rest. Interactive grey roles (200 hover bg, 300 active bg; border 500 hover, 600 active) give a consistent ladder.
- Focus: `:focus-visible` ring, never removed without a replacement, never covered by sticky bars (relevant to our sticky mobile result bar, see 1.7).
- Touch: `touch-action: manipulation`; tap highlight set deliberately; hit area at least 24px desktop, 44px mobile.
- Buttons expose variants (default, secondary, tertiary, error, warning), sizes (tiny, small, medium, large) and `loading`/`disabled`. Heights not given by the page.
- Applies to us: one primary button style per view, secondary for the rest; states 100 -> 200 hover -> 300 pressed; transition 120-150ms on background and border only (my choice; not from source).

### 1.6 Alignment and grid
Sources: https://vercel.com/design , https://vercel.com/geist/grid , https://vercel.com/design/guidelines
- Brand grid: 12 columns desktop, 6 tablet, 4 mobile; layout primitives named section, grid, split, band, span-4..12. Geist Grid component gives no gutter numbers.
- Guidelines advise optical alignment of +-1px, flex/grid over JS measurement.
- Applies to us (P4): put side-by-side cards in a CSS grid with `align-items: stretch` and make each card a grid with the same row template (`auto 1fr auto`: title / body / footer), so title baselines match at the top and footers match at the bottom regardless of content. Use `grid-template-columns: repeat(2, minmax(0,1fr))` above ~720px and one column below. Use `minmax(0,1fr)` and `min-width:0` to stop long mono strings forcing uneven widths.

### 1.7 Density and mobile (mostly from the guidelines)
Source: https://vercel.com/design/guidelines , web-interface-guidelines raw file.
- Inputs at least 16px font to stop iOS zoom; do not disable zoom; respect safe-area insets; avoid autofocus on mobile; keep default overscroll on touch.
- Truncate or clamp long text; flex children need `min-w-0`; handle empty and very long values.
- Use `text-wrap: balance` on headings, `tabular-nums` for number columns.
- Applies to us (P1): the page needs the first interactive control inside the first 844px minus browser chrome (about 660-720px usable). Practical budget: top bar 48px, title 1 line at 24px, one-line lede at 14px, then the control. Cut the intro to the control. Make the live result a compact sticky bar (height 48-56px, `position: sticky; top:0` or bottom with `padding-bottom: env(safe-area-inset-bottom)`) showing 1-2 key numbers in mono, so control and result are visible together when the user scrubs. Check that sticky bars do not cover a focused input (guideline).

## 2. Refactoring UI (Wathan and Schoger)
Sources: https://www.refactoringui.com/ (chapter titles and the border tip only), secondary summaries via search (treat numbers as unverified). Book text not read.
- Chapters relevant: "Not all elements are equal", "De-emphasize to emphasize", "Labels are a last resort", "Separate visual hierarchy from document hierarchy", "Start with too much white space", "Establish a spacing and sizing system", "You don't have to fill the whole screen", "Avoid ambiguous spacing", "Balance weight and contrast".
- Border tip on the landing page: use shadow, contrasting background or extra space instead of a border. Applies to us: inside a card, separate the readout from the control with spacing or a 100 vs 200 surface step instead of a second 1px line; keep borders only on the card edge. This reduces line noise and aids P2.
- Hierarchy: rank by size, weight and colour together; de-emphasise secondary things (lighter or smaller, not thinner weight, per summaries) so the primary stands out. Applies to P3: the connective paragraph is secondary, so grey 900 and 14px, while section heading is 1000 and 24px. The heading should be an `<h2>` visually bigger than any paragraph; if the connective text must read first, make it the visible lede and demote the heading instead of letting both shout.
- "Labels are a last resort": show "12.4 m" with a small unit, not a label plus a value in every row. Applies to readouts: put the quantity name in a 12px grey caption above a 16-20px mono number, only once per group.
- "Start with too much white space, then remove". Applies to us: set the card padding at 20 then tighten.
- Line height inversely related to size (summaries: headings about 1.2, body about 1.5-1.6). Applies: 24px heading at 1.2, 14px body at 1.55.
- "You don't have to fill the whole screen": cap content width (about 880-960px) and centre it; do not stretch cards across wide monitors.

## 3. Laws of UX
Sources: https://lawsofux.com/ , /law-of-common-region/ , /fittss-law/ , /law-of-proximity/ , /hicks-law/
- Proximity: nearby items read as related. Example: label, number and unit within 4-8px; the next group 24px away. Fixes P2 by rule rather than taste.
- Common Region: a bounded area (border or background) groups content. Example: one card per concept; do not nest a second bordered box inside it, use a surface step.
- Fitts: bigger and closer targets are faster, spacing between touch targets reduces mis-taps. Example: sliders and toggles on mobile at 44px minimum height with 8px or more gap; place the main control near the result so thumb travel is short (P1).
- Hick: more choices, slower decisions; mark a recommended option. Example: show one control per step and put advanced ones behind a disclosure; default one preset as selected.
- Index also lists Miller (about 7 items), Von Restorff (the odd one out is remembered), Serial Position (first and last remembered), Doherty (respond under about 400ms). Example: the only coloured element in a view should be the thing that changed state; update readouts within one frame of input.
- Laws are heuristics from definitions only; I did not read their studies.

## 4. Linear (quality: hierarchy through contrast and alignment on dark/light themes)
Source: https://linear.app/now/how-we-redesigned-the-linear-ui
- Raised contrast overall; reduced visual noise so navigation and content rank clearly; aligned labels, icons and buttons on both axes. Headings use a display cut of the font, body the regular cut. Theme built from base colour, accent and contrast variables in LCH so equal lightness looks equal.
- Quality we borrow: chrome recedes, content leads. Applies to us: keep greys neutral (little tint), keep icon and label on one shared baseline and left edge, and let a single contrast variable raise text steps if readability tests fail. Instrument Sans at larger sizes plays the "display" role; JetBrains Mono stays for data.
- Not fetched: Linear's actual px values for density; the post gives none.

## 5. Stripe (quality: systematic accessible colour and contrast steps)
Source: https://stripe.com/blog/accessible-color-systems
- Colour scales are built in a perceptually uniform space so each hue has the same lightness curve; any two levels 5 apart pass 4.5:1 for small text, 4 apart for icons and large text. Badges stay legible by moving background and text one level together.
- Applies to us: our state colours (valid, warning, error) should be picked at matching lightness, so one status never shouts louder than another. Check text on state backgrounds against 4.5:1; use numerical contrast checks, not eyeballing. Pair a tinted badge background with text 4-5 steps away on the same ramp.
- Not fetched: Stripe layout and spacing guidance; I make no layout claim from Stripe.

## 6. Cross-source decisions for the redesign
1. Tokens: 4px spacing base, 10-step neutral ramp with fixed roles, radii 6/12, type roles with 5 sizes max (12, 14, 16, 24, plus one display at 32-40 for the page title).
2. P1: first control within about 600px on a 390x844 phone; sticky compact result bar 48-56px with safe-area padding; 44px touch targets; inputs 16px.
3. P2: one padding and one gap token per card; card rows use `auto 1fr auto`; no ad hoc margins.
4. P3: connective paragraph = secondary grey 14px lede under the heading; heading = primary grey, larger, weight 600; never two competing bold lines.
5. P4: grid with `align-items: stretch`, shared row template across sibling cards, `minmax(0,1fr)` columns.
6. States: hover +1 ramp step, pressed +2, border +1 on hover, visible `:focus-visible` ring, 120-150ms transition.
7. Verification still needed (not done here): real px for Geist spacing and buttons, and pass-rate of our greys against 4.5:1. Measure on the page, do not copy Vercel's numbers.
