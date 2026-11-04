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

## Subsequent opportunities

1. **Textfiles Reader:** modern directory/search layer for preserved text archives, with byte-control cleanup shown as a separate derived view while preserving original bytes.
2. **GeoCities Gallery:** explore captured personal pages with capture dates, preservation status, attribution and clear original/archive URL distinction.
3. **Website Rescue Benchmark:** page-scoped task scenarios that compare baseline and modernization prototypes with explicit success criteria.
