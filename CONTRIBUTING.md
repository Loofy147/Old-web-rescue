# Contributing

## Before adding a website

- Prefer a concrete research question or user journey over collecting a homepage screenshot.
- Record the exact current or archived URL and capture date.
- Check whether the target already exists in `Pilot-001/EVIDENCE.md` or `Pilot-002/FIELD_NOTES.md`.
- Do not infer the launch date of a current page from the site's founding date.

## Before adding a finding

- Label claims using `RESEARCH_PROTOCOL.md`.
- Include the observation, source URL, retrieval date and page scope.
- Record tool limitations and counterevidence.
- Keep source-derived counts tied to the exact response that was inspected.
- Do not claim overall accessibility, security or performance from a partial inspection.

## Before adding code

- Prefer the standard library or an existing project dependency.
- Add a focused regression test for each behavior or defect.
- Keep live-network calls out of unit tests; use controlled fixtures for deterministic tests.
- Do not execute archived website scripts in the HTML auditor.
- Document environment requirements and exact commands.

## Before submitting

Run the applicable checks:

```bash
(cd Pilot-001 && node --test game-engine.test.mjs)
(cd Pilot-001 && python browser-smoke.py)  # requires Playwright + Chromium
(cd Pilot-002 && python -m unittest discover -s tests -v)
(cd Pilot-002 && python -m py_compile geocities_explorer.py legacy_html_audit.py)
(cd Pilot-003 && node --test tests/pixel-atlas-core.test.mjs)
(cd Pilot-004 && python -m unittest discover -s tests -v)
(cd Pilot-004 && python rescue_benchmark.py validate fixtures/synthetic-benchmark.json)
```

Update the relevant `README`, evidence notes, source register, run results and `CHANGELOG.md`. Never claim checks that were not executed.
