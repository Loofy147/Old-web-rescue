# Pilot 004 — Benchmark method

## Unit of analysis

The smallest unit is a **run**: one attempt to complete one declared task on one variant in one fully recorded environment. A site/domain is not the unit of analysis. Conclusions remain scoped to the tested page, task and conditions.

## Required controls

1. State an observable objective and success criteria before testing.
2. Identify the baseline and each prototype as separate variants.
3. Record browser, viewport, input mode and assistive-technology context for every run.
4. Record `met`, `not_met` or `unknown` plus evidence for every success criterion on every run; the declared run outcome must agree with those results.
5. Record outcome even when the task is blocked or not attempted. A blocked result requires a critical/major finding; a not-attempted record has no duration or step count.
6. Attach concrete evidence to each finding: what happened, how it was observed and how to reproduce it.
7. Keep original and archived pages distinct. Record exact URLs and capture status.
8. Re-run tasks after a prototype change; do not compare different environments as if they were equivalent.

## Metrics

Variant rollups show run records, attempted runs, outcome counts and finding occurrences only. Completion rates and duration/step medians are calculated inside each exact scenario-and-environment comparison; they are not pooled across dissimilar tasks.

For comparison, group by exact scenario ID and exact environment object. Report completion-rate delta in percentage points and, when both variants have successful observations, median successful duration and step deltas.

`not_attempted` is excluded from completion-rate denominators. `partial`, `blocked` and `failed` remain in the denominator and are not counted as successes. Time and steps from unsuccessful attempts are not blended into successful-run medians.

## No universal score

Do not collapse task usability, accessibility evidence, usefulness, reliability, preservation or content quality into one site score. A benchmark can show that a prototype improves one task while worsening another. Preserve those trade-offs. Ranking candidates requires a separately stated decision policy and must not be represented as a direct empirical result.

## Evidence discipline

Each finding includes category, severity, method, summary and evidence. Distinguish direct observation from automated output, source inspection, participant report and archive metadata. The benchmark utility can validate that these fields exist; it cannot validate their truth or quality.

## Reproducibility and privacy

Use stable scenario IDs, deterministic run IDs, exact environment descriptions and non-identifying participant references only when needed. Never store personal or sensitive participant details. A task result is not proof of a participant's identity, ability, motivation or satisfaction.
