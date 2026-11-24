"""Improvements 2 and 10 (docs/ui-redesign.md): the relativity section is two cards under one slider and
starts at one day. Every test runs in Chromium and WebKit (see conftest.py)."""
REL = "#step-relativity"
SLIDER = f"{REL} [data-id=slider]"


def settle(page):
    page.wait_for_timeout(500)  # Python answers, then the next frame draws


def text(page, selector):
    return page.locator(selector).inner_text().replace(" ", " ").strip()


def set_hours(page, value):
    page.locator(SLIDER).fill(str(value))
    settle(page)


def dot_centre(page, name):
    box = page.locator(f"{REL} [data-id=dot-{name}] circle").bounding_box()
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


def test_starts_at_one_day_with_the_effect_showing(open_page):
    page = open_page().page
    assert page.locator(SLIDER).input_value() == "24"
    assert text(page, f"{REL} [data-id=slider-value]") == "24 h"
    assert "38" in text(page, f"{REL} [data-id=gap]")
    assert "11 km" in text(page, f"{REL} [data-id=range]")
    assert text(page, f"{REL} [data-id=trusted-badge]") == "Fix is far off"
    assert text(page, f"{REL} [data-id=solved-badge]") == "Good fix"
    assert text(page, f"{REL} [data-id=trusted]").endswith("km off")
    assert text(page, f"{REL} [data-id=solved]") == "0 m off"
    # All four distance lines of both maps are drawn, none hidden, and the maps differ.
    for name in ("trusted", "solved"):
        lines = page.locator(f"{REL} [data-id=lines-{name}] polyline")
        assert lines.count() == 4
        assert page.locator(f"{REL} [data-id=lines-{name}] polyline.is-hidden").count() == 0
        assert text(page, f"{REL} [data-id=caption-{name}]") == ""
    (tx, ty), (sx, sy) = dot_centre(page, "trusted"), dot_centre(page, "solved")
    box_t = page.locator(f"{REL} [data-id=map-trusted]").bounding_box()
    box_s = page.locator(f"{REL} [data-id=map-solved]").bounding_box()
    # Compare positions inside each map, not on the page.
    assert abs((tx - box_t["x"]) - (sx - box_s["x"])) + abs((ty - box_t["y"]) - (sy - box_s["y"])) > 20


def test_digits_and_the_two_maps_agree_at_zero(open_page):
    page = open_page().page
    ground = text(page, f"{REL} [data-id=digits-ground]")
    satellite = text(page, f"{REL} [data-id=digits-satellite]")
    assert ground == "24:00:00.000 000"
    assert satellite == "24:00:00.000 038"
    # Only the digits that differ are bright.
    assert page.locator(f"{REL} [data-id=digits-satellite] .diff").count() == 2
    set_hours(page, 0)
    assert text(page, f"{REL} [data-id=digits-ground]") == text(page, f"{REL} [data-id=digits-satellite]")
    assert page.locator(f"{REL} [data-id=digits-satellite] .diff").count() == 0
    assert text(page, f"{REL} [data-id=gap]") == "0 µs"
    assert text(page, f"{REL} [data-id=sentence]").startswith("No gap yet")
    assert page.locator(f"{REL} [data-id=height-note]").is_hidden()
    set_hours(page, 12)
    assert text(page, f"{REL} [data-id=digits-satellite]") == "12:00:00.000 019"
    assert text(page, f"{REL} [data-id=gap]") == "about 19 µs"


def test_fixed_breakdown_and_words(open_page):
    page = open_page().page
    words = text(page, REL)
    for line in (
        "Weaker gravity up there: the clock runs faster, by 45 µs a day",
        "It moves fast: the clock runs slower, by 7 µs a day",
        "Together: about 38 µs a day faster",
        "A signal covers about 300 m in one millionth of a second.",
        "Both effects come from Einstein's relativity. Gravity is the bigger one.",
        "What you're looking at: two clocks that started together.",
        "What you're looking at: the map from the top of the page, twice",
    ):
        assert line in words, line
    lowered = words.lower()
    for banned in ("gain", "longer", "shorter", "special relativity", "set to tick slightly slow"):
        assert banned not in lowered, banned
    # The breakdown is fixed text: moving the slider does not change it.
    set_hours(page, 3)
    assert "by 45 µs a day" in text(page, REL)


def test_looking_lines_sit_above_their_pictures(open_page):
    page = open_page().page
    for card in ("rel-a-title", "rel-b-title"):
        looking = page.locator(f"{REL} section[aria-labelledby={card}] .looking")
        assert looking.is_visible()
        assert page.evaluate("(n) => getComputedStyle(n).opacity", looking.element_handle()) == "1"
    picture = page.locator(f"{REL} svg.figure").bounding_box()
    line = page.locator(f"{REL} section[aria-labelledby=rel-a-title] .looking").bounding_box()
    assert line["y"] + line["height"] <= picture["y"] and picture["y"] - (line["y"] + line["height"]) < 40


def test_phone_width_fits_and_maps_are_big_enough(open_page):
    site = open_page(width=390)
    page = site.page
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    for name in ("trusted", "solved"):
        assert page.locator(f"{REL} [data-id=map-{name}]").bounding_box()["width"] >= 140
    set_hours(page, 7)
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    assert site.errors == []


def test_dragging_stays_responsive(open_page):
    page = open_page().page
    page.locator(SLIDER).scroll_into_view_if_needed()
    page.evaluate("""() => {
      window.__gaps = [];
      let last = performance.now();
      const tick = (now) => { window.__gaps.push(now - last); last = now; window.__raf = requestAnimationFrame(tick); };
      window.__raf = requestAnimationFrame(tick);
    }""")
    for hours in list(range(24, -1, -1)) + list(range(0, 25)):
        page.locator(SLIDER).fill(str(hours))
        page.wait_for_timeout(16)
    settle(page)
    gaps = page.evaluate("() => { cancelAnimationFrame(window.__raf); return window.__gaps; }")
    print("longest frame gap while dragging (ms):", max(gaps))
    assert max(gaps) < 250
    assert text(page, f"{REL} [data-id=slider-value]") == "24 h"
    assert "38" in text(page, f"{REL} [data-id=gap]")  # the last value won
