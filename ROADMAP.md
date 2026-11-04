# Roadmap

## v0.2.0 — Research and tooling foundation

- [x] Pilot 001: independent, accessible, offline memory-game prototype.
- [x] Pilot 002: GeoCities archive discovery client.
- [x] Pilot 002: legacy HTML structural triage.
- [x] Evidence-first research and preservation protocol.
- [x] Deterministic tests and CI baseline.

## Pilot 003 — Pixel Atlas

**Problem:** The Million Dollar Homepage uses an image map with hundreds of clickable regions. In the inspected live HTML, 251 `<area>` elements had no `alt` attribute. The homepage is visually navigable but its link inventory is not adequately represented as text alternatives.

**Goal:** Build an independent, rights-conscious companion interface for exploring pixel-map destinations as a searchable, keyboard-accessible list and schematic coordinate view.

### Implemented in v0.1 prototype

- [x] Parse pasted or local HTML without executing its scripts or fetching referenced assets.
- [x] Extract map relationships, area shape/coordinates, source attributes and image dimensions.
- [x] Preserve every area, including orphan areas outside a map, with explicit diagnostics.
- [x] Distinguish alt/aria-label source text from title-only review candidates and missing labels.
- [x] Resolve relative HTTP(S) destinations only against an investigator-supplied base URL.
- [x] Detect Wayback replacements and preserve archive URL plus original destination.
- [x] Detect duplicate destinations and malformed geometry.
- [x] Provide searchable inventory and keyboard-operable region selection.
- [x] Provide schematic coordinate visualization without fetching the source image.
- [x] Export complete JSON and filtered CSV records.
- [x] Add parser regression tests and a browser smoke covering keyboard selection, local file import, filtering, export and responsive layouts.
- [x] Add Pilot 003 parser tests to GitHub Actions.

### Open verification gates

- [ ] Manual screen-reader review with at least one desktop and one mobile assistive-technology combination.
- [ ] Human review of source labels before treating any descriptions as meaningful alternatives.
- [ ] Test against a broader corpus of real-world HTML5 and HTML 4 image maps.
- [ ] Evaluate a standards-compliant parsing implementation if malformed nested structures materially reduce extraction accuracy.

### Acceptance and limits

Every extracted area must appear in the inventory; unassociated or malformed regions are surfaced with warnings. The tool does not manufacture descriptive labels. Title values are candidates for human review, not proof of accessible names. The geometry panel is schematic, not a screenshot. The parser is a limited tokenizer, not a full HTML5 parser. No WCAG conformance claim is made.

### Not in scope

- Cloning the live Million Dollar Homepage.
- Rehosting third-party ads, domains, logos or copyrighted images.
- Automatic crawling or link checking of extracted destinations.
- Claims of WCAG conformance without full human evaluation.

## Pilot 004 — Website Rescue Benchmark

**Problem:** Individual pilots can identify defects, but comparisons between original pages and independent prototypes need consistent task definitions, controlled environments and inspectable evidence.

**Goal:** Provide a repeatable, task-level benchmark format and deterministic analyzer without pretending that a website can be reduced to one quality score.

### Implemented

- [x] Standard-library CLI for validating benchmark JSON and producing Markdown/JSON reports.
- [x] Exactly one baseline and one or more candidate variants.
- [x] Explicit scenarios and uniquely identified success criteria.
- [x] Criterion-level `met` / `not_met` / `unknown` outcomes with evidence for every run.
- [x] Consistency checks between criterion results and declared task outcome.
- [x] Browser, viewport, input mode and assistive-technology context required for every run.
- [x] Separate success, partial, blocked, failed and not-attempted outcomes.
- [x] Exclude not-attempted records from completion-rate denominators; disallow durations/steps for them.
- [x] Compare only identical scenario IDs and complete environment records.
- [x] Keep completion rates and successful-run duration/step medians scoped to matched task conditions.
- [x] Preserve evidence category, severity, method, summary and reproduction details.
- [x] Synthetic fixture, deterministic tests, CLI validation and Markdown/JSON output.

### Open verification gates

- [ ] Run a real page/task benchmark with documented expert evaluators or participants.
- [ ] Confirm environment fields against the actual browser and assistive-technology matrix used in the study.
- [ ] Review participant consent, privacy and evidence-retention practices before collecting participant data.
- [ ] Execute the Python 3.10 and 3.12 CI matrix for this pilot.

### Limits

The utility validates record structure and calculation rules, not the truth or quality of observations. Matched environments do not imply paired participants or statistical significance. Finding counts are occurrences, not deduplicated defects. No composite website score, WCAG certification or whole-domain conclusion is produced.

## Subsequent opportunities

1. **Textfiles Reader:** modern directory/search layer for preserved text archives, with byte-control cleanup shown as a separate derived view while preserving original bytes.
2. **GeoCities Gallery:** explore captured personal pages with capture dates, preservation status, attribution and clear original/archive URL distinction.
