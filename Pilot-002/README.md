# Old Web Rescue Lab — Pilot 002

## GeoCities Explorer + Legacy HTML Triage 0.3

A small, dependency-free Python CLI for discovering, revisiting, and exporting pages preserved in Arquivo.pt's GeoCities collection.

### Why this exists

The pilot moved from visual nostalgia to evidence-based digital archaeology. Arquivo.pt exposes a dedicated GeoCities collection through its public APIs. The Explorer turns those APIs into a repeatable research workflow:

1. Search preserved page text and metadata.
2. Retrieve the capture history for a known original URL.
3. Search archived images and retain the original page/image archive links.
4. Export results to JSON or CSV for later auditing.
5. Run a separate local structural triage over saved legacy HTML, including image-map areas, missing alternatives, legacy tags, frames, document language and viewport metadata.

The project is metadata discovery, not a full browser or accessibility auditor. It does not execute archived JavaScript, download complete sites, test security, or guarantee that every image/script dependency was preserved.

## Requirements

- Python 3.10 or later
- Standard library only
- Internet connection when calling the live Arquivo.pt API

### Search archived pages

```bash
python geocities_explorer.py search "personal diary" --limit 5
python geocities_explorer.py search "computers" --from-date 20090101 --to-date 20091231 --format csv --output exports/computers-2009.csv
```

### Inspect the capture history for a page

```bash
python geocities_explorer.py history "https://geocities.com/kreisler76/diary.html" --format json
```

### Search archived images

```bash
python geocities_explorer.py images "dogs" --limit 10
python geocities_explorer.py images "dog portrait" --format csv --output exports/dog-images.csv
```

### Search all Arquivo.pt collections

By default, searches are restricted to `collection=Geocities`. To search across collections:

```bash
python geocities_explorer.py --all-collections search "personal diary" --limit 10
```

### Audit saved legacy HTML

Save a page's HTML source locally (for example, from a public archive replay), then run:

```bash
python legacy_html_audit.py saved-page.html
python legacy_html_audit.py saved-page.html --json
```

The auditor reports structural signals only. It does **not** claim WCAG conformance and does not replace keyboard, screen-reader, contrast, interaction or human testing. It makes no network requests and does not execute page scripts.

### Output formats

- `table` — readable terminal output (default)
- `json` — result envelope with estimate, offset and normalized records
- `csv` — export records for spreadsheets or downstream analysis

## API discipline

The client follows the official Arquivo.pt API contracts:

- Text search: `https://arquivo.pt/textsearch`
- Image search: `https://arquivo.pt/imagesearch`
- `collection=Geocities` scopes text and image searches to the GeoCities collection.
- URL history uses the `versionHistory` query parameter.
- Text-search maximum: 500 records/request.
- Image-search maximum: 200 records/request.

**Rate-limit warning:** Arquivo.pt publishes limits of 250 text/URL API requests per 60 seconds and 400 image requests per 60 seconds per source IP. The API documentation warns that exceeding a limit may result in a permanent IP block. This client sends one request per command and does not automatically paginate, retry, or bulk crawl. Increase offsets manually and keep request volume conservative.

## Verification

Run the local test suite:

```bash
python -m unittest discover -s tests -v
python -m py_compile geocities_explorer.py legacy_html_audit.py
```

The tests validate query construction, GeoCities scoping, capture-timestamp normalization, URL history, image/page archive links, CSV serialization, transport errors, API page-size limits, and structural HTML/image-map diagnostics. Network behavior is unit-tested with controlled responses; the runtime container used to build this package has no direct DNS/network access, so live API access is not claimed as a locally executed CLI test. The same API endpoints and query parameters were independently exercised during research through live Arquivo.pt responses.

## Files

- `geocities_explorer.py` — CLI and API client
- `legacy_html_audit.py` — local structural HTML triage tool
- `tests/` — 23 unit tests across the API client and HTML auditor
- `fixtures/live-sample.json` — small sample of live GeoCities search observations collected during the field study
- `fixtures/million-dollar-homepage-live-audit.json` — direct HTML observations from the Million Dollar Homepage inspection
- `fixtures/legacy-image-map-sample.html` — small image-map fixture used by the structural auditor
- `FIELD_NOTES.md` — captured-page walkthroughs and mobile usability observations
- `SOURCES.md` — authoritative sources and retrieval notes
- `RUN_RESULTS.md` — exact local verification results

## Use and preservation cautions

Archived pages can contain personal information, copyrighted images, external links, and content that was not intended for modern redistribution. Use archive links for research and preserve the source/creator attribution. Do not mirror or republish media merely because it is retrievable. An archive timestamp is a capture date, not necessarily the page's publication date.
