"""Signal section rebuilt (docs/ui-redesign.md improvements 1 and 9). Every test runs in Chromium and WebKit."""
SIG = "#step-signal"
SHIFT = f"{SIG} [data-el=shift]"
NOISE = f"{SIG} [data-el=noise]"


def el(name):
    return f"{SIG} [data-el={name}]"


def settle(page):
    page.wait_for_timeout(500)


def text(page, selector):
    return page.locator(selector).inner_text().replace(" ", " ").strip()


def set_shift(page, value):
    page.locator(SHIFT).fill(str(value))
    settle(page)


def press_search(page):
    page.locator(el("search")).click()


def boxes_apart(a, b):
    return (a["x"] + a["width"] <= b["x"] or b["x"] + b["width"] <= a["x"]
            or a["y"] + a["height"] <= b["y"] or b["y"] + b["height"] <= a["y"])


def test_score_is_one_only_when_lined_up(open_page):
    page = open_page().page
    set_shift(page, 14)
    assert text(page, el("hand-score")) == "1.00"
    assert text(page, el("hand-sentence")).startswith("Lined up")
    assert "14 chips" in text(page, el("hand-sentence"))
    set_shift(page, 13)
    assert text(page, el("hand-score")).startswith(("0.0", "-0.0"))
    assert text(page, el("hand-sentence")).startswith("Not lined up")


def test_dragging_the_copy_sets_the_slider(open_page):
    page = open_page().page
    page.locator(el("copy-hit")).scroll_into_view_if_needed()
    box = page.locator(el("copy-hit")).bounding_box()
    chip_px = page.locator(el("rows")).bounding_box()["width"] / 40
    y = box["y"] + box["height"] / 2
    page.mouse.move(box["x"] + 20, y)
    page.mouse.down()
    page.mouse.move(box["x"] + 20 + 14 * chip_px, y, steps=10)
    page.mouse.up()
    settle(page)
    assert page.locator(SHIFT).input_value() == "14"
    assert text(page, el("hand-score")) == "1.00"


def test_arrow_keys_move_the_copy_one_chip(open_page):
    page = open_page().page
    page.locator(SHIFT).focus()
    page.keyboard.press("ArrowRight")
    settle(page)
    assert page.locator(SHIFT).input_value() == "1"
    assert text(page, el("shift-value")) == "1 chip"
    assert "Match score" in page.locator(SHIFT).get_attribute("aria-valuetext")


def test_lit_steps_follow_agreement(open_page):
    page = open_page().page
    lit = "document.querySelectorAll('#step-signal .cell:not(.is-dim)').length"
    set_shift(page, 14)
    assert page.evaluate(lit) == 40  # no noise: every step agrees at the real delay
    set_shift(page, 13)
    assert page.evaluate(lit) < 40


def test_search_fills_readout_at_once_and_markers_line_up(open_page):
    page = open_page().page
    assert text(page, el("best-delay")) == "–"
    press_search(page)
    page.wait_for_timeout(100)  # well before the 1000 ms reveal ends
    assert text(page, el("best-delay")) == "14 chips"
    assert text(page, el("badge")) == "Found"
    settle(page)
    for real, best, close in [("closeup-real", "closeup-best", True), ("full-real", "full-best", False)]:
        a = page.locator(el(f"{real}-label")).bounding_box()
        b = page.locator(el(f"{best}-label")).bounding_box()
        assert page.locator(el(f"{real}-label")).is_visible() and page.locator(el(f"{best}-label")).is_visible()
        assert boxes_apart(a, b)
        ta = page.locator(el(f"{real}-tick")).bounding_box()
        tb = page.locator(el(f"{best}-tick")).bounding_box()
        assert abs((ta["x"] + ta["width"] / 2) - (tb["x"] + tb["width"] / 2)) <= 2
        if close:
            assert abs((a["x"] + a["width"] / 2) - (ta["x"] + ta["width"] / 2)) <= 2


def test_real_delay_marker_waits_for_the_find_then_stays(open_page):
    page = open_page().page
    for name in ("closeup-real-label", "closeup-real-tick", "full-real-label", "full-real-tick"):
        assert page.locator(el(name)).is_hidden(), name
    set_shift(page, 14)
    for name in ("closeup-real-label", "full-real-label"):
        assert page.locator(el(name)).is_visible(), name
    assert page.locator(el("closeup-best-label")).is_hidden()
    set_shift(page, 5)
    assert page.locator(el("full-real-label")).is_visible()
    page.locator(el("reset")).click()
    settle(page)
    assert page.locator(el("closeup-real-label")).is_hidden()
    press_search(page)
    settle(page)
    assert page.locator(el("full-real-label")).is_visible()


def test_keyboard_search_is_not_animated(open_page):
    page = open_page().page
    page.locator(el("search")).focus()
    page.keyboard.press("Enter")
    assert page.evaluate("document.querySelector('#step-signal [data-el=full-wrap]').dataset.reveal") == "done"


def test_noise_change_clears_the_search_message(open_page):
    page = open_page().page
    press_search(page)
    assert text(page, el("msg-search")) != ""
    page.locator(NOISE).fill("24")
    settle(page)
    assert text(page, el("msg-search")) == ""


def test_cards_line_up_and_no_band_under_the_noise_slider(open_page):
    page = open_page().page
    left = page.locator(f"{SIG} .grid > .card:first-child > :first-child").bounding_box()
    right = page.locator(f"{SIG} .grid > .card:last-child > :first-child").bounding_box()
    assert abs(left["y"] - right["y"]) <= 1
    block = page.locator(f"{SIG} .slider.inset").bounding_box()
    slider = page.locator(NOISE).bounding_box()
    assert block["y"] + block["height"] - (slider["y"] + slider["height"]) <= 24


def test_bracket_words_stay_inside_the_picture_at_shift_30_on_a_phone(open_page):
    page = open_page(width=390).page
    set_shift(page, 30)
    words = page.locator(el("bracket-text")).bounding_box()
    rows = page.locator(el("rows")).bounding_box()
    assert words["x"] >= rows["x"] - 1 and words["x"] + words["width"] <= rows["x"] + rows["width"] + 1


def test_close_up_prompt_before_the_search(open_page):
    page = open_page().page
    assert text(page, el("closeup-note")) == "Each shift you try leaves a bar here."
    press_search(page)
    assert text(page, el("closeup-note")) == ""


def test_reveal_takes_about_a_second_and_new_input_ends_it(open_page):
    page = open_page().page
    reveal = "document.querySelector('#step-signal [data-el=full-wrap]').dataset.reveal"
    press_search(page)
    page.wait_for_timeout(100)
    assert page.evaluate(reveal) == "running"
    page.locator(SHIFT).focus()
    page.keyboard.press("ArrowRight")
    assert page.evaluate(reveal) == "done"


def test_reduced_motion_draws_plots_at_once(open_page):
    page = open_page().page
    page.emulate_media(reduced_motion="reduce")
    press_search(page)
    page.wait_for_timeout(50)
    assert page.evaluate("document.querySelector('#step-signal [data-el=full-wrap]').dataset.reveal") == "done"


def test_noise_loses_the_signal_and_close_up_says_so(open_page):
    page = open_page().page
    page.locator(NOISE).fill("24")
    settle(page)
    press_search(page)
    settle(page)
    assert text(page, el("badge")) == "Lost"
    assert "outside this close-up" in text(page, el("closeup-note"))
    assert page.locator(el("closeup-best-label")).is_hidden()
    assert page.locator(el("full-best-label")).is_visible()


def test_tries_show_before_the_search_and_reset_clears_everything(open_page):
    page = open_page().page
    set_shift(page, 3)
    assert page.evaluate("document.querySelectorAll('#step-signal [data-el=closeup-tries] .bar').length") == 1
    press_search(page)
    settle(page)
    page.locator(el("reset")).click()
    settle(page)
    assert text(page, el("msg-reset")) == "Back to the start: copy at 0, no noise."
    assert page.locator(SHIFT).input_value() == "0"
    assert text(page, el("best-delay")) == "–"
    assert page.evaluate("document.querySelectorAll('#step-signal [data-el=closeup-tries] .bar').length") == 0


def test_guide_moves_one_step_at_a_time(open_page):
    page = open_page().page
    page.wait_for_timeout(500)
    hint = el("hint")
    assert text(page, hint).startswith("Step 1")
    assert page.evaluate("getComputedStyle(document.querySelector('#step-signal [data-el=hint]')).opacity") == "1"
    set_shift(page, 14)
    assert text(page, hint).startswith("Step 2")
    press_search(page)
    assert text(page, hint).startswith("Step 3")
    page.locator(NOISE).focus()
    page.keyboard.press("ArrowRight")
    settle(page)
    assert page.locator(hint).is_hidden()


def test_looking_line_is_above_the_picture_and_nothing_overflows_at_phone_width(open_page):
    site = open_page(width=390)
    page = site.page
    line = page.locator(f"{SIG} .looking")
    assert line.is_visible() and line.inner_text().startswith("What you're looking at:")
    assert line.bounding_box()["y"] < page.locator(el("rows")).bounding_box()["y"]
    hit = page.locator(el("copy-hit")).bounding_box()
    assert hit["height"] >= 44
    press_search(page)
    settle(page)
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    assert site.errors == []
