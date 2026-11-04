# Roadmap

## v0.2.0 — Research and tooling foundation

- [x] Pilot 001: independent, accessible, offline memory-game prototype.
- [x] Pilot 002: GeoCities archive discovery client.
- [x] Pilot 002: legacy HTML structural triage.
- [x] Evidence-first research and preservation protocol.
- [x] Deterministic tests and CI baseline.

## Pilot 003 — Pixel Atlas

**Problem:** The Million Dollar Homepage uses an image map with hundreds of clickable regions. In the inspected live HTML, 251 `<area>` elements had no `alt` attribute. The homepage is visually navigable but its link inventory is not adequately represented as text alternatives.

**Goal:** Build an independent, rights-conscious companion interface for exploring pixel-map destinations as a searchable, keyboard-accessible list and visual grid.

### Scope

- Parse a user-supplied/local image-map HTML export; do not crawl the live website automatically.
- Extract each region's destination, title, original URL (when supplied), shape and coordinates.
- Provide searchable text index and keyboard-operable selection.
- Expose region links as semantic anchors with meaningful labels derived from available title/metadata; clearly flag entries without sufficient label data.
- Show when a destination is a current URL versus an archive replacement.
- Preserve evidence provenance and original target strings.
- Include a static fixture modelled on a generic image map, not a mirrored commercial site.

### Acceptance criteria

- Every parsed region appears in the text inventory.
- Every interactive item is reachable by keyboard.
- No interactive item is unnamed; missing label metadata is surfaced as an explicit data-quality error, not hidden behind a fabricated label.
- Search and selection work without a pointer.
- 320, 390 and desktop layouts have no horizontal overflow.
- Unit tests cover malformed areas, URL normalization, duplicate destinations, missing labels and empty maps.
- No copyrighted site artwork or advertising assets are bundled.

### Not in scope

- Cloning the live Million Dollar Homepage.
- Rehosting third-party ads, domains, logos or copyrighted images.
- Automatic crawling or link checking of extracted destinations.
- Claims of WCAG conformance without full human evaluation.

## Subsequent opportunities

1. **Textfiles Reader:** modern directory/search layer for preserved text archives, with byte-control cleanup shown as a separate derived view while preserving original bytes.
2. **GeoCities Gallery:** explore captured personal pages with capture dates, preservation status, attribution and clear original/archive URL distinction.
3. **Website Rescue Benchmark:** page-scoped task scenarios that compare baseline and modernization prototypes with explicit success criteria.
