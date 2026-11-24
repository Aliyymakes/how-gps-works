"""Issue #59: the first two minutes. Every test runs in Chromium and WebKit (see conftest.py)."""
import time

HINTS = ["#hint-1", "#hint-2", "#hint-3", "#hint-done"]
BLOCKS = ["#block-slider", "#block-solve", "#block-switches"]


def visible_hints(page):
    return [h for h in HINTS if page.locator(h).is_visible()]


def highlighted(page):
    return [b for b in BLOCKS if "highlight" in page.locator(b).get_attribute("class")]


def drag_slider_right(page, key="End", times=1):
    page.locator("#clock").focus()
    for _ in range(times):
        page.keyboard.press(key)
    page.wait_for_timeout(500)  # Python answers, then the next frame draws


def press_solve(page):
    page.locator("#solve").click()
    page.wait_for_timeout(800)  # the glide takes 450 ms


def switch_one_satellite_off(page):
    page.locator("#switches label").nth(0).click()
    page.wait_for_timeout(500)


# 1
def test_idea_key_and_map_text_show_before_python_is_ready(open_page):
    page = open_page(cdn="cache", delay_ms=3000, wait=False).page
    page.wait_for_selector("#map-wait", state="visible", timeout=1000)
    assert page.get_by_text("Each satellite's signal says when it left.").is_visible()
    assert page.get_by_text("That only works if the phone's clock is right.").is_visible()
    assert page.locator(".map-key li").count() == 3
    assert page.locator(".map-key li").nth(2).is_visible()
    assert page.locator("#map-wait").text_content() == "The map appears when Python has loaded."
    assert page.locator("#clock").is_disabled()
    assert visible_hints(page) == []


# 2
def test_after_ready_only_hint_1_shows_and_only_the_slider_is_highlighted(open_page):
    page = open_page().page
    assert visible_hints(page) == ["#hint-1"]
    assert highlighted(page) == ["#block-slider"]
    assert page.locator("#map-wait").is_hidden()


# 3
def test_the_guide_moves_one_step_at_a_time(open_page):
    page = open_page().page
    drag_slider_right(page)
    assert visible_hints(page) == ["#hint-2"]
    assert highlighted(page) == ["#block-solve"]
    press_solve(page)
    assert visible_hints(page) == ["#hint-3"]
    assert highlighted(page) == ["#block-switches"]
    switch_one_satellite_off(page)
    assert visible_hints(page) == ["#hint-done"]
    assert highlighted(page) == []


# 4
def test_reset_does_not_bring_a_hint_back(open_page):
    page = open_page().page
    drag_slider_right(page)
    press_solve(page)
    switch_one_satellite_off(page)
    page.locator("#reset").click()
    page.wait_for_timeout(500)
    assert visible_hints(page) == ["#hint-done"]
    assert highlighted(page) == []


# 5
def test_the_path_is_quick_and_the_slider_fits_a_phone_screen(open_page):
    page = open_page(width=390).page
    page.locator("section[aria-labelledby=map-title]").evaluate("(node) => window.scrollTo(0, node.getBoundingClientRect().top + window.scrollY)")
    bottom = page.locator("#block-slider").evaluate("(node) => node.getBoundingClientRect().bottom")
    assert bottom <= 844
    assert page.locator("#hint-1").is_visible()
    started = time.time()
    drag_slider_right(page)
    press_solve(page)
    switch_one_satellite_off(page)
    assert time.time() - started < 10
    assert visible_hints(page) == ["#hint-done"]


def watch_line(page):
    """Record every different value of the second line's points (the first is off the map at End) over the next 900 ms."""
    page.evaluate("""() => {
      window.__seen = [];
      const node = document.querySelectorAll("#map-lines polyline")[1];
      const until = performance.now() + 900;
      const look = () => {
        const value = node.getAttribute("points");
        if (window.__seen[window.__seen.length - 1] !== value) window.__seen.push(value);
        if (performance.now() < until) requestAnimationFrame(look);
      };
      look();
    }""")


# 6
def test_the_lines_glide_together_unless_motion_is_reduced(open_page):
    page = open_page().page
    drag_slider_right(page)
    watch_line(page)
    page.locator("#solve").click()
    page.wait_for_timeout(1000)
    seen = page.evaluate("window.__seen")
    assert len(set(seen)) >= 3
    assert seen[-1] == page.locator("#map-lines polyline").nth(1).get_attribute("points")

    calm = open_page().page
    calm.emulate_media(reduced_motion="reduce")
    drag_slider_right(calm)
    watch_line(calm)
    calm.locator("#solve").click()
    calm.wait_for_timeout(1000)
    seen = calm.evaluate("window.__seen")
    assert len(seen) == 2  # the old value, then one change to the final one


# 7
def test_no_sideways_scroll_at_phone_width(open_page):
    page = open_page(width=390).page
    assert page.evaluate("document.scrollingElement.scrollWidth <= innerWidth")


def test_step_two_hint_goes_back_when_lines_meet_again(open_page):
    """Codex review on #63: hint 2 says the lines no longer meet, so it must not stay when they meet again."""
    page = open_page().page
    page.focus("#clock")
    page.keyboard.press("End")
    page.wait_for_function("!document.getElementById('hint-2').hidden")
    page.click("#reset")
    page.wait_for_function("!document.getElementById('hint-1').hidden")
    assert page.locator("#hint-2").is_hidden()
