# Old Web Rescue Lab — Research Protocol v0.1

## 1. Purpose

Produce repeatable, evidence-backed investigations of long-lived, neglected, broken or historically preserved websites. A research record must be useful to another investigator without relying on this chat or unstated assumptions.

## 2. Investigation sequence

1. **Discover** — identify a candidate, its historical context, current URL and available archive sources.
2. **Bound** — define the exact pages, viewports, user journeys and test dimensions under review.
3. **Engage** — perform task-based navigation rather than stopping at the homepage.
4. **Observe** — record visible behavior, HTTP/page access outcomes, source markup, links, capture dates and screenshots where available.
5. **Test** — reproduce significant failures and separate site behavior from inspection-tool limitations.
6. **Interpret** — connect findings to usability, accessibility, usefulness, preservation and technical health without overstating the evidence.
7. **Extract** — identify reusable patterns or product opportunities.
8. **Implement** — build a small, legally and technically independent prototype when the finding justifies it.
9. **Verify** — add regression tests, rerun the relevant suite and record negative results.
10. **Publish** — update field notes, source provenance, machine-readable records, run results and the changelog.

## 3. Evidence labels

Use the following labels consistently:

- `ESTABLISHED` — directly visible in an inspected source, page, official document or reproducible artifact.
- `EXPERIMENTALLY_SUPPORTED` — reproduced by a stated test or task in a defined environment.
- `USER_REPORTED` — supplied by a participant or user and not independently verified.
- `INFERENCE` — interpretation logically derived from identified observations.
- `HYPOTHESIS` — a proposition that requires a discriminating test.
- `CONTRADICTED` — evidence directly conflicts with the stated claim.
- `UNKNOWN` — not tested, inaccessible or not established by available evidence.
- `OPEN` — an unresolved question with a defined next test where possible.

Do not convert an estimate, a screenshot, a validator warning or a third-party claim into an established conclusion without checking what it actually proves.

## 4. Minimum website record

For each investigated site or page, capture as applicable:

- Candidate name, canonical URL, domain and historical reference date.
- Current or archived state, archive provider and exact capture timestamp.
- Exact page URLs and page-level scope.
- Viewport dimensions, browser/environment and date of inspection.
- User journey: starting point, intended task, actions, outcome and recovery behavior.
- Technical observations: response/access status, markup features, scripts/plugins, frames, links and media dependencies.
- Accessibility observations: text alternatives, document language, heading structure, keyboard behavior, focus, contrast and assistive-technology results where tested.
- Evidence pointers: source URL, archive URL, screenshot path, response excerpt, fixture or test name.
- Claim label, limitation, counterevidence and confidence-relevant unknowns.
- Reuse opportunity, proposed fix and acceptance test.

An observation may be page-specific; do not assign one blanket accessibility or usability result to an entire domain based on a single page.

## 5. Task-based engagement

Prefer at least three representative tasks when the site supports them. Examples include finding a record, following an internal link, completing a form, reading/downloading a resource, recovering from a failed interaction, or opening a historical capture. Record blocked and failed tasks as carefully as successful ones.

When a tool cannot interact with a page (for example, a frame, plugin, script-heavy canvas or anti-bot gate), label the result as a tool/access limitation until a separate method establishes a site defect.

## 6. Scoring and comparison

Do not create a single composite website score by default. Keep usefulness, task completion, accessibility evidence, technical condition, responsive behavior, information architecture and preservation completeness as separate dimensions. Preserve `UNKNOWN` values explicitly; do not silently substitute zero or an assumed average.

For baseline-versus-prototype comparisons, define the task objective and observable success criteria before testing. Record the browser, viewport, input mode and assistive-technology context for every run. Compare outcomes only under matched task and environment conditions. Keep success, partial, blocked, failed and not-attempted outcomes distinct. Report duration and step medians for successful runs separately from completion rates.

If a decision process later requires a weighted priority score, declare the dimensions, weights, scale anchors, page scope and evidence coverage first. Publish raw observations and counterevidence alongside it. A prioritization score is not a direct empirical result, accessibility certificate or whole-domain conclusion.

## 7. Prototype gate

A modernization prototype is justified when all are true:

1. A concrete defect, lost capability or high-value pattern is evidenced.
2. The target user/task is explicit.
3. The new implementation can be independent of protected code/assets or has a clear permission basis.
4. Acceptance criteria are measurable.
5. Regression tests can capture the important behavior.

Prototype only the smallest useful slice. Do not rebuild an entire brand/site merely because the original looks dated.

## 8. Verification requirements

- Unit tests for pure logic.
- Controlled fixtures for external APIs and archived HTML.
- Browser checks for critical user journeys and responsive layouts.
- Keyboard and focus checks for interactive prototypes.
- Screen-reader/manual accessibility evaluation where accessibility claims are made.
- Security review before running untrusted code or interacting with archived destinations.
- Record failed/killed tests, no-op controls, environment details and exact commands.

A successful HTML validator run is not proof of accessibility; a failed validator check is not proof that the whole service is unusable.

## 9. Required output per investigation

Every completed investigation should publish:
- A concise finding summary.
- A per-page record with evidence labels.
- Source/capture provenance and retrieval date.
- Task paths and outcomes.
- Findings grouped by usefulness, usability, accessibility, technical condition and preservation.
- Uncertainties, counterevidence and limits.
- A ranked reuse/opportunity list.
- A tested prototype or an explicit reason not to implement.
- Run results and a continuation pointer.
