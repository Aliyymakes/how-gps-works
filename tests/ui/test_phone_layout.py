"""Phone layout of the first screen (docs/ui-redesign.md, improvements 5, 11 and 12, and the "looking at" line and
drawing of improvements 3 and 4). Every test runs in Chromium and WebKit (see conftest.py)."""

PHONE = {"width": 390, "height": 844}
SLIDER_LIMIT = 620  # docs/ui-redesign.md improvement 5: the clock slider's bottom, in px from the top of the page
CONTROLS = ["#clock", "#solve", "#switches label:nth-child(1)", "#switches label:nth-child(4)", "#reset"]


def phone(open_page, size=PHONE, **kwargs):
    site = open_page(wait=False, **kwargs)
    site.page.set_viewport_size(size)
    return site


def box(page, selector):
    return page.locator(selector).first.evaluate(
        "(node) => { const r = node.getBoundingClientRect(); return { top: r.top, bottom: r.bottom, left: r.left, right: r.right }; }")


def inside_window(page, selector, height=PHONE["height"]):
    r = box(page, selector)
    return r["top"] >= 0 and r["bottom"] <= height


def is_sticky(page):
    return page.locator(".map-card").evaluate("(node) => getComputedStyle(node).position") == "sticky"


def test_slider_and_step_1_hint_are_on_the_first_screen_without_scrolling(open_page):
    site = phone(open_page)
    site.wait_ready()
    page = site.page
    assert page.evaluate("window.scrollY") == 0
    assert box(page, "#clock")["bottom"] <= SLIDER_LIMIT
    assert inside_window(page, "#hint-1")
    assert page.locator("#hint-1").evaluate("(node) => getComputedStyle(node).opacity") == "1"


def test_nothing_jumps_when_python_is_ready(open_page):
    site = phone(open_page, cdn="cache", delay_ms=2000)  # the delay keeps Python loading while we measure
    page = site.page
    page.wait_for_selector("#clock", state="visible")
    before = box(page, "#clock")["top"]
    assert page.locator("#clock").is_disabled()
    site.wait_ready()
    assert abs(box(page, "#clock")["top"] - before) <= 2


def test_the_map_and_the_number_stay_in_view_while_the_controls_are_used(open_page):
    site = phone(open_page)
    site.wait_ready()
    page = site.page
    assert is_sticky(page)
    card_start = page.evaluate("document.querySelector('.map-card').getBoundingClientRect().top + scrollY")
    page.locator("#clock").focus()
    page.keyboard.press("End")
    page.wait_for_timeout(400)
    for selector in ["#clock", "#solve", "#switches label:nth-child(1)", "#reset"]:
        # put the control at the top of the window: the map card has to ride along above it
        page.locator(selector).evaluate("(node) => (node.querySelector('input') || node).scrollIntoView({ block: 'start' })")  # what Tab would scroll to
        page.wait_for_timeout(200)
        assert page.evaluate("scrollY") > card_start, selector  # the page really scrolled past the card's own place
        shown = selector + " .toggle-track" if "label" in selector else selector  # a switch is drawn by its track
        assert box(page, shown)["top"] >= box(page, ".map-card")["bottom"] - 1, selector  # not under the card
        if selector != "#clock":
            page.locator(selector).click()
            page.wait_for_timeout(700)
        card = box(page, ".map-card")
        assert -1 <= card["top"] <= 1, selector
        assert inside_window(page, "#map"), selector
        assert inside_window(page, "#error-value"), selector


def test_the_sticky_card_never_covers_the_focused_control(open_page):
    site = phone(open_page)
    site.wait_ready()
    page = site.page
    webkit = page.context.browser.browser_type.name == "webkit"  # plain Tab skips sliders and buttons there
    forward, backward = ("Alt+Tab", "Alt+Shift+Tab") if webkit else ("Tab", "Shift+Tab")
    page.evaluate("document.activeElement.blur()")
    seen = set()

    def look():
        page.wait_for_timeout(250)
        focused = page.evaluate("""() => {
          const node = document.activeElement;
          const r = (node.closest("label") || node).getBoundingClientRect();
          const card = document.querySelector(".map-card").getBoundingClientRect();
          const msg = document.getElementById("msg-slider").getBoundingClientRect();
          return { id: node.id, top: r.top, msgTop: msg.top, cardBottom: card.bottom, inControls: !!node.closest(".controls") };
        }""")
        if focused["inControls"]:
            seen.add(focused["id"] or "switch")
            assert focused["top"] >= focused["cardBottom"] - 1, focused
            if focused["id"] == "clock":  # the line above the slider (hint or message) is not hidden by the card either
                assert focused["msgTop"] >= focused["cardBottom"] - 1, focused

    for _ in range(14):  # down through the controls and on into the next section
        page.keyboard.press(forward)
        look()
    for _ in range(14):  # and back up: the controls now come in from the top, under the sticky card
        page.keyboard.press(backward)
        look()
    assert {"clock", "solve", "reset"} <= seen, seen


def test_the_map_card_lets_go_when_the_page_moves_on_to_geometry(open_page):
    site = phone(open_page)
    site.wait_ready()
    page = site.page
    page.evaluate("document.getElementById('step-geometry').scrollIntoView()")
    page.wait_for_timeout(300)
    assert box(page, ".map-card")["bottom"] <= 0


def test_the_card_is_not_sticky_on_a_short_screen(open_page):
    site = phone(open_page, {"width": 390, "height": 500})
    site.wait_ready()
    assert not is_sticky(site.page)


def test_no_sideways_scroll_at_390_and_at_200_percent_zoom(open_page):
    site = phone(open_page)
    site.wait_ready()
    page = site.page
    for width in (390, 195):
        page.set_viewport_size({"width": width, "height": 844})
        page.wait_for_timeout(200)
        assert page.evaluate("document.scrollingElement.scrollWidth <= innerWidth"), width


def test_the_looking_at_line_and_the_drawing_are_above_the_map(open_page):
    for size in (PHONE, {"width": 1200, "height": 900}):
        site = phone(open_page, size)
        site.wait_ready()
        page = site.page
        looking = box(page, "#looking-map")
        card = box(page, ".map-card")
        assert looking["bottom"] <= card["top"] <= looking["bottom"] + 40, size
        assert page.locator("#looking-map").evaluate("(node) => getComputedStyle(node).opacity") == "1"
        assert page.locator("#looking-map").text_content().startswith("What you're looking at:")
        figure = page.locator("#figure-first svg:visible")
        assert figure.count() == 1
        assert figure.get_attribute("role") == "img" and figure.get_attribute("aria-label")
        assert box(page, "#figure-first svg:visible")["bottom"] <= looking["top"]


def test_the_drawing_shows_within_a_second_even_when_the_cdn_is_slow(open_page):
    site = phone(open_page, cdn="cache", delay_ms=3000)
    page = site.page
    page.wait_for_selector("#figure-first svg:visible", timeout=1000)
    assert page.locator("#looking-map").is_visible()


def test_the_slider_stays_put_when_a_message_takes_over_the_hint_line(open_page):
    site = phone(open_page)
    site.wait_ready()
    page = site.page
    start = box(page, "#clock")["top"]
    page.locator("#clock").focus()
    page.keyboard.press("End")
    page.wait_for_timeout(400)
    page.locator("#solve").click()
    page.wait_for_timeout(800)
    page.locator("#clock").focus()
    page.keyboard.press("Home")  # back to a good clock: hint 1 returns, and so does the "Back to trusting" message
    page.wait_for_timeout(600)
    assert page.locator("#msg-slider").text_content().startswith("Back to trusting")
    assert abs(box(page, "#clock")["top"] - start) <= 1
