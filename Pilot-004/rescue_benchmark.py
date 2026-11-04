#!/usr/bin/env python3
"""Validate and summarize task-based website rescue benchmark records.

Standard-library only. The tool never opens URLs or executes supplied content.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

SCHEMA_VERSION = "1.0"
OUTCOMES = {"success", "partial", "blocked", "failed", "not_attempted"}
VARIANT_ROLES = {"baseline", "candidate"}
INPUT_MODES = {"mouse", "keyboard", "touch", "switch", "voice", "mixed"}
FINDING_CATEGORIES = {
    "navigation", "keyboard", "screen_reader", "vision", "motor", "cognitive",
    "compatibility", "performance", "content", "security", "preservation", "other",
}
SEVERITIES = {"critical", "major", "moderate", "minor", "info"}
FINDING_METHODS = {"manual", "automated", "source_inspection", "participant_report", "archive_metadata"}


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_nonnegative_number(value: Any) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(float(value)) and value >= 0
    except (OverflowError, ValueError):
        return False


def _valid_http_url(value: Any) -> bool:
    if not _is_nonempty_string(value):
        return False
    try:
        parsed = urlsplit(value.strip())
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
            return False
        _ = parsed.port  # Force invalid/out-of-range port detection.
        return True
    except ValueError:
        return False


def _valid_viewport(value: Any) -> bool:
    if not _is_nonempty_string(value):
        return False
    match = re.fullmatch(r"([1-9][0-9]*)x([1-9][0-9]*)", value)
    return bool(match)


def validate_benchmark(document: Any) -> list[str]:
    """Return deterministic, human-readable validation errors."""
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["root: expected an object"]

    if document.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version: expected {SCHEMA_VERSION!r}")
    if not _is_nonempty_string(document.get("benchmark_id")):
        errors.append("benchmark_id: expected a non-empty string")

    site = document.get("site")
    if not isinstance(site, dict):
        errors.append("site: expected an object")
    else:
        if not _is_nonempty_string(site.get("label")):
            errors.append("site.label: expected a non-empty string")
        if not _valid_http_url(site.get("canonical_url")):
            errors.append("site.canonical_url: expected an absolute HTTP(S) URL without credentials")
        if site.get("archive_url") is not None and not _valid_http_url(site.get("archive_url")):
            errors.append("site.archive_url: expected an absolute HTTP(S) URL when supplied")
        capture_status = site.get("capture_status")
        if not isinstance(capture_status, str) or capture_status not in {"live", "archive", "local_fixture", "unknown"}:
            errors.append("site.capture_status: expected live, archive, local_fixture or unknown")
        if site.get("captured_at") is not None and not _is_nonempty_string(site.get("captured_at")):
            errors.append("site.captured_at: expected a non-empty string when supplied")
        if capture_status == "archive":
            if not _valid_http_url(site.get("archive_url")):
                errors.append("site.archive_url: required when capture_status is archive")
            if not _is_nonempty_string(site.get("captured_at")):
                errors.append("site.captured_at: required when capture_status is archive")

    variants = document.get("variants")
    variant_ids: set[str] = set()
    baseline_ids: list[str] = []
    if not isinstance(variants, list) or len(variants) < 2:
        errors.append("variants: expected a list containing at least two variants")
        variants = []
    for index, variant in enumerate(variants):
        prefix = f"variants[{index}]"
        if not isinstance(variant, dict):
            errors.append(f"{prefix}: expected an object")
            continue
        variant_id = variant.get("id")
        if not _is_nonempty_string(variant_id):
            errors.append(f"{prefix}.id: expected a non-empty string")
        elif variant_id in variant_ids:
            errors.append(f"{prefix}.id: duplicate variant id {variant_id!r}")
        else:
            variant_ids.add(variant_id)
        if not _is_nonempty_string(variant.get("label")):
            errors.append(f"{prefix}.label: expected a non-empty string")
        role = variant.get("role")
        if not isinstance(role, str) or role not in VARIANT_ROLES:
            errors.append(f"{prefix}.role: expected baseline or candidate")
        elif role == "baseline" and _is_nonempty_string(variant_id):
            baseline_ids.append(variant_id)
    if len(baseline_ids) != 1:
        errors.append("variants: exactly one variant must have role 'baseline'")

    scenarios = document.get("scenarios")
    scenario_ids: set[str] = set()
    scenario_definitions: dict[str, dict[str, Any]] = {}
    if not isinstance(scenarios, list) or not scenarios:
        errors.append("scenarios: expected a non-empty list")
        scenarios = []
    for index, scenario in enumerate(scenarios):
        prefix = f"scenarios[{index}]"
        if not isinstance(scenario, dict):
            errors.append(f"{prefix}: expected an object")
            continue
        scenario_id = scenario.get("id")
        if not _is_nonempty_string(scenario_id):
            errors.append(f"{prefix}.id: expected a non-empty string")
        elif scenario_id in scenario_ids:
            errors.append(f"{prefix}.id: duplicate scenario id {scenario_id!r}")
        else:
            scenario_ids.add(scenario_id)
            scenario_definitions[scenario_id] = scenario
        if not _is_nonempty_string(scenario.get("objective")):
            errors.append(f"{prefix}.objective: expected a non-empty string")
        criteria = scenario.get("success_criteria")
        criterion_ids: set[str] = set()
        if not isinstance(criteria, list) or not criteria:
            errors.append(f"{prefix}.success_criteria: expected a non-empty list")
        else:
            for criterion_index, criterion in enumerate(criteria):
                criterion_prefix = f"{prefix}.success_criteria[{criterion_index}]"
                if not isinstance(criterion, dict):
                    errors.append(f"{criterion_prefix}: expected an object with id and description")
                    continue
                criterion_id = criterion.get("id")
                if not _is_nonempty_string(criterion_id):
                    errors.append(f"{criterion_prefix}.id: expected a non-empty string")
                elif criterion_id in criterion_ids:
                    errors.append(f"{criterion_prefix}.id: duplicate criterion id {criterion_id!r}")
                else:
                    criterion_ids.add(criterion_id)
                if not _is_nonempty_string(criterion.get("description")):
                    errors.append(f"{criterion_prefix}.description: expected a non-empty string")

    runs = document.get("runs")
    run_ids: set[str] = set()
    if not isinstance(runs, list) or not runs:
        errors.append("runs: expected a non-empty list")
        runs = []
    for index, run in enumerate(runs):
        prefix = f"runs[{index}]"
        if not isinstance(run, dict):
            errors.append(f"{prefix}: expected an object")
            continue
        run_id = run.get("id")
        if not _is_nonempty_string(run_id):
            errors.append(f"{prefix}.id: expected a non-empty string")
        elif run_id in run_ids:
            errors.append(f"{prefix}.id: duplicate run id {run_id!r}")
        else:
            run_ids.add(run_id)
        scenario_ref = run.get("scenario_id")
        if not _is_nonempty_string(scenario_ref) or scenario_ref not in scenario_ids:
            errors.append(f"{prefix}.scenario_id: references an unknown scenario")
        variant_ref = run.get("variant_id")
        if not _is_nonempty_string(variant_ref) or variant_ref not in variant_ids:
            errors.append(f"{prefix}.variant_id: references an unknown variant")
        outcome = run.get("outcome")
        if not isinstance(outcome, str) or outcome not in OUTCOMES:
            errors.append(f"{prefix}.outcome: expected one of {', '.join(sorted(OUTCOMES))}")
        environment = run.get("environment")
        if not isinstance(environment, dict):
            errors.append(f"{prefix}.environment: expected an object")
        else:
            for field in ("browser", "assistive_technology"):
                if not _is_nonempty_string(environment.get(field)):
                    errors.append(f"{prefix}.environment.{field}: expected a non-empty string")
            if not _valid_viewport(environment.get("viewport")):
                errors.append(f"{prefix}.environment.viewport: expected WIDTHxHEIGHT using positive integers")
            input_mode = environment.get("input_mode")
            if not isinstance(input_mode, str) or input_mode not in INPUT_MODES:
                errors.append(f"{prefix}.environment.input_mode: expected one of {', '.join(sorted(INPUT_MODES))}")
        if "steps" in run and (not isinstance(run["steps"], int) or isinstance(run["steps"], bool) or run["steps"] < 0):
            errors.append(f"{prefix}.steps: expected a non-negative integer")
        if "duration_seconds" in run and not _is_nonnegative_number(run["duration_seconds"]):
            errors.append(f"{prefix}.duration_seconds: expected a finite non-negative number")
        findings = run.get("findings", [])
        if not isinstance(findings, list):
            errors.append(f"{prefix}.findings: expected a list")
            continue
        for finding_index, finding in enumerate(findings):
            finding_prefix = f"{prefix}.findings[{finding_index}]"
            if not isinstance(finding, dict):
                errors.append(f"{finding_prefix}: expected an object")
                continue
            for field in ("category", "severity", "method"):
                if not _is_nonempty_string(finding.get(field)):
                    errors.append(f"{finding_prefix}.{field}: expected a non-empty string")
            category = finding.get("category")
            if not isinstance(category, str) or category not in FINDING_CATEGORIES:
                errors.append(f"{finding_prefix}.category: unsupported finding category")
            severity = finding.get("severity")
            if not isinstance(severity, str) or severity not in SEVERITIES:
                errors.append(f"{finding_prefix}.severity: unsupported severity")
            method = finding.get("method")
            if not isinstance(method, str) or method not in FINDING_METHODS:
                errors.append(f"{finding_prefix}.method: unsupported evidence method")
            if not _is_nonempty_string(finding.get("summary")):
                errors.append(f"{finding_prefix}.summary: expected a non-empty string")
            if not _is_nonempty_string(finding.get("evidence")):
                errors.append(f"{finding_prefix}.evidence: expected a non-empty string")
            if finding.get("reproduction") is not None and not _is_nonempty_string(finding.get("reproduction")):
                errors.append(f"{finding_prefix}.reproduction: expected a non-empty string when supplied")

        scenario_id_for_results = run.get("scenario_id")
        scenario_definition = scenario_definitions.get(scenario_id_for_results) if _is_nonempty_string(scenario_id_for_results) else None
        criterion_results = run.get("criterion_results")
        result_statuses: list[str] = []
        result_ids: set[str] = set()
        result_structure_valid = True
        if not isinstance(criterion_results, list):
            errors.append(f"{prefix}.criterion_results: expected a list covering every scenario success criterion")
            result_structure_valid = False
        elif scenario_definition is not None:
            expected_criteria = scenario_definition.get("success_criteria", [])
            expected_ids = {
                criterion.get("id") for criterion in expected_criteria
                if isinstance(criterion, dict) and _is_nonempty_string(criterion.get("id"))
            }
            for result_index, criterion_result in enumerate(criterion_results):
                result_prefix = f"{prefix}.criterion_results[{result_index}]"
                if not isinstance(criterion_result, dict):
                    errors.append(f"{result_prefix}: expected an object")
                    result_structure_valid = False
                    continue
                criterion_id = criterion_result.get("criterion_id")
                if not _is_nonempty_string(criterion_id) or criterion_id not in expected_ids:
                    errors.append(f"{result_prefix}.criterion_id: references an unknown criterion")
                    result_structure_valid = False
                elif criterion_id in result_ids:
                    errors.append(f"{result_prefix}.criterion_id: duplicate criterion result {criterion_id!r}")
                    result_structure_valid = False
                else:
                    result_ids.add(criterion_id)
                status = criterion_result.get("status")
                if not isinstance(status, str) or status not in {"met", "not_met", "unknown"}:
                    errors.append(f"{result_prefix}.status: expected met, not_met or unknown")
                    result_structure_valid = False
                else:
                    result_statuses.append(status)
                if not _is_nonempty_string(criterion_result.get("evidence")):
                    errors.append(f"{result_prefix}.evidence: expected evidence or a reason for unknown")
                    result_structure_valid = False
            if result_ids != expected_ids:
                missing = sorted(expected_ids - result_ids)
                if missing:
                    errors.append(f"{prefix}.criterion_results: missing results for {', '.join(missing)}")
                    result_structure_valid = False
            if len(criterion_results) != len(expected_ids):
                result_structure_valid = False
        else:
            result_structure_valid = False

        findings_have_blocker = any(
            isinstance(finding, dict) and isinstance(finding.get("severity"), str) and finding.get("severity") in {"critical", "major"}
            for finding in findings if isinstance(findings, list)
        )
        if result_structure_valid and len(result_statuses) == len(result_ids):
            status_set = set(result_statuses)
            if outcome == "success" and status_set != {"met"}:
                errors.append(f"{prefix}.outcome: success requires every criterion to be met")
            elif outcome == "partial" and not ("met" in status_set and len(status_set) > 1):
                errors.append(f"{prefix}.outcome: partial requires at least one met and one unmet or unknown criterion")
            elif outcome == "failed" and not ("met" not in status_set and "not_met" in status_set):
                errors.append(f"{prefix}.outcome: failed requires no met criteria and at least one not_met criterion")
            elif outcome == "blocked" and not (status_set == {"unknown"} and findings_have_blocker):
                errors.append(f"{prefix}.outcome: blocked requires unknown criteria and a critical/major finding")
            elif outcome == "not_attempted":
                if status_set != {"unknown"}:
                    errors.append(f"{prefix}.outcome: not_attempted requires every criterion to be unknown")
                if "duration_seconds" in run or "steps" in run:
                    errors.append(f"{prefix}.outcome: not_attempted must not include duration_seconds or steps")

    return errors


def _environment_key(environment: dict[str, Any]) -> str:
    return json.dumps(environment, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _variant_summary(variant: dict[str, Any], runs: list[dict[str, Any]]) -> dict[str, Any]:
    outcomes = Counter(run["outcome"] for run in runs)
    attempted = len(runs) - outcomes.get("not_attempted", 0)
    findings = Counter(
        f"{finding['severity']}:{finding['category']}"
        for run in runs for finding in run.get("findings", [])
    )
    return {
        "label": variant["label"],
        "role": variant["role"],
        "run_records": len(runs),
        "attempted_runs": attempted,
        "outcome_counts": {outcome: outcomes.get(outcome, 0) for outcome in sorted(OUTCOMES)},
        "finding_occurrences": sum(findings.values()),
        "finding_counts": dict(sorted(findings.items())),
    }

def analyze_benchmark(document: dict[str, Any]) -> dict[str, Any]:
    """Build deterministic descriptive metrics; does not issue a composite score."""
    errors = validate_benchmark(document)
    if errors:
        raise ValueError("Invalid benchmark:\n- " + "\n- ".join(errors))

    variants = {variant["id"]: variant for variant in document["variants"]}
    scenarios = {scenario["id"]: scenario for scenario in document["scenarios"]}
    runs_by_variant: dict[str, list[dict[str, Any]]] = defaultdict(list)
    cells: dict[tuple[str, str], dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for run in document["runs"]:
        runs_by_variant[run["variant_id"]].append(run)
        cells[(run["scenario_id"], _environment_key(run["environment"]))][run["variant_id"]].append(run)

    baseline_id = next(variant_id for variant_id, variant in variants.items() if variant["role"] == "baseline")
    summaries = {
        variant_id: _variant_summary(variant, runs_by_variant.get(variant_id, []))
        for variant_id, variant in sorted(variants.items())
    }
    comparisons: list[dict[str, Any]] = []
    for (scenario_id, environment_key), by_variant in sorted(cells.items(), key=lambda item: (item[0][0], item[0][1])):
        baseline_runs = by_variant.get(baseline_id, [])
        baseline_attempts = [run for run in baseline_runs if run["outcome"] != "not_attempted"]
        if not baseline_attempts:
            continue
        environment = json.loads(environment_key)
        baseline_successes = [run for run in baseline_attempts if run["outcome"] == "success"]
        baseline_rate = len(baseline_successes) / len(baseline_attempts)
        for candidate_id, candidate in sorted(variants.items()):
            if candidate["role"] != "candidate":
                continue
            candidate_attempts = [run for run in by_variant.get(candidate_id, []) if run["outcome"] != "not_attempted"]
            if not candidate_attempts:
                continue
            candidate_successes = [run for run in candidate_attempts if run["outcome"] == "success"]
            candidate_rate = len(candidate_successes) / len(candidate_attempts)
            base_durations = [run["duration_seconds"] for run in baseline_successes if "duration_seconds" in run]
            candidate_durations = [run["duration_seconds"] for run in candidate_successes if "duration_seconds" in run]
            base_steps = [run["steps"] for run in baseline_successes if "steps" in run]
            candidate_steps = [run["steps"] for run in candidate_successes if "steps" in run]
            baseline_median_duration = statistics.median(base_durations) if base_durations else None
            candidate_median_duration = statistics.median(candidate_durations) if candidate_durations else None
            baseline_median_steps = statistics.median(base_steps) if base_steps else None
            candidate_median_steps = statistics.median(candidate_steps) if candidate_steps else None
            comparisons.append({
                "scenario_id": scenario_id,
                "scenario_objective": scenarios[scenario_id]["objective"],
                "environment": environment,
                "baseline_variant_id": baseline_id,
                "candidate_variant_id": candidate_id,
                "baseline": {
                    "successes": len(baseline_successes), "attempted": len(baseline_attempts),
                    "completion_rate": baseline_rate,
                    "median_success_duration_seconds": baseline_median_duration,
                    "median_success_steps": baseline_median_steps,
                },
                "candidate": {
                    "successes": len(candidate_successes), "attempted": len(candidate_attempts),
                    "completion_rate": candidate_rate,
                    "median_success_duration_seconds": candidate_median_duration,
                    "median_success_steps": candidate_median_steps,
                },
                "completion_rate_delta_percentage_points": round((candidate_rate - baseline_rate) * 100, 2),
                "median_success_duration_delta_seconds": (
                    round(candidate_median_duration - baseline_median_duration, 3)
                    if baseline_median_duration is not None and candidate_median_duration is not None else None
                ),
                "median_success_steps_delta": (
                    round(candidate_median_steps - baseline_median_steps, 3)
                    if baseline_median_steps is not None and candidate_median_steps is not None else None
                ),
            })

    not_attempted_count = sum(run["outcome"] == "not_attempted" for run in document["runs"])
    return {
        "schema_version": SCHEMA_VERSION,
        "benchmark_id": document["benchmark_id"],
        "site": document["site"],
        "baseline_variant_id": baseline_id,
        "scenario_count": len(scenarios),
        "run_record_count": len(document["runs"]),
        "not_attempted_records_excluded_from_rates": not_attempted_count,
        "variants": summaries,
        "matched_condition_comparisons": comparisons,
        "interpretation_limits": [
            "Completion rates are descriptive and depend on the recorded task, sample and environment.",
            "Comparisons are grouped only when scenario id and the full environment record match exactly.",
            "Matched conditions do not imply paired participants or statistical significance.",
            "Duration and step medians include successful runs only; inspect outcome counts beside them.",
            "Finding counts are occurrences, not deduplicated defects or severity-weighted scores.",
            "No composite site score, accessibility certification or whole-domain conclusion is produced.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# Benchmark report: {report['benchmark_id']}",
        "",
        f"- **Site:** {report['site']['label']}",
        f"- **URL:** {report['site']['canonical_url']}",
        f"- **Capture status:** {report['site']['capture_status']}",
        f"- **Scenarios:** {report['scenario_count']}",
        f"- **Run records:** {report['run_record_count']}",
        f"- **Not attempted (excluded from rates):** {report['not_attempted_records_excluded_from_rates']}",
        "",
        "## Variant outcomes (counts across recorded scenarios)",
        "",
        "| Variant | Role | Records | Attempts | Success | Partial | Blocked | Failed | Not attempted | Finding occurrences |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for variant_id, summary in report["variants"].items():
        counts = summary["outcome_counts"]
        lines.append(
            f"| {variant_id} ({summary['label']}) | {summary['role']} | {summary['run_records']} | "
            f"{summary['attempted_runs']} | {counts['success']} | {counts['partial']} | "
            f"{counts['blocked']} | {counts['failed']} | {counts['not_attempted']} | "
            f"{summary['finding_occurrences']} |"
        )
    lines.extend(["", "## Matched-condition comparisons", ""])
    if not report["matched_condition_comparisons"]:
        lines.append("No baseline/candidate pairs shared an identical scenario and environment record.")
    else:
        lines.extend([
            "| Scenario | Environment | Baseline completion | Candidate completion | Delta (pp) | Successful duration baseline → candidate (Δ s) | Successful steps baseline → candidate (Δ) |",
            "|---|---|---:|---:|---:|---:|---:|",
        ])
        for item in report["matched_condition_comparisons"]:
            environment = item["environment"]
            env_text = f"{environment['browser']} · {environment['viewport']} · {environment['input_mode']} · {environment['assistive_technology']}"
            baseline_rate = f"{item['baseline']['completion_rate'] * 100:.1f}% ({item['baseline']['successes']}/{item['baseline']['attempted']})"
            candidate_rate = f"{item['candidate']['completion_rate'] * 100:.1f}% ({item['candidate']['successes']}/{item['candidate']['attempted']})"
            base_duration = item["baseline"]["median_success_duration_seconds"]
            candidate_duration = item["candidate"]["median_success_duration_seconds"]
            duration_delta = item["median_success_duration_delta_seconds"]
            duration_text = "—" if base_duration is None or candidate_duration is None else f"{base_duration} → {candidate_duration} ({duration_delta:+.3f})"
            base_steps = item["baseline"]["median_success_steps"]
            candidate_steps = item["candidate"]["median_success_steps"]
            step_delta = item["median_success_steps_delta"]
            steps_text = "—" if base_steps is None or candidate_steps is None else f"{base_steps} → {candidate_steps} ({step_delta:+.3f})"
            lines.append(
                f"| {item['scenario_id']} | {env_text} | {baseline_rate} | {candidate_rate} | "
                f"{item['completion_rate_delta_percentage_points']:+.2f} | {duration_text} | {steps_text} |"
            )
    lines.extend(["", "## Interpretation limits", ""])
    lines.extend(f"- {limit}" for limit in report["interpretation_limits"])
    lines.append("")
    return "\n".join(lines)


def _load_document(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path} at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("validate", "report"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("benchmark", type=Path, help="path to a benchmark JSON file")
        if command == "report":
            subparser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    args = parser.parse_args(argv)

    try:
        document = _load_document(args.benchmark)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    errors = validate_benchmark(document)
    if errors:
        if args.command == "report" and args.format == "json":
            print(json.dumps({"valid": False, "errors": errors}, ensure_ascii=False, indent=2))
        else:
            print("Invalid benchmark:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
        return 1

    if args.command == "validate":
        print(f"Valid benchmark: {document['benchmark_id']} — {len(document['scenarios'])} scenarios, {len(document['runs'])} run records")
        return 0

    report = analyze_benchmark(document)
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render_markdown(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
