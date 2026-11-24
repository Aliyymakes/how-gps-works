"""Checks that every annotated file in docs/annotated/ quotes its source exactly.

Rules (see docs/annotated/how-to-read-code.md for what these files are):
  (a) every line inside a python/js/html/css code block must be a real line of the source;
  (b) every non-blank line of the source must be quoted somewhere in the annotation;
  (c) every source file must have an annotation file, unless it is listed in PENDING.
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
ANNOTATED = ROOT / "docs" / "annotated"
SKIP_DOCS = {"how-to-read-code.md", "reader-test.md"}
CHECKED_TAGS = {"python", "js", "html", "css"}
SHOWN = 10  # how many lines a failure message lists

# Source files whose annotation is not written yet. The main session empties
# this set as the docs land (mechanism docs are on other branches; web docs come later).
PENDING = {
    "index.html",
    "web/theme.css",
    *(f"web/{p.name}" for p in (ROOT / "web").glob("*.js")),
    *(f"mechanism/{p.name}" for p in (ROOT / "mechanism").glob("*.py")),
}


def source_files():
    found = [p.relative_to(ROOT).as_posix() for p in (ROOT / "mechanism").glob("*.py")]
    found += [p.relative_to(ROOT).as_posix() for p in (ROOT / "web").glob("*.js")]
    for name in ("web/theme.css", "index.html"):
        if (ROOT / name).exists():
            found.append(name)
    return sorted(found)


def parse_annotation(text):
    """Return (source path, list of stripped non-blank quoted lines)."""
    match = re.search(r"^Source: `([^`]+)`", text, re.MULTILINE)
    source = match.group(1) if match else None
    quoted, tag = [], None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            tag = stripped[3:].strip() if tag is None else None
            continue
        if tag in CHECKED_TAGS and stripped:
            quoted.append(stripped)
    return source, quoted


def source_lines(source_text):
    """(line number, stripped line) for each non-blank source line."""
    return [(n, l.strip()) for n, l in enumerate(source_text.splitlines(), 1) if l.strip()]


def check_unknown(source_text, quoted):
    """Rule (a): quoted lines that are not in the source."""
    real = {l for _, l in source_lines(source_text)}
    return [q for q in quoted if q not in real]


def check_missing(source_text, quoted):
    """Rule (b): source lines that are not quoted. Returns (line number, line)."""
    seen = set(quoted)
    return [(n, l) for n, l in source_lines(source_text) if l not in seen]


def format_missing(missing):
    shown = "\n".join(f"  line {n}: {l}" for n, l in missing[:SHOWN])
    more = f"\n  ... and {len(missing) - SHOWN} more" if len(missing) > SHOWN else ""
    return shown + more


ANNOTATION_FILES = (
    sorted(p for p in ANNOTATED.rglob("*.md") if p.name not in SKIP_DOCS)
    if ANNOTATED.exists()
    else []
)

PARAMS = [pytest.param(p, id=p.relative_to(ANNOTATED).as_posix()) for p in ANNOTATION_FILES] or [
    pytest.param(None, marks=pytest.mark.skip(reason="no annotation files yet"))
]


def load(path):
    source, quoted = parse_annotation(path.read_text(encoding="utf-8"))
    assert source, f"{path.name}: no 'Source: `...`' line found"
    source_path = ROOT / source
    assert source_path.exists(), f"{path.name}: source file {source} does not exist"
    return source, source_path.read_text(encoding="utf-8"), quoted


@pytest.mark.parametrize("path", PARAMS)
def test_quoted_lines_are_real(path):
    source, text, quoted = load(path)
    unknown = check_unknown(text, quoted)
    assert not unknown, (
        f"{path.name} quotes lines that are not in {source}:\n"
        + "\n".join(f"  {l}" for l in unknown[:SHOWN])
    )


@pytest.mark.parametrize("path", PARAMS)
def test_every_source_line_is_quoted(path):
    source, text, quoted = load(path)
    missing = check_missing(text, quoted)
    assert not missing, (
        f"{path.name} does not quote {len(missing)} line(s) of {source}:\n" + format_missing(missing)
    )


def test_every_source_has_an_annotation():
    missing = [
        src
        for src in source_files()
        if src not in PENDING and not (ANNOTATED / (src + ".md")).exists()
    ]
    assert not missing, "no annotation file in docs/annotated/ for: " + ", ".join(missing)


def test_selftest_catches_missing_and_invented_lines(tmp_path):
    src = tmp_path / "fake.py"
    src.write_text("x = 1\n\ndef f():\n    return x\n", encoding="utf-8")
    good = (
        "# fake.py, line by line\n\nSource: `fake.py`\n\n"
        "```python\nx = 1\ndef f():\n    return x\n```\n"
    )
    bad = (
        "Source: `fake.py`\n\n```python\nx = 1\ndef f():\n    return y\n```\n"
        "```text\nnot checked = 5\n```\n"
    )
    text = src.read_text(encoding="utf-8")

    source, quoted = parse_annotation(good)
    assert source == "fake.py"
    assert check_unknown(text, quoted) == []
    assert check_missing(text, quoted) == []

    _, quoted = parse_annotation(bad)
    assert check_unknown(text, quoted) == ["return y"]  # (a) invented line caught; text block ignored
    assert check_missing(text, quoted) == [(4, "return x")]  # (b) missing line caught, with its number
