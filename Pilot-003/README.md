# Old Web Rescue Lab — Pilot 003: Pixel Atlas

**Status:** functional prototype · **Version:** 0.1.0 · **Issue:** [#1](https://github.com/Loofy147/Old-web-rescue/issues/1)

Pixel Atlas converts legacy HTML image maps into a searchable inventory and a schematic coordinate view. It is designed for research and remediation planning, not for certifying accessibility or cloning the source website.

## What it does

- Accepts pasted HTML or a local `.html`, `.htm`, `.xhtml` or `.txt` file (maximum 5 MB).
- Parses `<map>`, `<area>` and matching `<img usemap>` relationships in the browser.
- Retains raw attributes, shape, coordinates, source `alt`, `aria-label` and `title` values, map references and destination metadata.
- Resolves relative `href` values only when the investigator supplies an absolute HTTP(S) base URL. The base URL is never fetched.
- Distinguishes original destinations, archive replacements and other explicitly rewritten destinations.
- Recovers Wayback-wrapped original URLs when possible, including query strings, while retaining the archive URL.
- Flags title-only candidate labels, missing/empty alternatives, duplicate destinations, invalid/unsafe destinations and malformed geometry.
- Preserves orphan `<area>` elements as unassociated records rather than silently dropping them.
- Displays every region in a semantic searchable inventory. Keyboard-operable buttons select a region and highlight its geometry in the schematic view.
- Exports the complete evidence record as JSON or the currently filtered inventory as CSV.

## Run locally

Requires a modern browser. For the module-based app, serve this folder locally:

```bash
cd Pilot-003
python -m http.server 8000
```

Open `http://localhost:8000` in your browser. No backend, package manager, account, API key or third-party script is required.

The **Load synthetic example** action supplies a local demonstration with normal, duplicate, title-only, missing-label, archived, malformed-geometry and unsafe-scheme cases. It contains no third-party artwork or copied homepage content.

## Tests

Pure parser tests use Node's built-in test runner:

```bash
node --test tests/pixel-atlas-core.test.mjs
```

Optional browser smoke test (Python Playwright + Chromium required):

```bash
python browser-smoke.py
```

The browser smoke test uses an in-memory document containing the checked-in source files. It verifies synthetic-data import, search, keyboard selection, local file import, JSON export, unsafe URL handling, script-injection resistance, zero external requests, zero page errors and no horizontal overflow at 320, 390 and 1440 px.

## Parser and evidence limitations

The parser is a dependency-free, bounded tokenizer for image-map inspection, not a standards-complete HTML5 parser or browser DOM implementation. It skips comments and raw-text element contents, but heavily malformed/nested documents may still be interpreted differently by a browser. Compare the extracted records with the original source before using them for repairs or migration.

The schematic geometry view is not a screenshot or source image preview. It plots valid coordinates using the associated image's declared dimensions where available, or a derived coordinate extent otherwise. The source image is not fetched. `default` areas cover the entire map and are not spatially distinguishable from one another in the schematic.

A `title` value is presented as a review candidate, never as a verified text alternative. A non-empty `alt` or `aria-label` is treated as source-provided text, not proof that the description is meaningful. Humans must review the wording and context. The tool does not claim WCAG conformance.

Only HTTP(S) destination links are offered as manually activated external links. `javascript:`, `data:`, `file:`, `mailto:` and other non-HTTP(S) schemes are retained in raw attributes where present but are not made clickable. No extracted URL is crawled, checked or opened automatically.

## Privacy and execution model

- HTML is parsed in the browser as text.
- Scripts, styles and embedded page code from the supplied source are not executed.
- The application uses `textContent` and DOM element creation for imported values; it does not inject source HTML into the page.
- No upload, backend, analytics, telemetry, link crawler or external asset request is used.
- External links are opened only after a deliberate user click, in a new tab with `noopener noreferrer` and `no-referrer`.

## File map

- `index.html` — Pixel Atlas UI
- `styles.css` — responsive interface and reduced-motion handling
- `app.mjs` — local browser workflow, searchable list, geometry view and exports
- `pixel-atlas-core.mjs` — parsing, URL provenance, label classification and geometry validation
- `tests/pixel-atlas-core.test.mjs` — Node unit tests
- `fixtures/demo-image-map.html` — synthetic image-map fixture
- `browser-smoke.py` — optional in-memory Playwright flow test
- `RUN_RESULTS.md` — latest verification record
