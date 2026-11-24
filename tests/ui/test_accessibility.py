"""Issue #66: accessibility pass. Every test runs in Chromium and WebKit (see conftest.py),
at a phone width (390) and a desktop width (1200). The zoom test uses 195 px, which is
what a 390 px phone shows at 200 % zoom.
"""
import pytest

WIDTHS = [390, 1200]
CLOCK = "#clock"
GEO_SLIDER = "#step-geometry [data-id=slider]"
NOISE = "#step-signal [data-el=noise]"
REL_SLIDER = "#rel-hours"
SLIDERS = [CLOCK, GEO_SLIDER, NOISE, REL_SLIDER]
RESETS = ["#reset", "#step-geometry [data-id=reset]", "#step-signal [data-el=reset]", "#step-relativity [data-id=reset]"]
CONTROLS = "input, button, select, textarea, a[href]"

# Shared helpers, written once in the page: colours, backgrounds, contrast ratio, visibility.
JS_HELPERS = """
const parseColour = (text) => {
  const hex = /^#([0-9a-f]{6})$/i.exec(text.trim());
  if (hex) return [0, 2, 4].map((i) => parseInt(hex[1].slice(i, i + 2), 16)).concat([1]);
  const m = /^(rgba?|color)\\(([^)]*)\\)/.exec(text.trim());
  if (!m) return [0, 0, 0, 0];
  const parts = m[2].replace("srgb", "").split(/[\\s,\\/]+/).filter(Boolean).map(Number);
  if (m[1] === "color") return [parts[0] * 255, parts[1] * 255, parts[2] * 255, parts.length > 3 ? parts[3] : 1];
  return [parts[0], parts[1], parts[2], parts.length > 3 ? parts[3] : 1];
};
const over = (top, bottom) => {
  const a = top[3];
  return [0, 1, 2].map((i) => top[i] * a + bottom[i] * (1 - a)).concat([1]);
};
const backdrop = (node) => {
  const chain = [];
  for (let n = node; n; n = n.parentElement) {
    const c = parseColour(getComputedStyle(n).backgroundColor);
    if (c[3] > 0) { chain.push(c); if (c[3] >= 1) break; }
  }
  let base = [255, 255, 255, 1];
  for (const c of chain.reverse()) base = over(c, base);
  return base;
};
const opacityOf = (node) => {
  let o = 1;
  for (let n = node; n; n = n.parentElement) o *= Number(getComputedStyle(n).opacity);
  return o;
};
const luminance = ([r, g, b]) => {
  const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
  return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
};
const ratio = (a, b) => {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
};
const shown = (node) => {
  if (!node.getClientRects().length) return false;
  for (let n = node; n && n.nodeType === 1; n = n.parentElement) {
    const s = getComputedStyle(n);
    if (s.display === "none" || s.visibility === "hidden") return false;
  }
  return true;
};
const nameOf = (node) => (node.id ? "#" + node.id : (node.dataset.id || node.dataset.el) ? "[" + (node.dataset.id || node.dataset.el) + "]" : node.tagName.toLowerCase() + "." + String(node.getAttribute("class") || "").split(" ")[0]);
"""


def run(page, body, arg=None):
    """Run JS with the shared helpers. `body` is the text of a function body that may use them."""
    return page.evaluate("(arg) => {" + JS_HELPERS + body + "}", arg)


def report(problems):
    """Fail with every problem on its own line."""
    if problems:
        pytest.fail("\n".join(sorted(set(problems))), pytrace=False)


def settle(page):
    page.wait_for_timeout(500)  # Python answers, then the next frame draws


def set_slider(page, selector, value):
    page.locator(selector).fill(str(value))
    settle(page)


def slider_max(page, selector):
    return int(page.locator(selector).get_attribute("max"))


def press_next(page, browser):
    # In WebKit, Tab skips controls unless Alt is held.
    page.keyboard.press("Alt+Tab" if browser.browser_type.name == "webkit" else "Tab")


# 1. Labels and slider values
@pytest.mark.parametrize("width", WIDTHS)
def test_every_control_has_a_name_and_every_slider_a_valuetext(open_page, width):
    page = open_page(width).page
    missing = run(page, """
      const out = [];
      for (const c of document.querySelectorAll('input, button, select, textarea')) {
        const labelled = c.getAttribute('aria-label') || c.getAttribute('aria-labelledby')
          || [...(c.labels || [])].some((l) => l.textContent.trim()) || (c.tagName === 'BUTTON' && c.textContent.trim());
        if (!labelled) out.push(nameOf(c));
      }
      return out;
    """)
    assert missing == [], f"controls without an accessible name: {missing}"
    for selector in SLIDERS:
        slider = page.locator(selector)
        before = slider.get_attribute("aria-valuetext")
        assert before, f"{selector} has no aria-valuetext"
        set_slider(page, selector, slider_max(page, selector) // 2)
        after = slider.get_attribute("aria-valuetext")
        assert after != before, f"{selector}: aria-valuetext did not follow the slider"
        assert any(unit in after for unit in ("µs", "%", "×", "times", "h", "hour")), f"{selector}: no unit in '{after}'"


# 2. Target size
@pytest.mark.parametrize("width", WIDTHS)
def test_every_control_is_at_least_44_by_44(open_page, width):
    page = open_page(width).page
    small = run(page, """
      const out = [];
      for (const c of document.querySelectorAll('button, input[type=range], label.toggle')) {
        const r = c.getBoundingClientRect();
        if (r.width < 44 || r.height < 44) out.push(nameOf(c) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
      }
      return out;
    """)
    assert small == [], f"boxes under 44 x 44 px: {small}"


# 3. Keyboard
@pytest.mark.parametrize("width", WIDTHS)
def test_tab_visits_every_control_once_in_reading_order_with_a_focus_ring(open_page, browser, width):
    page = open_page(width).page
    expected = run(page, """
      const out = [];
      for (const c of document.querySelectorAll('input, button, select, textarea, a[href]')) {
        if (c.disabled) continue;
        const box = (c.type === 'checkbox' ? c.closest('label') : c).getBoundingClientRect();
        out.push({ name: nameOf(c) + (c.type === 'checkbox' ? ' ' + c.closest('label').textContent.trim() : ''), top: box.top + scrollY, left: box.left });
      }
      return out;
    """)
    assert len(expected) == 15  # 5 sliders, 1 solve button, 4 switches, 4 reset buttons, 1 search button
    for a, b in zip(expected, expected[1:]):
        same_row = abs(a["top"] - b["top"]) <= 2
        next_column = b["left"] > a["left"] + 100  # the signal section's left card comes before its right card
        assert (same_row and b["left"] >= a["left"]) or b["top"] > a["top"] or next_column, f"DOM order is not reading order: {a['name']} then {b['name']}"
    page.evaluate("document.activeElement && document.activeElement.blur(); window.scrollTo(0, 0)")
    visited = []
    problems = []
    for _ in expected:
        press_next(page, browser)
        info = run(page, """
          const a = document.activeElement;
          const ring = a.type === 'checkbox' ? a.nextElementSibling : a;
          return { name: nameOf(a) + (a.type === 'checkbox' ? ' ' + a.closest('label').textContent.trim() : ''),
                   outline: getComputedStyle(ring).outlineStyle };
        """)
        visited.append(info["name"])
        if info["outline"] == "none":
            problems.append(info["name"])
    assert visited == [e["name"] for e in expected], "Tab did not visit each control once, in reading order"
    assert problems == [], f"no visible focus indicator on: {problems}"


@pytest.mark.parametrize("width", WIDTHS)
def test_every_control_works_from_the_keyboard(open_page, width):
    page = open_page(width).page
    for selector in SLIDERS:
        slider = page.locator(selector)
        slider.focus()
        before = slider.input_value()
        step = -1 if before == slider.get_attribute("max") else 1  # the relativity slider starts at its maximum
        page.keyboard.press("ArrowLeft" if step < 0 else "ArrowRight")
        settle(page)
        assert int(slider.input_value()) == int(before) + step, f"{selector}: arrow key did not move the slider"
    boxes = page.locator("#switches input")
    for key in ("Space", "Space"):
        was = boxes.first.is_checked()
        boxes.first.focus()
        page.keyboard.press(key)
        settle(page)
        assert boxes.first.is_checked() != was, "Space did not flip the switch"
    solve = page.locator("#solve")
    for key in ("Enter", "Space"):
        set_slider(page, CLOCK, 5)  # moving the slider goes back to trusting the clock
        assert solve.get_attribute("aria-pressed") == "false"
        solve.focus()
        page.keyboard.press(key)
        settle(page)
        assert solve.get_attribute("aria-pressed") == "true", f"{key} did not press the solve button"
    for reset, slider in zip(RESETS, SLIDERS):
        for key in ("Enter", "Space"):
            set_slider(page, slider, 7)
            page.locator(reset).focus()
            page.keyboard.press(key)
            settle(page)
            start = "24" if slider == REL_SLIDER else "0"  # the relativity slider starts at one day
            assert page.locator(slider).input_value() == start, f"{key} did not press {reset}"


# 4. Contrast
CONTRAST_TEXT = """
  const out = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const t = walker.currentNode;
    const words = t.textContent.trim();
    const el = t.parentElement;
    if (!words || ['SCRIPT', 'STYLE', 'NOSCRIPT'].includes(el.tagName) || !shown(el)) continue;
    const s = getComputedStyle(el);
    const svg = el.closest('svg') !== null;
    const fg = parseColour(svg ? s.fill : s.color);
    const o = opacityOf(el);
    if (o === 0) continue;
    const bg = backdrop(el);
    const mixed = over([fg[0], fg[1], fg[2], fg[3] * o], bg);
    const size = parseFloat(s.fontSize);
    const large = size >= 24 || (size >= 18.66 && Number(s.fontWeight) >= 700);
    const need = large ? 3 : 4.5;
    const got = ratio(mixed, bg);
    if (got < need) out.push(nameOf(el) + ' "' + words.slice(0, 30) + '" text ' + mixed.map(Math.round).slice(0, 3) + ' on ' + bg.map(Math.round).slice(0, 3) + ' = ' + got.toFixed(2) + ':1 (needs ' + need + ')');
  }
  return out;
"""

CONTRAST_MARKS = """
  const marks = [
    ['map line', '#map-lines polyline', 'stroke'], ['map true cross', '#map-true line, .map-true path', 'stroke'],
    ['map dot', '#map-dot circle', 'stroke'], ['sky dot', '.sky-sat', 'fill'],
    ['signal received line', '.signal-step .received', 'stroke'], ['signal score line', '.signal-step .scores', 'stroke'],
    ['signal true-delay mark', '.signal-step .mark-true', 'stroke'], ['signal best mark', '.signal-step .mark-best', 'stroke'],
  ];
  const out = [];
  const check = (label, node, fg) => {
    const bg = backdrop(node);
    const got = ratio(over(fg, bg), bg);
    if (got < 3) out.push(label + ' ' + fg.map(Math.round).slice(0, 3) + ' on ' + bg.map(Math.round).slice(0, 3) + ' = ' + got.toFixed(2) + ':1 (needs 3)');
  };
  for (const [label, selector, prop] of marks) {
    for (const node of document.querySelectorAll(selector)) {
      if (!shown(node) || node.classList.contains('is-hidden') || node.classList.contains('is-off')) continue;
      const o = opacityOf(node);
      if (o < 0.5) continue;
      const c = parseColour(getComputedStyle(node)[prop]);
      c[3] *= o;
      check(label, node, c);
    }
  }
  // Slider track: browsers do not report a pseudo-element's colour, so read the last style rule for it.
  let trackRule = null;
  for (const sheet of document.styleSheets) {
    let rules = [];
    try { rules = sheet.cssRules; } catch (error) { continue; } // the fonts stylesheet is from another site
    for (const rule of rules) {
      if (rule.selectorText && rule.selectorText.includes('slider-runnable-track')) trackRule = rule;
    }
  }
  for (const slider of document.querySelectorAll('input[type=range]')) {
    let value = trackRule.style.getPropertyValue('background-color') || trackRule.style.getPropertyValue('background');
    const named = /var\\((--[\\w-]+)\\)/.exec(value);
    if (named) value = getComputedStyle(slider).getPropertyValue(named[1]);
    check('slider track ' + nameOf(slider), slider, parseColour(value.trim()));
  }
  // Toggle track: its fill, or its edge ring if it has one.
  for (const box of document.querySelectorAll('.toggle input:not(:checked) + .toggle-track')) {
    const s = getComputedStyle(box);
    const ring = /rgba?\\([^)]*\\)/.exec(s.boxShadow);
    const bg = backdrop(box.parentElement);
    const fill = over(parseColour(s.backgroundColor), bg);
    const edge = ring ? over(parseColour(ring[0]), bg) : fill;
    const got = Math.max(ratio(fill, bg), ratio(edge, bg));
    if (got < 3) out.push('toggle track (off) = ' + got.toFixed(2) + ':1 (needs 3)');
  }
  return out;
"""


def stress_the_page(page):
    """Push every control so the warn and bad colours and the refusal sentences are on screen."""
    set_slider(page, CLOCK, slider_max(page, CLOCK))
    set_slider(page, GEO_SLIDER, slider_max(page, GEO_SLIDER))
    set_slider(page, NOISE, slider_max(page, NOISE))
    page.locator("#switches label").nth(0).click()
    settle(page)


@pytest.mark.parametrize("width", WIDTHS)
def test_text_contrast(open_page, width):
    page = open_page(width).page
    failures = run(page, CONTRAST_TEXT)
    stress_the_page(page)
    failures += run(page, CONTRAST_TEXT)
    report(failures)


@pytest.mark.parametrize("width", WIDTHS)
def test_meaningful_marks_have_3_to_1_contrast(open_page, width):
    page = open_page(width).page
    # Switch one satellite off first so the "off" toggle track exists.
    page.locator("#switches label").nth(1).click()
    settle(page)
    failures = run(page, CONTRAST_MARKS)
    set_slider(page, CLOCK, slider_max(page, CLOCK))
    set_slider(page, NOISE, slider_max(page, NOISE))
    failures += run(page, CONTRAST_MARKS)
    report(failures)


# 5. Colour is never the only signal
@pytest.mark.parametrize("width", WIDTHS)
def test_every_coloured_state_has_words_beside_it(open_page, width):
    page = open_page(width).page
    check = """
      const out = [];
      for (const node of document.querySelectorAll('.is-ok, .is-warn, .is-bad')) {
        if (!shown(node) || node.classList.contains('badge')) continue;
        const part = node.closest('.grid, .geo-grid, .rel');
        const badges = [...part.querySelectorAll('.badge')].filter((b) => shown(b) && b.textContent.trim());
        if (!badges.length) out.push(nameOf(node) + ' has no badge with words in its section');
      }
      return out;
    """
    problems = run(page, check)
    set_slider(page, CLOCK, slider_max(page, CLOCK))
    set_slider(page, NOISE, slider_max(page, NOISE))
    problems += run(page, check)
    assert problems == [], problems


# 6. Reduced motion
@pytest.mark.parametrize("width", WIDTHS)
def test_reduced_motion_removes_movement(open_page, width):
    page = open_page(width).page
    page.emulate_media(reduced_motion="reduce")
    page.evaluate("""() => {
      window.__moving = [];
      window.__watch = true;
      const look = () => {
        for (const a of document.getAnimations()) {
          const props = a.transitionProperty ? [a.transitionProperty]
            : (a.effect ? a.effect.getKeyframes().flatMap((k) => Object.keys(k)) : []);
          for (const p of props) if (/transform|translate|scale|rotate/.test(p)) window.__moving.push(p + ' on ' + (a.effect && a.effect.target ? a.effect.target.tagName + '.' + a.effect.target.className : '?') + ' ' + (a.effect && a.effect.pseudoElement || ''));
        }
        if (window.__watch) requestAnimationFrame(look);
      };
      look();
    }""")
    for selector in SLIDERS:
        page.locator(selector).focus()
        page.keyboard.press("ArrowRight")
        page.mouse.move(*[page.locator(selector).bounding_box()[k] + page.locator(selector).bounding_box()[d] / 2 for k, d in (("x", "width"), ("y", "height"))])
        page.mouse.down()
        page.wait_for_timeout(300)
        page.mouse.up()
    page.locator("#switches label").nth(0).click()
    page.wait_for_timeout(400)
    page.locator("#switches label").nth(0).click()
    page.wait_for_timeout(400)
    for button in ["#solve"] + RESETS:
        box = page.locator(button).bounding_box()
        page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        page.mouse.down()
        page.wait_for_timeout(300)
        pressed = page.locator(button).evaluate("n => getComputedStyle(n).transform")
        page.mouse.up()
        assert pressed == "none", f"{button} still scales when pressed: {pressed}"
        page.wait_for_timeout(300)
    moving = page.evaluate("() => { window.__watch = false; return [...new Set(window.__moving)]; }")
    assert moving == [], f"movement animates under reduced motion: {moving}"


# 7. Screen reader text
@pytest.mark.parametrize("width", WIDTHS)
def test_drawings_have_labels_that_follow_the_picture(open_page, width):
    page = open_page(width).page
    unlabelled = run(page, """
      return [...document.querySelectorAll('svg:not([aria-hidden=true])')].filter((s) => s.getAttribute('role') !== 'img' || !(s.getAttribute('aria-label') || '').trim()).map((s) => nameOf(s));
    """)
    assert unlabelled == [], f"drawings without role=img and aria-label: {unlabelled}"
    labels = {
        "#map": (CLOCK, "#map"),
        "sky": (GEO_SLIDER, "#step-geometry svg"),
        "received": (NOISE, "#step-signal [data-el=rows]"),
        "scores": (NOISE, "#step-signal [data-el=scores-plot]"),
    }
    for name, (slider, svg) in labels.items():
        if name == "scores":
            page.locator("#step-signal [data-el=search]").click()
            settle(page)
        before = page.locator(svg).get_attribute("aria-label")
        half = slider_max(page, slider) // 2
        # The score graph's words only change when the best match moves, which takes a lot of noise.
        target = slider_max(page, slider) if name == "scores" else half
        set_slider(page, slider, target if page.locator(slider).input_value() != str(target) else target - 1)
        after = page.locator(svg).get_attribute("aria-label")
        assert after != before, f"{name}: aria-label did not change with its picture"
    map_label = page.locator("#map").get_attribute("aria-label")
    assert map_label.startswith("Ground map. 4 distance lines."), map_label
    assert "Position off by" in map_label
    page.locator("#switches label").nth(0).click()
    page.locator("#switches label").nth(1).click()
    settle(page)
    assert "no position" in page.locator("#map").get_attribute("aria-label").lower()


@pytest.mark.parametrize("width", WIDTHS)
def test_messages_are_announced_and_headings_do_not_skip(open_page, width):
    page = open_page(width).page
    silent = run(page, """
      const wanted = '[role=status], #status, #map-caption, [id^=msg-], [data-id^=msg], [data-el^=msg], [data-id=status], [data-el=status], [data-el=sentence]';
      return [...document.querySelectorAll(wanted)].filter((n) => n.getAttribute('aria-live') !== 'polite').map(nameOf);
    """)
    assert silent == [], f"messages without aria-live=polite: {silent}"
    levels = page.evaluate("[...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map((h) => Number(h.tagName[1]))")
    assert levels[0] == 1
    for before, after in zip(levels, levels[1:]):
        assert after <= before + 1, f"heading levels skip: {levels}"


# 8. Zoom: 200 % on a 390 px phone is a 195 px wide screen
def test_nothing_is_cut_off_at_200_percent_zoom(open_page):
    page = open_page(195).page
    problems = run(page, """
      const out = [];
      const view = document.documentElement;
      if (view.scrollWidth > view.clientWidth) out.push('page scrolls sideways: ' + view.scrollWidth + ' > ' + view.clientWidth);
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      while (walker.nextNode()) {
        const t = walker.currentNode;
        const el = t.parentElement;
        if (!t.textContent.trim() || ['SCRIPT', 'STYLE'].includes(el.tagName) || el.closest('svg') || !shown(el)) continue;
        const range = document.createRange();
        range.selectNodeContents(t);
        const r = range.getBoundingClientRect();
        let clip = view.clientWidth;
        for (let n = el; n && n !== document.body; n = n.parentElement) {
          if (getComputedStyle(n).overflowX !== 'visible') clip = Math.min(clip, n.getBoundingClientRect().right);
        }
        if (r.right > clip + 0.5 || r.left < -0.5) out.push(nameOf(el) + ' "' + t.textContent.trim().slice(0, 25) + '" ends at ' + Math.round(r.right) + ', visible up to ' + Math.round(clip));
      }
      for (const c of document.querySelectorAll('button, input, label.toggle')) {
        const r = c.getBoundingClientRect();
        if (r.right > view.clientWidth + 0.5) out.push(nameOf(c) + ' sticks out at ' + Math.round(r.right));
      }
      return out;
    """)
    report(problems)


# 6b. The line snap (the glide when the phone solves for its clock)
def watch_first_line(page):
    page.evaluate("""() => {
      window.__seen = new Set();
      window.__watching = true;
      const look = () => {
        const line = document.querySelector('#map-lines polyline');
        if (line) window.__seen.add(line.getAttribute('points'));
        if (window.__watching) requestAnimationFrame(look);
      };
      look();
    }""")


def count_shapes_after_pressing_solve(page):
    set_slider(page, CLOCK, 20)
    watch_first_line(page)
    page.locator("#solve").click()  # a real click, so the page may glide
    page.wait_for_timeout(1200)
    return page.evaluate("() => { window.__watching = false; return window.__seen.size; }")


@pytest.mark.parametrize("width", WIDTHS)
def test_the_snap_glides_normally_but_not_under_reduced_motion(open_page, width):
    page = open_page(width).page
    assert count_shapes_after_pressing_solve(page) > 3, "the test cannot see the glide, so it proves nothing"
    page = open_page(width).page
    page.emulate_media(reduced_motion="reduce")
    assert count_shapes_after_pressing_solve(page) <= 3, "the line snap still glides under reduced motion"
