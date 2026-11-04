# Run Results — Pilot 002

**Run date:** 2026-11-03

## Verification

| Check | Result |
|---|---:|
| `python -m unittest discover -s tests -v` | PASS — 23 tests |
| `python -m py_compile geocities_explorer.py legacy_html_audit.py` | PASS |
| `python legacy_html_audit.py fixtures/legacy-image-map-sample.html --json` | PASS — valid JSON report |
| Manual CLI help: Explorer | PASS |
| Manual CLI help: HTML auditor | PASS |

## Coverage

- GeoCities search query encoding and collection scoping.
- URL version-history request construction.
- Page and image metadata normalization.
- Empty and invalid API responses.
- CSV serialization and captured sample metadata.
- API item-count caps and transport failures.
- HTML doctype, language and viewport detection.
- Missing/empty `img` and image-map `area` alternatives.
- Image-map href/coords and map/usemap reference integrity, including HTML 4 `map name` support.
- Legacy element and frame counts.
- Heading-level inventory and explicit non-conformance scope note.

## Live-network limitation

The CLI's request layer is unit-tested with controlled responses. Direct network/DNS access from the build container was unavailable, so no claim is made that the Python CLI itself was executed successfully against the live service from this runtime. Actual Arquivo.pt page-search, version-history and image-search endpoints were independently exercised during the field study with live responses.
