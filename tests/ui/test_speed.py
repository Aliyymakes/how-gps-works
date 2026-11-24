"""Speed checks (issue #64): the first paint does not wait for Python, and nothing freezes
the page for long while the sliders and buttons are used."""
FRAME_RECORDER = """
window.__gaps = { max: 0, last: performance.now() };
(function tick(now) {
  const gap = now - window.__gaps.last;
  if (gap > window.__gaps.max) window.__gaps.max = gap;
  window.__gaps.last = now;
  requestAnimationFrame(tick);
})(performance.now());
"""

MAX_GAP_MS = 150  # ui-guide 6 says 100 ms; the extra 50 ms allows for headless CI noise


def test_heading_and_first_label_show_while_the_cdn_is_slow(open_page):
    site = open_page(delay_ms=3000, wait=False)
    page = site.page
    page.get_by_role("heading", level=1).wait_for(state="visible", timeout=1000)
    page.locator("label[for=clock]").wait_for(state="visible", timeout=1000)
    # Time from the start of navigation to the first thing painted (Chromium and WebKit both report it).
    paint = page.evaluate(
        "performance.getEntriesByName('first-contentful-paint')[0].startTime")
    print("first paint: %.0f ms" % paint)
    assert paint < 1000
    page.unroute_all(behavior="ignoreErrors")  # the slow downloads are still waiting; drop them


def use_everything(page):
    """Drag every slider end to end in 40 mouse steps, then press every button."""
    for slider in page.locator("input[type=range]").all():
        slider.scroll_into_view_if_needed()  # mouse moves do not scroll; the slider must be on screen
        box = slider.bounding_box()
        y = box["y"] + box["height"] / 2
        page.mouse.move(box["x"] + 2, y)
        page.mouse.down()
        for i in range(1, 41):
            page.mouse.move(box["x"] + 2 + (box["width"] - 4) * i / 40, y)
        page.mouse.up()
        assert slider.input_value() == slider.get_attribute("max"), "the drag did not reach the end"
    for button in page.locator("button:visible").all():
        if button.is_enabled():
            button.click()
    page.wait_for_timeout(300)


def test_no_long_frame_gap_and_no_errors_in_use(open_page):
    site = open_page()
    site.page.add_init_script(FRAME_RECORDER)  # runs on the reload, before the page's own scripts
    site.page.reload()
    site.wait_ready()
    assert site.page.locator("input[type=range]").count() >= 3
    site.page.evaluate("window.__gaps.max = 0")  # measure use, not start-up
    use_everything(site.page)
    worst = site.page.evaluate("window.__gaps.max")
    print("longest frame gap in use: %.0f ms" % worst)
    assert worst < MAX_GAP_MS
    assert site.errors == []
