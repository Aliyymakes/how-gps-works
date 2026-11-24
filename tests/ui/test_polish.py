"""Issue #68: visual polish. Every test runs in Chromium and WebKit (see conftest.py)."""
import pytest

SLIDER_BLOCKS = ["#block-slider", "#step-geometry .slider", "#step-signal .slider", "#step-relativity .slider"]


@pytest.mark.parametrize("metres, words", [
    (0, "0 m"),
    (4.63, "4.6 m"),
    (520.34, "520 m"),
    (1561.2, "1,561 m"),
    (19766.9, "19,767 m"),
])
def test_format_metres(open_page, metres, words):
    page = open_page(wait=False).page
    got = page.evaluate("async (m) => (await import('./web/format.js')).formatMetres(m)", metres)
    assert got.replace(" ", " ") == words


def test_card_labels_do_not_touch_what_is_under_them_at_phone_width(open_page):
    page = open_page(width=390).page
    gaps = page.evaluate("""() => [...document.querySelectorAll('.card h2.label, .card h3.label')].map(label => {
      const next = label.nextElementSibling.getBoundingClientRect();
      return [label.textContent, next.top - label.getBoundingClientRect().bottom];
    })""")
    assert len(gaps) == 5  # ground map, sky, and the three signal headings
    for name, gap in gaps:
        assert gap >= 4, (name, gap)


def test_all_four_slider_blocks_look_the_same(open_page):
    page = open_page().page
    looks = page.evaluate("""(selectors) => selectors.map(s => {
      const block = getComputedStyle(document.querySelector(s));
      const card = getComputedStyle(document.querySelector(s).parentElement);
      return [block.borderTopWidth, block.padding, card.borderTopWidth, card.padding];
    })""", SLIDER_BLOCKS)
    assert all(look == looks[0] for look in looks), looks
