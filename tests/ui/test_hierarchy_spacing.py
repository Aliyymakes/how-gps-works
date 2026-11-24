"""Improvements 6 and 7 of docs/ui-redesign.md: headings lead, bridges go quiet, card spacing."""

LINK_AND_H2 = """() => {
  const rows = [];
  const muted = getComputedStyle(document.documentElement).getPropertyValue('--text-muted').trim();
  const probe = document.createElement('span');
  probe.style.color = muted;
  document.body.append(probe);
  const mutedRgb = getComputedStyle(probe).color;
  probe.remove();
  for (const bridge of document.querySelectorAll('.link-line')) {
    const h2 = bridge.nextElementSibling.querySelector('h2');
    const before = bridge.previousElementSibling.getBoundingClientRect();
    const b = bridge.getBoundingClientRect();
    const h = h2.getBoundingClientRect();
    const word = getComputedStyle(bridge.querySelector('strong'));
    rows.push({
      h2Size: parseFloat(getComputedStyle(h2).fontSize),
      h2Weight: getComputedStyle(h2).fontWeight,
      bridgeSize: parseFloat(getComputedStyle(bridge).fontSize),
      bridgeColor: getComputedStyle(bridge).color,
      bridgeWeight: getComputedStyle(bridge).fontWeight,
      wordColor: word.color,
      wordWeight: word.fontWeight,
      mutedRgb,
      above: b.top - before.bottom,
      below: h.top - b.bottom,
      label: (h2.parentElement.querySelector('.label') || {}).textContent,
    });
  }
  return rows;
}"""

LARGEST_TEXT = """(sel) => {
  const root = document.querySelector(sel);
  const size = (e) => parseFloat(getComputedStyle(e).fontSize);
  const h2 = size(root.querySelector('h2'));
  return [...root.querySelectorAll('*')]
    // The big result numbers (.num, 32 px) are readings, not prose: they are the one thing allowed to match h1.
    .filter((e) => e.offsetParent && !e.closest('svg') && !e.classList.contains('num') && e.textContent.trim())
    .every((e) => size(e) <= h2);
}"""


def test_headings_lead_and_bridges_go_quiet(open_page):
    page = open_page().page
    rows = page.evaluate(LINK_AND_H2)
    assert len(rows) == 3
    for row in rows:
        assert row["h2Size"] == 24 and row["h2Weight"] == "600"
        assert row["h2Size"] > row["bridgeSize"] == 18
        assert row["bridgeColor"] == row["mutedRgb"] and row["wordColor"] == row["mutedRgb"]
        assert row["bridgeWeight"] == "400" and row["wordWeight"] == "500"
        assert row["below"] < row["above"]


def test_part_labels_sit_above_each_heading(open_page):
    page = open_page().page
    assert page.locator("h1").evaluate("h => h.previousElementSibling.textContent") == "Part 1 of 4"
    assert [r["label"] for r in page.evaluate(LINK_AND_H2)] == ["Part 2 of 4", "Part 3 of 4", "Part 4 of 4"]


def test_h2_is_the_largest_text_in_its_section(open_page):
    page = open_page().page
    for step in ["#step-geometry", "#step-signal", "#step-relativity"]:
        assert page.evaluate(LARGEST_TEXT, step), step
