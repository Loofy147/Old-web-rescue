"""Optional in-memory browser smoke test for Pixel Atlas.

Requires Python Playwright + Chromium. The browser receives the local source
files as an in-memory document, avoiding local-server navigation and any
external network dependency.
"""
from __future__ import annotations

import json
import os
import re
import shutil
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUTPUT = Path(os.environ.get("PIXEL_ATLAS_SCREENSHOTS", "/tmp/pixel-atlas-browser-smoke"))
OUTPUT.mkdir(parents=True, exist_ok=True)

html = (ROOT / "index.html").read_text(encoding="utf-8")
css = (ROOT / "styles.css").read_text(encoding="utf-8")
core = re.sub(r"\bexport\s+", "", (ROOT / "pixel-atlas-core.mjs").read_text(encoding="utf-8"))
app = (ROOT / "app.mjs").read_text(encoding="utf-8")
app = re.sub(r"^import\s+.*?;\s*", "", app, count=1, flags=re.S)
html = re.sub(r'\s*<link rel="stylesheet" href="styles.css">', "", html)
html = re.sub(r'\s*<script type="module" src="app.mjs"></script>', "", html)

with sync_playwright() as playwright:
    chromium = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
    launch_options = {"headless": True, "args": ["--no-sandbox"]}
    if chromium:
        launch_options["executable_path"] = chromium
    browser = playwright.chromium.launch(**launch_options)
    page = browser.new_page(viewport={"width": 1440, "height": 1100}, accept_downloads=True)
    errors: list[str] = []
    external_requests: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("request", lambda request: external_requests.append(request.url) if request.url.startswith(("http://", "https://")) else None)
    page.set_content(html, wait_until="load")
    page.add_style_tag(content=css)
    page.add_script_tag(content=core)
    page.add_script_tag(content=app)

    assert page.title() == "Pixel Atlas — Old Web Rescue Lab"
    assert page.locator("#page-title").inner_text().startswith("Every region")
    assert page.locator("#results").is_hidden()
    assert page.locator("#analyze-button").is_visible()

    page.get_by_role("button", name="Load synthetic example").click()
    page.get_by_role("button", name="Analyze image map").click()
    page.locator("#results").wait_for(state="visible")
    assert page.locator("#metric-total").inner_text() == "8"
    assert page.locator("#region-list .region-card").count() == 8
    assert page.locator("#metric-archive").inner_text() == "1"
    assert page.locator("#metric-verified").inner_text() == "4"
    assert page.locator("#metric-review").inner_text() == "4"
    assert page.locator(".geometry-svg .geometry-region").count() == 7
    assert page.locator("#import-status").inner_text().startswith("Inspection complete")

    # Search is live, keeps provenance distinctions and restores the full list.
    search = page.locator("#region-search")
    search.fill("archive replacement")
    assert page.locator("#region-list .region-card").count() == 1
    assert page.locator("#region-count").inner_text() == "1/8"
    assert page.get_by_text("Open archived target").count() == 1
    search.fill("")
    assert page.locator("#region-list .region-card").count() == 8

    # Keyboard action selects a region and highlights its geometry.
    region_button = page.get_by_role("button", name="Locate region 3: Reading circle events")
    region_button.focus()
    page.keyboard.press("Enter")
    assert region_button.get_attribute("aria-pressed") == "true"
    assert page.locator(".geometry-svg .geometry-region.is-selected").count() == 1

    # Unsafe schemes are not surfaced as executable/clickable anchors.
    unsafe_card = page.locator(".region-card").filter(has_text="Unsafe script destination")
    assert unsafe_card.count() == 1
    assert unsafe_card.locator('a[href^="javascript:"]').count() == 0
    assert unsafe_card.get_by_text("No safe HTTP(S) destination").count() == 1

    # The parser never injects or executes content pasted into the source field.
    hostile_source = '<script>window.__PIXEL_ATLAS_PWNED = true;</script><map><area href="https://example.org" alt="Safe label" shape="default"></map>'
    page.locator("#source-html").fill(hostile_source)
    page.get_by_role("button", name="Analyze image map").click()
    assert page.locator("#metric-total").inner_text() == "1"
    assert page.evaluate("window.__PIXEL_ATLAS_PWNED === true") is False
    assert page.locator("script").count() == 2  # Only the trusted local parser and app scripts.

    # Exercise the real local-file input with a small temporary HTML file.
    upload_path = OUTPUT / "pixel-atlas-upload-fixture.html"
    upload_path.write_text('<map name="uploaded"><area href="/from-file" alt="Imported from file" shape="default"></map>', encoding="utf-8")
    page.locator("#source-file").set_input_files(str(upload_path))
    assert page.locator("#file-name").inner_text() == upload_path.name
    page.get_by_role("button", name="Analyze image map").click()
    assert page.locator("#metric-total").inner_text() == "1"
    assert page.get_by_text("Imported from file").count() == 1

    # Restore demonstration data before the export and viewport checks.
    page.get_by_role("button", name="Load synthetic example").click()
    page.get_by_role("button", name="Analyze image map").click()
    with page.expect_download() as download_info:
        page.get_by_role("button", name="Export JSON").click()
    download = download_info.value
    downloaded = Path(download.path()).read_text(encoding="utf-8")
    exported = json.loads(downloaded)
    assert exported["summary"]["total"] == 8
    assert exported["provenance"]["networkRequests"] == 0

    # Search shortcut and Escape reset are keyboard operable.
    page.locator("body").click(position={"x": 10, "y": 10})
    page.keyboard.press("/")
    assert page.locator("#region-search").evaluate("el => document.activeElement === el")
    page.locator("#region-search").fill("rare books")
    page.keyboard.press("Escape")
    assert page.locator("#region-count").inner_text() == "8/8"

    page.screenshot(path=str(OUTPUT / "pixel-atlas-desktop.png"), full_page=True)
    viewport_results = []
    for width in (320, 390, 1440):
        page.set_viewport_size({"width": width, "height": 900})
        overflow = page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
        assert not overflow, f"Horizontal overflow at {width}px"
        viewport_results.append({"width": width, "overflow": overflow})
        if width == 390:
            page.screenshot(path=str(OUTPUT / "pixel-atlas-mobile.png"), full_page=True)

    assert external_requests == [], f"Unexpected external request(s): {external_requests}"
    assert errors == [], f"Browser errors: {errors}"
    print(json.dumps({
        "result": "PASS",
        "page_title": page.title(),
        "regions": 8,
        "archive_replacements": 1,
        "source_labels": 4,
        "needs_review_or_missing": 4,
        "keyboard_selection": True,
        "search_filter": True,
        "json_export": True,
        "local_file_import": True,
        "unsafe_links_blocked": True,
        "source_injection_prevented": True,
        "viewports": viewport_results,
        "external_requests": len(external_requests),
        "page_errors": errors,
        "screenshots": [str(OUTPUT / "pixel-atlas-desktop.png"), str(OUTPUT / "pixel-atlas-mobile.png")],
    }, indent=2))
    browser.close()
