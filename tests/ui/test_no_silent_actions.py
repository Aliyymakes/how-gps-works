"""Issue #56: no silent actions. Every test runs in Chromium and WebKit (see conftest.py)."""
STATUS_LINES = [
    "#status",
    "#step-geometry [data-id=status]",
    "#step-signal [data-el=status]",
    "#step-relativity [data-id=status]",
]
FAILURE_WORDS = "Python could not be downloaded, so nothing here can calculate yet."
VISIBLE_LINES = "#map-lines polyline:not(.is-hidden)"


def text(page, selector):
    return page.locator(selector).inner_text().strip()


def settle(page):
    page.wait_for_timeout(500)  # Python answers, then the next frame draws


def toggle_satellite(page, number):
    page.locator("#switches label").nth(number).click()
    settle(page)


def set_slider(page, selector, value):
    page.locator(selector).fill(str(value))
    settle(page)


def count_flashes(page):
    """Count how often the page flashed a message (say.js calls element.animate)."""
    page.evaluate("""() => {
      window.__flashes = 0;
      const animate = Element.prototype.animate;
      Element.prototype.animate = function (...args) { window.__flashes++; return animate.apply(this, args); };
    }""")


def wait_for_text_in_all_status_lines(page, words):
    page.wait_for_function(
        "([selectors, words]) => selectors.every((s) => document.querySelector(s).textContent.includes(words))",
        arg=[STATUS_LINES, words],
        timeout=60000,
    )


def assert_nothing_pretends_to_work(page):
    assert page.locator("#clock").is_disabled()
    assert page.locator("#solve").is_disabled()
    assert page.locator("#reset").is_disabled()
    assert page.locator("#step-geometry [data-id=slider]").is_disabled()
    assert page.locator("#step-signal [data-el=noise]").is_disabled()
    assert page.locator("#error-badge").is_hidden()
    assert text(page, "#error-value") == "–"


# 1
def test_every_button_answers_each_press(open_page):
    page = open_page().page
    count_flashes(page)
    buttons = [  # (button, the message line it answers in)
        ("#solve", "#msg-solve"),
        ("#reset", "#msg-reset"),
        ("#step-geometry [data-id=reset]", "#step-geometry [data-id=msg-reset]"),
        ("#step-signal [data-el=reset]", "#step-signal [data-el=msg-reset]"),
    ]
    for button, message in buttons:
        for _ in range(2):
            before = page.evaluate("window.__flashes")
            page.locator(button).click()
            page.wait_for_function("(n) => window.__flashes > n", arg=before, timeout=1000)
            assert text(page, message) != ""


# 2
def test_clock_solved_with_one_satellite_off_refuses(open_page):
    page = open_page().page
    page.locator("#solve").click()
    settle(page)
    toggle_satellite(page, 0)
    message = text(page, "#msg-switch")
    assert message.startswith("Can't solve:")
    assert message.endswith("Turn a satellite back on.")
    assert page.locator("#error-badge").is_hidden()
    assert page.locator("#map-dot").evaluate("node => node.style.display") == "none"
    assert text(page, "#error-value") == "–"
    assert page.locator(VISIBLE_LINES).count() == 3


# 3
def test_clock_trusted_with_too_few_satellites_refuses(open_page):
    page = open_page().page
    toggle_satellite(page, 0)
    toggle_satellite(page, 1)
    steps = [
        (None, "only 2 satellites are", 2),
        (2, "only 1 satellite is", 1),
        (3, "no satellites are", 0),
    ]
    for number, words, on in steps:
        if number is not None:
            toggle_satellite(page, number)
        message = text(page, "#msg-switch")
        assert message.startswith("Can't find a position:")
        assert words in message
        assert page.locator(VISIBLE_LINES).count() == on
        assert text(page, "#msg-readout") == "No position: see the message under the satellite switches."


# 4
def test_solve_button_shows_its_mode(open_page):
    page = open_page().page
    solve = page.locator("#solve")
    assert solve.get_attribute("aria-pressed") == "false"
    first_words = solve.inner_text()
    solve.click()
    settle(page)
    assert solve.get_attribute("aria-pressed") == "true"
    assert solve.inner_text() != first_words
    set_slider(page, "#clock", 10)
    assert solve.get_attribute("aria-pressed") == "false"
    assert solve.inner_text() == first_words
    assert "Back to trusting the clock" in text(page, "#msg-slider")
    set_slider(page, "#clock", 11)
    assert "Back to trusting the clock" in text(page, "#msg-slider")  # it stays through a drag (#73)
    page.locator("#solve").click()
    settle(page)
    assert text(page, "#msg-slider") == ""


# 5
def test_clock_slider_at_max_says_lines_are_off_the_map(open_page):
    page = open_page().page
    set_slider(page, "#clock", page.locator("#clock").get_attribute("max"))
    assert "moved off the edge of this map" in text(page, "#map-caption")


# 6
def test_blocked_download_fails_in_words_and_try_again_recovers(open_page):
    site = open_page(cdn="block", wait=False)
    page = site.page
    wait_for_text_in_all_status_lines(page, FAILURE_WORDS)
    assert page.get_by_role("button", name="Try again").count() == 4
    assert_nothing_pretends_to_work(page)
    site.cdn = "cache"
    page.get_by_role("button", name="Try again").first.click()
    site.wait_ready()
    page.wait_for_function(
        "(selectors) => selectors.every((s) => document.querySelector(s).textContent === '')", arg=STATUS_LINES
    )
    assert page.get_by_role("button", name="Try again").count() == 0
    assert page.locator("#step-geometry [data-id=slider]").is_enabled()
    assert page.locator("#step-signal [data-el=noise]").is_enabled()
    assert page.locator("#step-relativity [data-id=slider]").is_enabled()


# 7
def test_loading_shows_steps_in_every_section(open_page):
    site = open_page(delay_ms=200, wait=False)
    wait_for_text_in_all_status_lines(site.page, "Step")
    site.wait_ready()


# 8
def test_missing_mechanism_file_fails_the_load(open_page):
    page = open_page(missing=["mechanism/solver.py"], wait=False).page
    wait_for_text_in_all_status_lines(page, "Part of our GPS code could not be downloaded")
    assert page.get_by_role("button", name="Try again").count() == 4
    assert_nothing_pretends_to_work(page)


# 9
def test_every_status_message_is_announced(open_page):
    page = open_page().page
    missing = page.evaluate(
        "[...document.querySelectorAll('[role=status]')].filter(n => n.getAttribute('aria-live') !== 'polite').length"
    )
    assert missing == 0
    assert page.locator("[role=status]").count() > 10


# 10
def test_no_errors_while_using_every_control(open_page):
    site = open_page()
    page = site.page
    set_slider(page, "#clock", 30)
    page.locator("#solve").click()
    settle(page)
    toggle_satellite(page, 0)
    toggle_satellite(page, 0)
    page.locator("#reset").click()
    settle(page)
    set_slider(page, "#step-geometry [data-id=slider]", 60)
    page.locator("#step-geometry [data-id=reset]").click()
    settle(page)
    set_slider(page, "#step-signal [data-el=noise]", 8)
    page.locator("#step-signal [data-el=reset]").click()
    settle(page)
    assert site.errors == []


def test_bridge_file_missing_shows_failure(open_page):
    """If web/bridge.js itself cannot be downloaded, every section still says so (Codex review on #58)."""
    page = open_page(missing=["web/bridge.js"], wait=False).page
    page.wait_for_timeout(3000)
    words = page.locator("text=Python could not be downloaded")
    assert words.count() == 4
