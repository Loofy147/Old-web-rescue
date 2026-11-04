# Pilot 004 — Run results

**Verification date:** 2026-11-04  
**Local runtime:** Python 3.13.5  
**Fixture:** `fixtures/synthetic-benchmark.json` (synthetic; not a real user study)

## Checks

- `python -m unittest discover -s tests -v` — **34/34 PASS**.
- `python -m py_compile rescue_benchmark.py` — **PASS**.
- `python rescue_benchmark.py validate fixtures/synthetic-benchmark.json` — **PASS**.
- `python rescue_benchmark.py report fixtures/synthetic-benchmark.json --format json` — **PASS**; output also parsed with `python -m json.tool`.
- `python rescue_benchmark.py report fixtures/synthetic-benchmark.json` — **PASS**.
- Exact-environment mismatch control — **PASS**; no comparison emitted when viewport differs.
- Invalid values control — **PASS**; credentialed/invalid-port URLs, invalid viewport, unsupported enum values, `NaN`, negative duration, broken references, malformed criterion results and inconsistent outcomes are rejected.
- Determinism control — **PASS**; identical input yields identical report data.

## Synthetic fixture output

- 2 scenarios, 7 run records, 1 not-attempted record.
- `find-contact`, keyboard / Chromium 130 / 1280×800: baseline 1/2 success; candidate 2/2; +50 percentage points. Median successful duration: 80 s → 71 s (−9 s). Median successful steps: 9 → 7.5 (−1.5).
- `find-hours`, touch / Mobile Safari 17 / 390×844: baseline 0/1; candidate 1/1; +100 percentage points. Duration/step deltas are not emitted because the baseline had no successful run.

These values are fabricated solely to test calculation logic. They are **not** evidence about a real library website, prototype or participant population.

## Environment limitation

Only Python 3.13.5 was available in the local container. Compatibility with the repository's Python 3.10 and 3.12 CI matrix is assigned to GitHub Actions and is not claimed as locally executed here.

## Remaining verification

- Run a real page/task benchmark using documented participants or controlled expert evaluators.
- Confirm whether browser/assistive-technology environment fields need expansion for the planned study design.
- Review privacy, consent and evidence-retention rules before collecting participant observations.
