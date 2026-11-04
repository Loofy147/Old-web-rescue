# Old Web Rescue Lab

**Canonical repository:** https://github.com/Loofy147/Old-web-rescue  
**Current baseline:** v0.2.0 · **Next pilot:** 003 — Pixel Atlas  
**Purpose:** evidence-led web archaeology, structural HTML triage, preservation research and independent modernization prototypes.

Old Web Rescue Lab investigates websites and web experiences that survived, became outdated, partially broke, or disappeared. We follow real user journeys, capture reproducible evidence, separate website defects from inspection-tool limitations, and build independent prototypes when the findings justify it.

This is not a nostalgia gallery or a generic website-score service. The objective is to recover useful interaction patterns, identify lost or inaccessible functionality, and convert evidence into tested engineering work.

## Pilots

### Pilot 001 — Memory Reboot
An independent, offline memory-matching game that replaces only the generic interaction pattern blocked by the Shockwave dependency in a 1996 Space Jam page. It uses no film characters, assets, music, copied source code or branding.

Start with `Pilot-001/memory-reboot.html`.

### Pilot 002 — GeoCities Explorer + Legacy HTML Triage
Two standard-library Python tools:
- `Pilot-002/geocities_explorer.py`: search Arquivo.pt's GeoCities collection, inspect capture histories and search archived images; export JSON/CSV.
- `Pilot-002/legacy_html_audit.py`: inspect saved HTML for structural signals such as missing text alternatives, image-map problems, legacy markup, frames and missing document metadata.

### Pilot 003 — Pixel Atlas
A local-only image-map inspector that turns legacy `<map>` / `<area>` markup into a searchable region inventory, a coordinate schematic, label-quality warnings and provenance-aware original/archive destination links.

Start with `Pilot-003/README.md`.

## Run locally

Pilot 001:
```bash
cd Pilot-001
node --test game-engine.test.mjs
python browser-smoke.py  # optional; requires Playwright + Chromium
```

Pilot 002:
```bash
cd Pilot-002
python -m unittest discover -s tests -v
python -m py_compile geocities_explorer.py legacy_html_audit.py
```

Pilot 003:
```bash
cd Pilot-003
node --test tests/pixel-atlas-core.test.mjs
python -m http.server 8000
```
Open `http://localhost:8000`. Optional browser smoke: `python browser-smoke.py` (requires Python Playwright + Chromium).

## Verification baseline

| Pilot | Verification |
|---|---|
| 001 | 6/6 Node tests; keyboard browser smoke; 320/390/1440 px; zero page errors |
| 002 | 23/23 Python tests; compilation; fixture audit |
| 003 | 18/18 Node tests; Playwright smoke: local import, search, keyboard selection, exports, unsafe-link blocking, source-injection resistance; 320/390/1440 px; zero external requests and page errors |

GitHub Actions runs Pilot 001 Node tests, Pilot 002 Python tests on 3.10 and 3.12, and Pilot 003 parser tests on Node 22. Browser smoke scripts are optional local checks and are not CI gates.

## Research discipline

Claims use explicit evidence labels: `ESTABLISHED`, `EXPERIMENTALLY_SUPPORTED`, `USER_REPORTED`, `INFERENCE`, `HYPOTHESIS`, `CONTRADICTED`, `UNKNOWN`, and `OPEN`. Record exact URLs, capture timestamps, viewports, journeys, methods, failures, tool limits and next discriminating tests.

The HTML auditors are structural triage, **not** WCAG conformance checkers. Screenshots, HTML validation and automated tools cannot establish complete accessibility. Keyboard, screen-reader, contrast and human evaluation remain separate.

Pixel Atlas uses a bounded tokenizer, not a standards-complete HTML5 parser. It does not run supplied scripts, upload source, crawl extracted links or fetch source images. A title is only a review candidate, not a verified text alternative. The coordinate display is schematic. See `Pilot-003/README.md`.

The Arquivo.pt CLI tests use controlled responses. Direct DNS/network access from the original build container was unavailable, so no live CLI request is claimed as a locally executed test; the API endpoints were independently exercised during research. Capture timestamps are archive dates, not proof of original publication dates.

## Preservation and rights

Archived content may contain personal information, copyrighted material and untrusted outbound links. Retrieval does not grant republication rights. The tools do not execute archived scripts or automatically visit extracted destinations. Do not bulk mirror or republish third-party material without a rights basis.

## Next

Pilot 003 implementation is tracked in [GitHub issue #1](https://github.com/Loofy147/Old-web-rescue/issues/1). Current implementation is on the `feat/pilot-003-pixel-atlas` branch for review.

See `RESEARCH_PROTOCOL.md`, `IP_AND_PRESERVATION.md`, `CONTRIBUTING.md`, and `CHANGELOG.md` for the operating rules and repository history.
