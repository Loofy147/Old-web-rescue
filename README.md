# Old Web Rescue Lab

**Canonical repository:** https://github.com/Loofy147/Old-web-rescue  
**Baseline:** v0.2.0  
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

Example archive search:
```bash
python geocities_explorer.py search "personal diary" --limit 5
python geocities_explorer.py history "https://geocities.com/kreisler76/diary.html" --format json
python geocities_explorer.py images "dogs" --limit 10
```

Example local HTML triage:
```bash
python legacy_html_audit.py saved-page.html --json
```

## Verification baseline (2026-11-04)

| Check | Result |
|---|---:|
| Pilot 001 Node tests | 6/6 PASS |
| Pilot 001 browser smoke | PASS — 16 cards; keyboard match/mismatch recovery; restart; 320/390/1440 px; zero page errors |
| Pilot 002 Python tests | 23/23 PASS |
| Python compilation | PASS |
| HTML fixture audit output | Valid JSON |
| GitHub Actions | PASS — Node, Python 3.10 and 3.12, compilation and fixture validation |

Latest verified CI run: [GitHub Actions run #23](https://github.com/Loofy147/Old-web-rescue/actions/runs/41821030322).

The Playwright browser smoke remains an optional local check; it is not currently a CI job.

## Research discipline

Claims use explicit evidence labels: `ESTABLISHED`, `EXPERIMENTALLY_SUPPORTED`, `USER_REPORTED`, `INFERENCE`, `HYPOTHESIS`, `CONTRADICTED`, `UNKNOWN`, and `OPEN`. Record exact URLs, capture timestamps, viewports, journeys, methods, failures, tool limits and next discriminating tests.

The HTML auditor is structural triage, **not** a WCAG conformance checker. Screenshots, HTML validation and automated tools cannot establish complete accessibility. Keyboard, screen-reader, contrast and human evaluation remain separate.

The Arquivo.pt CLI tests use controlled responses. Direct DNS/network access from the original build container was unavailable, so no live CLI request is claimed as a locally executed test; the API endpoints were independently exercised during research. Capture timestamps are archive dates, not proof of original publication dates.

## Preservation and rights

Archived content may contain personal information, copyrighted material and untrusted outbound links. Retrieval does not grant republication rights. The tools do not execute archived scripts or automatically visit extracted destinations. Do not bulk mirror or republish third-party material without a rights basis.

## Next

Pilot 003 is **Pixel Atlas**: an accessible, searchable companion interface for image-map-heavy pixel directories. Its scope and acceptance criteria are tracked in [GitHub issue #1](https://github.com/Loofy147/Old-web-rescue/issues/1) and `ROADMAP.md`.

See `RESEARCH_PROTOCOL.md`, `IP_AND_PRESERVATION.md`, `CONTRIBUTING.md`, and `CHANGELOG.md` for the operating rules and repository history.
