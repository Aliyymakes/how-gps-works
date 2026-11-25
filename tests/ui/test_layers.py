"""Issue #60: every layer (geometry, signal, relativity) meets the same standard.
Every test runs in Chromium and WebKit (see conftest.py)."""
GEO = "#step-geometry"
SIG = "#step-signal"
REL = "#step-relativity"
GEO_SLIDER = f"{GEO} [data-id=slider]"
SIG_SLIDER = f"{SIG} [data-el=noise]"
REL_SLIDER = f"{REL} [data-id=slider]"


def settle(page):
    page.wait_for_timeout(500)  # Python answers, then the next frame draws


def set_slider(page, selector, value):
    page.locator(selector).fill(str(value))
    settle(page)


def text(page, selector):
    return page.locator(selector).inner_text().replace(" ", " ").strip()


def test_hints_show_after_ready_and_hide_for_good_after_first_input(open_page):
    page = open_page().page
    for section, hint, slider, reset, value in [
        (GEO, f"{GEO} [data-id=hint]", GEO_SLIDER, f"{GEO} [data-id=reset]", 50),
        (REL, f"{REL} [data-id=hint]", REL_SLIDER, f"{REL} [data-id=reset]", 12),
    ]:
        assert page.locator(hint).is_visible(), section
        set_slider(page, slider, value)
        assert page.locator(hint).is_hidden(), section
        page.locator(reset).click()
        settle(page)
        assert page.locator(hint).is_hidden(), section


def test_geometry_sentences_badge_and_closing_paragraph(open_page):
    page = open_page().page
    sentence = f"{GEO} [data-id=msg-slider]"
    assert text(page, sentence).startswith("Spread across the sky")
    set_slider(page, GEO_SLIDER, 100)
    assert text(page, sentence).startswith("Bunched together")
    assert text(page, f"{GEO} [data-id=badge]") == "Fix is far off"
    assert "DOP" in page.locator(f"{GEO} [data-id=sky]").get_attribute("aria-label")
    assert page.locator(f"{GEO} section[aria-label='Controls and results'] .geo-closing").count() == 0
    assert page.locator(f"{GEO} .geo-closing").count() == 1


def test_signal_clip_note_badge_and_slider_head_at_phone_width(open_page):
    page = open_page(width=390).page
    clip = f"{SIG} [data-el=clip-note]"
    assert text(page, clip) == ""
    set_slider(page, SIG_SLIDER, 24)
    assert text(page, clip) != ""
    page.locator(f"{SIG} [data-el=search]").click()
    settle(page)
    assert text(page, f"{SIG} [data-el=badge]") == "Lost"
    label = page.locator(f"{SIG} label[for=signal-noise]").bounding_box()
    value = page.locator(f"{SIG} [data-el=noise-value]").bounding_box()
    apart = (
        label["x"] + label["width"] <= value["x"] or value["x"] + value["width"] <= label["x"]
        or label["y"] + label["height"] <= value["y"] or value["y"] + value["height"] <= label["y"]
    )
    assert apart
    set_slider(page, SIG_SLIDER, 0)
    assert text(page, clip) == ""


def test_relativity_slider_results_and_reset(open_page):
    page = open_page().page
    # It starts at one day, so the effect is already showing (improvement 10).
    assert page.locator(REL_SLIDER).input_value() == "24"
    assert "38" in text(page, f"{REL} [data-id=gap]")
    assert "11 km" in text(page, f"{REL} [data-id=range]")
    assert text(page, f"{REL} [data-id=trusted-badge]") == "Fix is far off"
    assert text(page, f"{REL} [data-id=solved-badge]") == "Good fix"
    set_slider(page, REL_SLIDER, 0)
    assert text(page, f"{REL} [data-id=range]") == "0 m"
    assert text(page, f"{REL} [data-id=solved]") == "0 m off"
    assert text(page, f"{REL} [data-id=sentence]").startswith("No gap yet")
    page.locator(f"{REL} [data-id=reset]").click()
    settle(page)
    assert text(page, f"{REL} [data-id=msg-reset]") == "Back to the start: one day."
    assert page.locator(REL_SLIDER).input_value() == "24"
    assert "11 km" in text(page, f"{REL} [data-id=range]")


def test_relativity_never_says_gain_longer_or_shorter(open_page):
    page = open_page().page
    set_slider(page, REL_SLIDER, 24)
    words = text(page, REL).lower()
    for word in ("gain", "longer", "shorter"):
        assert word not in words


def test_no_overflow_and_no_errors_at_phone_width(open_page):
    site = open_page(width=390)
    page = site.page
    set_slider(page, GEO_SLIDER, 100)
    set_slider(page, SIG_SLIDER, 24)
    set_slider(page, REL_SLIDER, 24)
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    assert site.errors == []
