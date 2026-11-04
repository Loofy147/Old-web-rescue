# Old Web Rescue Lab — Pilot 004: Website Rescue Benchmark

**Status:** functional research utility · **Version:** 0.1.0 · **Input:** investigator-authored JSON

Website Rescue Benchmark is a standard-library command-line tool for validating task-based website investigation records and producing transparent baseline-versus-prototype summaries.

It does not crawl websites, run user studies, inspect assistive technology, or decide whether a website is useful. Investigators record observations; the tool checks record integrity and calculates descriptive metrics.

## Why this pilot exists

Old Web Rescue needs a repeatable way to compare the original experience with a narrowly scoped independent prototype. A single site rating would conceal important trade-offs, so the benchmark keeps task completion, time, steps and recorded findings separate.

## Run

Requires Python 3.10+; no third-party packages or network access.

```bash
cd Pilot-004
python rescue_benchmark.py validate fixtures/synthetic-benchmark.json
python rescue_benchmark.py report fixtures/synthetic-benchmark.json
python rescue_benchmark.py report fixtures/synthetic-benchmark.json --format json
python -m unittest discover -s tests -v
```

## Record model

A benchmark contains:

- `site`: canonical page URL, optional archive URL, capture status and optional timestamp.
- `variants`: exactly one `baseline` and one or more `candidate` implementations.
- `scenarios`: task objective and explicit, uniquely identified success criteria.
- `runs`: one observed attempt, its scenario/variant, environment, outcome, a result plus evidence for every success criterion, optional duration/steps, and evidence-backed findings.

Each run must state browser, viewport, input mode and assistive-technology context. A comparison is emitted only when baseline and candidate runs share the same scenario ID and the complete environment object matches exactly.

Outcomes are `success`, `partial`, `blocked`, `failed` and `not_attempted`. Every run must record `met`, `not_met` or `unknown` plus evidence for each scenario criterion; the declared outcome must agree with those criterion results. A blocked run requires a critical/major finding. Not-attempted records have no duration/steps and are excluded from completion-rate denominators. Duration and step medians include successful runs only.

Finding categories include navigation, keyboard, screen reader, vision, motor, cognitive, compatibility, performance, content, security and preservation. Each finding must include a method, severity, summary and concrete evidence.

## Interpretation rules

- Completion rate is `successful attempts / attempted runs` for the stated scenario and environment. It is descriptive, not a population estimate.
- A matched-condition comparison is not necessarily a paired-participant study and does not establish statistical significance.
- Finding counts are occurrences, not deduplicated defects. Repeated observations may refer to the same underlying issue.
- Duration and step differences are conditional on successful runs; they must be read with outcome counts.
- No composite site score, accessibility certification or whole-domain conclusion is produced.
- An `automated` finding is an observation from an automated check, not proof of a human impact. Human and assistive-technology findings must state the method actually used.

## Evidence and safety

The included fixture is wholly synthetic. The tool validates URL syntax but never fetches a URL. Do not include names, contact details, health data, account identifiers or other participant personal data in benchmark records. Use non-identifying run IDs. Do not publish private observations without a rights and privacy basis.

## Limits

The tool cannot determine whether tasks represent real user priorities, whether success criteria are adequate, whether finding severity is correct, or whether a label is meaningful. It cannot replace participant research, expert accessibility review, browser inspection or legal review. It validates consistency of recorded evidence, not truth of the underlying observations.
