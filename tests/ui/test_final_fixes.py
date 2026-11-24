"""Issue #73: fixes from the final re-audit. Every test runs in Chromium and WebKit (see conftest.py)."""
import pytest

HINTS = ["#hint-1", "#hint-2", "#hint-3", "#hint-done"]
STEP_HINTS = [
    ("#step-geometry [data-id=hint]", "#geo-bunch"),
    ("#step-signal [data-el=hint]", "#signal-noise"),
    ("#step-relativity [data-id=hint]", "#rel-hours"),
]
STATUS_LINES = ["#status", "#step-geometry [data-id=status]", "#step-signal [data-el=status]", "#step-relativity [data-id=status]"]
BACK_WORDS = "Back to trusting the clock. Press the button below to solve for it again."
OUR_FILE_WORDS = "Part of our GPS code could not be downloaded, so nothing here can calculate yet. Reload the page; if that does not help, the site itself has a problem."
INTERNET_WORDS = "Python could not be downloaded, so nothing here can calculate yet. Check your internet connection, then press Try again."


def opacity(page, selector):
    return page.evaluate("(s) => getComputedStyle(document.querySelector(s)).opacity", selector)


def shown_hints(page):
    # is_visible ignores opacity, so a hint counts only when it is not hidden and fully opaque
    return [h for h in HINTS if page.locator(h).is_visible() and opacity(page, h) == "1"]


def drag_slider_right(page):
    page.locator("#clock").focus()
    page.keyboard.press("End")
    page.wait_for_timeout(500)


def press_solve(page):
    page.locator("#solve").click()
    page.wait_for_timeout(800)


def switch_one_satellite_off(page):
    page.locator("#switches label").nth(0).click()
    page.wait_for_timeout(500)


# N2
@pytest.mark.parametrize("hint, slider", STEP_HINTS)
def test_hints_of_sections_2_to_4_are_seen_then_hidden_after_first_input(open_page, hint, slider):
    page = open_page().page
    page.wait_for_timeout(500)  # the fade takes a moment
    assert page.locator(hint).is_visible()
    assert opacity(page, hint) == "1"
    page.locator(slider).focus()
    at_max = page.locator(slider).input_value() == page.locator(slider).get_attribute("max")  # relativity starts at its maximum
    page.keyboard.press("ArrowLeft" if at_max else "ArrowRight")
    page.wait_for_timeout(500)
    assert page.locator(hint).is_hidden()


# N3
def test_back_to_trusting_the_clock_stays_for_the_whole_drag(open_page):
    page = open_page().page
    press_solve(page)
    box = page.locator("#clock").bounding_box()
    y = box["y"] + box["height"] / 2
    page.mouse.move(box["x"] + 10, y)
    page.mouse.down()
    page.mouse.move(box["x"] + box["width"] - 10, y, steps=20)
    page.mouse.up()
    page.wait_for_timeout(800)
    assert page.locator("#msg-slider").text_content() == BACK_WORDS
    # any other action clears it
    press_solve(page)
    assert page.locator("#msg-slider").text_content() == ""


# N1
def test_the_closing_line_is_inside_the_window_when_it_appears(open_page):
    site = open_page()
    page = site.page
    page.evaluate("window.scrollTo(0, 0)")
    drag_slider_right(page)
    press_solve(page)
    switch_one_satellite_off(page)
    page.wait_for_timeout(1500)  # a smooth scroll takes a moment
    assert shown_hints(page) == ["#hint-done"]
    box = page.locator("#hint-done").bounding_box()
    assert box["y"] >= 0
    assert box["y"] + box["height"] <= 900


# N6 (a)
def test_back_to_trusting_the_clock_at_step_3_goes_back_to_step_2(open_page):
    page = open_page().page
    drag_slider_right(page)
    press_solve(page)
    assert shown_hints(page) == ["#hint-3"]
    page.locator("#clock").focus()
    page.keyboard.press("ArrowLeft")  # trusted again, the lines still miss
    page.wait_for_timeout(600)
    assert shown_hints(page) == ["#hint-2"]


def test_reset_at_step_3_goes_back_to_step_1(open_page):
    page = open_page().page
    drag_slider_right(page)
    press_solve(page)
    assert shown_hints(page) == ["#hint-3"]
    page.locator("#reset").click()  # trusted again, the lines meet
    page.wait_for_timeout(600)
    assert shown_hints(page) == ["#hint-1"]


# N6 (b)
@pytest.mark.parametrize("move_slider_first", [False, True])
def test_the_cant_solve_refusal_goes_straight_to_done(open_page, move_slider_first):
    page = open_page().page
    if move_slider_first:
        drag_slider_right(page)
        assert shown_hints(page) == ["#hint-2"]
    else:
        assert shown_hints(page) == ["#hint-1"]
    switch_one_satellite_off(page)
    press_solve(page)
    assert page.locator("#msg-switch").text_content().startswith("Can't solve")
    assert shown_hints(page) == ["#hint-done"]


# N5
def test_the_loading_words_do_not_overlap_the_cross(open_page):
    page = open_page(delay_ms=3000, wait=False).page
    page.wait_for_selector("#map-wait", state="visible", timeout=1000)
    a = page.evaluate("(s) => document.querySelector(s).getBoundingClientRect().toJSON()", "#map-wait")
    b = page.evaluate("(s) => document.querySelector(s).getBoundingClientRect().toJSON()", "#map-true")
    overlap = a["left"] < b["right"] and b["left"] < a["right"] and a["top"] < b["bottom"] and b["top"] < a["bottom"]
    assert not overlap, (a, b)


# N7
def test_try_again_while_still_offline_flashes_the_failure_words(open_page):
    page = open_page(cdn="block", wait=False).page
    page.get_by_role("button", name="Try again").first.wait_for(timeout=20000)
    assert page.locator("#status").text_content() == INTERNET_WORDS
    page.evaluate("""() => {
      const node = document.getElementById('status');
      window.__flashed = false;
      new MutationObserver(() => { if (node.getAnimations().length > 0) window.__flashed = true; })
        .observe(node, { childList: true, characterData: true, subtree: true });
    }""")
    page.get_by_role("button", name="Try again").first.click()
    page.wait_for_timeout(300)
    assert page.evaluate("window.__flashed") is True
    page.get_by_role("button", name="Try again").first.wait_for(timeout=20000)
    assert page.locator("#status").text_content() == INTERNET_WORDS


# N8
def test_no_half_sentence_while_python_is_starting(open_page):
    site = open_page(delay_ms=1500, wait=False)
    page = site.page
    page.add_init_script("""
      window.__seen = new Set();
      setInterval(() => {
        const node = document.getElementById('status');
        if (node) window.__seen.add(node.textContent);
      }, 25);
    """)
    page.reload()
    page.wait_for_timeout(2000)
    seen = page.evaluate("[...window.__seen]")
    assert any("Step 1 of 2" in s for s in seen), seen  # the sampler works
    assert "The controls switch on when this finishes." not in [s.strip() for s in seen], seen


# C6
def test_a_missing_file_of_ours_is_not_blamed_on_the_internet(open_page):
    page = open_page(missing=["mechanism/signal.py"], wait=False).page
    for selector in STATUS_LINES:
        page.wait_for_function("(s) => document.querySelector(s).textContent.startsWith('Part of our GPS code')", arg=selector, timeout=60000)
        assert page.locator(selector).text_content() == OUR_FILE_WORDS
    assert page.get_by_role("button", name="Try again").count() == 4
