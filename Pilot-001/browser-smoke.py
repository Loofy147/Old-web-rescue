"""Optional Playwright smoke test; requires Python Playwright and Chromium."""
from pathlib import Path
import re
import shutil
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
html = (ROOT / "index.html").read_text()
css = (ROOT / "styles.css").read_text()
engine = re.sub(r"\bexport\s+", "", (ROOT / "game-engine.mjs").read_text())
app = re.sub(r"^import\s+.*?;\s*", "", (ROOT / "app.mjs").read_text(), count=1, flags=re.S)
html = re.sub(r'\s*<link rel="stylesheet" href="styles.css">', "", html)
html = re.sub(r'\s*<script type="module" src="app.mjs"></script>', "", html)

with sync_playwright() as p:
    launch_options = {"headless": True, "args": ["--no-sandbox"]}
    # Prefer a system Chromium when present; otherwise use Playwright's managed browser.
    system_chromium = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
    if system_chromium:
        launch_options["executable_path"] = system_chromium
    browser = p.chromium.launch(**launch_options)
    page = browser.new_page(viewport={"width": 390, "height": 844})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.set_content(html, wait_until="load")
    page.add_style_tag(content=css)
    # Fixed RNG makes the first two cards a known mismatch, so the browser test
    # always exercises concealment before it searches for and finds the pair.
    page.add_script_tag(content="Math.random = () => 0.5;")
    page.add_script_tag(content=engine + "\n" + app)

    cards = page.locator(".memory-card")
    assert cards.count() == 16
    assert page.locator("#pairs").inner_text() == "0 / 8"
    assert page.locator("html").get_attribute("lang") == "en"
    assert page.locator("#game-status").get_attribute("aria-live") == "polite"
    assert page.locator(".memory-card").evaluate_all("cards => cards.every(card => card.tagName === 'BUTTON' && card.getAttribute('aria-label'))")

    # First prove that a mismatch is announced and concealed.
    first = cards.nth(0)
    mismatch = cards.nth(1)
    first.focus()
    page.keyboard.press("Enter")
    first_label = first.get_attribute("aria-label").split(",")[0]
    mismatch.focus()
    page.keyboard.press("Space")
    assert page.locator("#moves").inner_text() == "1"
    assert page.locator("#game-status").inner_text().startswith("Not a match.")
    page.wait_for_timeout(950)
    assert first.get_attribute("aria-pressed") == "false"
    assert mismatch.get_attribute("aria-pressed") == "false"

    # Then keyboard-play until the matching card is found.
    first.focus()
    page.keyboard.press("Enter")
    candidates = 1
    for index in range(2, cards.count()):
        if first.get_attribute("aria-pressed") == "false":
            first.focus()
            page.keyboard.press("Enter")
            page.wait_for_timeout(80)
        card = cards.nth(index)
        card.focus()
        page.keyboard.press("Space")
        page.wait_for_timeout(80)
        candidates += 1
        if card.get_attribute("aria-label").split(",")[0] == first_label:
            assert first.get_attribute("aria-disabled") == "true"
            break
        page.wait_for_timeout(950)
    else:
        raise AssertionError("No matching pair found during keyboard play")

    assert page.locator("#pairs").inner_text() == "1 / 8"
    assert int(page.locator("#moves").inner_text()) == candidates
    assert page.locator("#game-status").inner_text().startswith("Match found:")
    assert not errors, errors
    assert page.locator("button").count() == 17
    page.screenshot(path=str(ROOT / "mobile-preview.png"), full_page=True)

    page.locator("#new-game").click()
    assert page.locator("#pairs").inner_text() == "0 / 8"
    assert page.locator("#moves").inner_text() == "0"

    page.set_viewport_size({"width": 1440, "height": 1000})
    page.screenshot(path=str(ROOT / "desktop-preview.png"), full_page=True)
    grid = page.locator("#game-grid").bounding_box()
    assert grid and grid["width"] >= 500

    page.set_viewport_size({"width": 320, "height": 700})
    assert page.evaluate("document.documentElement.scrollWidth === document.documentElement.clientWidth")

    # Verify the one-file build independently: no project CSS/JS URLs and the
    # game initializes directly from the embedded source.
    standalone_html = (ROOT / "memory-reboot.html").read_text()
    assert not re.search(r'<(?:script|link)[^>]+(?:src|href)="(?:styles\.css|app\.mjs|game-engine\.mjs)"', standalone_html, re.I)
    standalone_page = browser.new_page(viewport={"width": 390, "height": 844})
    standalone_errors = []
    standalone_page.on("pageerror", lambda error: standalone_errors.append(str(error)))
    standalone_page.set_content(standalone_html, wait_until="load")
    assert standalone_page.locator(".memory-card").count() == 16
    standalone_page.locator(".memory-card").nth(0).focus()
    standalone_page.keyboard.press("Enter")
    assert standalone_page.locator(".memory-card").nth(0).get_attribute("aria-pressed") == "true"
    assert not standalone_errors, standalone_errors

    print({"result": "PASS", "cards": 16, "keyboard_pair": True, "mismatch_conceal": True, "candidate_attempts": candidates, "restart": True, "semantic_controls": True, "widths": [320, 390, 1440], "standalone_file": True, "page_errors": errors + standalone_errors})
    browser.close()
