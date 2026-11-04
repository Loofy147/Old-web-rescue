# Pilot 003 — Pixel Atlas Run Results

**Verification date:** 2026-11-04  
**Branch:** `feat/pilot-003-pixel-atlas`

## Unit tests

`node --test tests/pixel-atlas-core.test.mjs`

<badge>18/18 PASS</badge>

Coverage includes:
- image/map/usemap extraction and source-attribute retention
- relative, root-relative and absolute URL normalization
- unsafe protocol rejection
- Wayback replacement detection and original URL recovery, including wrapped query strings
- alt, aria-label and title-only label classification
- empty/missing labels
- duplicate normalized destinations
- rectangle, circle, polygon and default geometry
- malformed coordinate counts and non-numeric values
- missing href and malformed/incomplete areas
- orphan areas outside a map
- map id/name association
- empty documents
- fake markup inside comments, scripts, textarea, title and legacy raw-text elements
- checked-in synthetic fixture counts

## Browser smoke

`python browser-smoke.py` — PASS using Python Playwright + system Chromium.

The container's localhost navigation policy blocked a temporary test server with `ERR_BLOCKED_BY_ADMINISTRATOR`; the smoke test therefore embeds the exact local HTML, CSS and JavaScript into an in-memory document. This avoids the blocked server hop and does not contact external services.

| Check | Result |
|---|---|
| Page title and primary screen | PASS |
| Synthetic fixture import and inventory | PASS — 8 regions |
| Archived/original destination distinction | PASS — 1 archive replacement |
| Source-label classification | PASS — 4 source labels; 4 title-only/missing labels |
| Search/filter and empty/full restoration | PASS |
| Keyboard selection and geometry highlight | PASS |
| Local HTML file input | PASS |
| JSON export and provenance | PASS |
| Unsafe `javascript:` link withheld | PASS |
| Pasted script not executed | PASS |
| External requests | 0 |
| Browser page errors | 0 |
| Horizontal overflow at 320 / 390 / 1440 px | 0 |

Screenshots were captured locally for desktop and mobile review; generated screenshots are not committed to keep the repository source-focused.

## Remaining verification

- No assistive-technology user or manual screen-reader study has been performed.
- No formal WCAG conformance assessment has been performed.
- The parser is a limited tokenizer, not a complete HTML5 parsing implementation.
- The imported source image is not loaded; the coordinate view is schematic.
- Extracted destinations are not crawled or automatically checked for availability.
