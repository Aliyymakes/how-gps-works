"""Real-browser tests of the page. They only run with UI_TESTS=1 and Playwright installed,
so the normal `python -m pytest -q` never starts a browser.

The page is opened at its live address, but the files are answered from this folder's repo
(page.route), and the Pyodide downloads are cached on disk in tests/ui/.cdn-cache/.
"""
import hashlib
import importlib.util
import json
import mimetypes
import os
import pathlib

import pytest

ENABLED = os.environ.get("UI_TESTS") == "1" and importlib.util.find_spec("playwright") is not None
collect_ignore_glob = [] if ENABLED else ["test_*.py"]

ROOT = pathlib.Path(__file__).resolve().parents[2]
CDN_DIR = pathlib.Path(__file__).parent / ".cdn-cache"
LIVE = "https://aliyymakes.github.io/how-gps-works/"


class Site:
    """One open page. `cdn` is "cache" (use the disk cache), "live" (real network, no disk cache,
    nothing written) or "block" (fail every CDN request)."""

    def __init__(self, page, cdn, delay_ms, missing):
        self.page = page
        self.cdn = cdn
        self.delay_ms = delay_ms
        self.missing = missing  # repo-relative paths that answer 404
        self.errors = []
        page.on("pageerror", lambda error: self.errors.append("pageerror: " + str(error)))
        page.on("console", self._on_console)
        page.route(LIVE + "**", self._local)
        page.route("https://cdn.jsdelivr.net/**", self._remote)

    def _on_console(self, message):
        # While the CDN is blocked on purpose, the failed downloads are expected noise.
        if message.type == "error" and self.cdn != "block":
            self.errors.append("console.error: " + message.text)

    def _local(self, route):
        rel = route.request.url[len(LIVE):].split("?")[0] or "index.html"
        file = ROOT / rel
        if rel in self.missing or not file.is_file():
            route.fulfill(status=404, body="")
        else:
            route.fulfill(body=file.read_bytes(), content_type=mimetypes.guess_type(str(file))[0] or "text/plain")

    def _remote(self, route):
        url = route.request.url
        if self.cdn == "block":
            return route.abort()
        if self.delay_ms:
            # wait_for_timeout lets other requests be answered meanwhile; time.sleep froze them all
            self.page.wait_for_timeout(self.delay_ms)
        if self.cdn == "live":
            return route.continue_()
        key = CDN_DIR / hashlib.sha1(url.encode()).hexdigest()
        meta = key.with_suffix(".json")
        if key.exists() and meta.exists():
            saved = json.loads(meta.read_text())
            return route.fulfill(status=saved["status"], headers=saved["headers"], body=key.read_bytes())
        try:
            response = route.fetch()
        except Exception:
            return route.abort()
        body = response.body()
        skip = ("content-encoding", "content-length", "transfer-encoding")
        headers = {k: v for k, v in response.headers.items() if k.lower() not in skip}
        CDN_DIR.mkdir(exist_ok=True)
        key.write_bytes(body)
        meta.write_text(json.dumps({"status": response.status, "headers": headers}))
        route.fulfill(status=response.status, headers=headers, body=body)

    def wait_ready(self):
        self.page.wait_for_function("document.getElementById('clock').disabled === false", timeout=120000)
        self.page.wait_for_timeout(500)  # let the first drawing frame land


@pytest.fixture(scope="session", params=["chromium", "webkit"])
def browser(request):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = getattr(playwright, request.param).launch()
        yield browser
        browser.close()


@pytest.fixture
def open_page(browser):
    """open_page(width=1200, cdn="cache", delay_ms=0, missing=(), wait=True) returns a Site."""
    contexts = []

    def open_it(width=1200, cdn="cache", delay_ms=0, missing=(), wait=True):
        context = browser.new_context(viewport={"width": width, "height": 900})
        contexts.append(context)
        site = Site(context.new_page(), cdn, delay_ms, set(missing))
        site.page.goto(LIVE)
        if wait:
            site.wait_ready()
        return site

    yield open_it
    for context in contexts:
        context.close()
