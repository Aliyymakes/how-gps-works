"""Improvements 3 (geometry part) and 8 (docs/ui-redesign.md): the sky picture has a "What you're looking at" line,
and geometry and signal are joined by one bridge. Every test runs in Chromium and WebKit (see conftest.py)."""
GEO = "#step-geometry"


def test_looking_line_sits_just_above_the_sky_picture(open_page):
    page = open_page().page
    looking = page.locator(f"{GEO} .looking")
    assert looking.count() == 1
    assert looking.is_visible()
    assert looking.evaluate("e => getComputedStyle(e).opacity") == "1"
    text = looking.inner_text().replace(" ", " ")
    assert text.startswith("What you're looking at:")
    assert "The centre is straight overhead, the edge is the horizon." in text
    assert page.locator(f"{GEO} .geo-note", has_text="Edge is the horizon").count() == 0
    line = looking.bounding_box()
    sky = page.locator(f"{GEO} [data-id=sky]").bounding_box()
    gap = sky["y"] - (line["y"] + line["height"])
    assert 0 <= gap <= 40, gap
    assert "Sky, seen from below" in page.locator(f"{GEO} [data-id=sky]").get_attribute("aria-label")


def test_one_bridge_between_geometry_and_signal(open_page):
    page = open_page().page
    closing = page.locator(f"{GEO} .geo-closing").inner_text()
    assert "next" not in closing.lower()
    assert closing.endswith("Bunched, they multiply.")
    between = page.evaluate("""() => {
      let n = document.querySelector('#step-geometry').nextElementSibling, found = [];
      while (n && n.id !== 'step-signal') { if (n.matches('p')) found.push(n.className); n = n.nextElementSibling; }
      return found;
    }""")
    assert between == ["link-line"]
