# Changelog

## Unreleased — Pilot 004 Website Rescue Benchmark

- Added a standard-library CLI for validating task-based website benchmark records.
- Added criterion-level results with evidence and consistency checks against success, partial, blocked, failed and not-attempted outcomes.
- Added baseline/candidate comparisons only for identical scenario IDs and full environment records.
- Kept completion rates and successful-run duration/step medians scoped to matched task conditions; no pooled site metric or composite score is emitted.
- Added finding categories, severities, evidence methods and reproducible evidence requirements.
- Added a wholly synthetic fixture, 35 regression tests, CLI validation and Markdown/JSON reports.
- Added exact URL, archive-capture, viewport, malformed-value, outcome-consistency, numeric-overflow and determinism checks.
- Local verification passed on Python 3.13.5; Python 3.10/3.12 CI results remain pending.

## Unreleased — Pilot 003 Pixel Atlas

- Added a local-only image-map inspector for pasted and local HTML.
- Added region extraction, map/image association, coordinate validation and raw-attribute provenance.
- Added title-only/missing-label warnings, duplicate destination detection, safe HTTP(S) URL normalization and Wayback replacement handling.
- Added a searchable region inventory, keyboard selection, schematic coordinate view and JSON/CSV exports.
- Added 18 deterministic Node tests and an optional in-memory Playwright browser smoke.
- Verified local import, search, keyboard selection, exports, unsafe URL withholding and source-script non-execution.
- Added the Pilot 003 parser suite to GitHub Actions.
- Kept screen-reader/human accessibility validation explicitly open.

## v0.2.0 — 2026-11-04

- Consolidated the first two research and engineering pilots into the canonical repository structure.
- Added a reusable evidence protocol, contribution rules, preservation/IP notes and a versioned roadmap.
- Added GitHub Actions CI for Node unit tests and Python unit/compile checks.
- Re-ran Pilot 001: 6/6 Node tests and browser smoke PASS (16 cards; keyboard matching, mismatch recovery, restart; 320/390/1440 px; no page errors).
- Re-ran Pilot 002: 23/23 Python tests, Python compilation and legacy HTML fixture JSON audit PASS.
- Preserved source provenance and explicit network/accessibility limitations.

## v0.1.0 — 2026-11-03

- Initial Memory Reboot prototype for the generic matching-game interaction blocked by the legacy Shockwave dependency.
- Initial GeoCities Explorer and Legacy HTML Triage CLIs.
- Added pilot field notes, captured observations, test fixtures and run results.
