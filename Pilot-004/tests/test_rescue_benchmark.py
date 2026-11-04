import copy
import json
import tempfile
import unittest
from pathlib import Path

from rescue_benchmark import analyze_benchmark, main, validate_benchmark

FIXTURE = Path(__file__).parents[1] / "fixtures" / "synthetic-benchmark.json"


class BenchmarkValidationTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_synthetic_fixture_is_valid(self):
        self.assertEqual(validate_benchmark(self.document), [])

    def test_non_object_root_is_rejected(self):
        self.assertEqual(validate_benchmark([]), ["root: expected an object"])

    def test_requires_exactly_one_baseline(self):
        self.document["variants"][1]["role"] = "baseline"
        self.assertTrue(any("exactly one variant" in error for error in validate_benchmark(self.document)))

    def test_duplicate_run_ids_are_rejected(self):
        self.document["runs"][1]["id"] = self.document["runs"][0]["id"]
        self.assertTrue(any("duplicate run id" in error for error in validate_benchmark(self.document)))

    def test_unknown_scenario_reference_is_rejected(self):
        self.document["runs"][0]["scenario_id"] = "missing"
        self.assertTrue(any("unknown scenario" in error for error in validate_benchmark(self.document)))

    def test_unknown_variant_reference_is_rejected(self):
        self.document["runs"][0]["variant_id"] = "missing"
        self.assertTrue(any("unknown variant" in error for error in validate_benchmark(self.document)))

    def test_credentialed_url_is_rejected(self):
        self.document["site"]["canonical_url"] = "https://user:pass@example.test/"
        self.assertTrue(any("canonical_url" in error for error in validate_benchmark(self.document)))

    def test_invalid_url_port_is_rejected(self):
        self.document["site"]["canonical_url"] = "https://example.test:70000/"
        self.assertTrue(any("canonical_url" in error for error in validate_benchmark(self.document)))

    def test_archive_requires_archive_url_and_capture_timestamp(self):
        self.document["site"]["capture_status"] = "archive"
        self.document["site"].pop("archive_url", None)
        self.document["site"].pop("captured_at", None)
        errors = validate_benchmark(self.document)
        self.assertTrue(any("archive_url: required" in error for error in errors))
        self.assertTrue(any("captured_at: required" in error for error in errors))

    def test_viewport_requires_positive_width_and_height(self):
        self.document["runs"][0]["environment"]["viewport"] = "0x844"
        self.assertTrue(any("viewport" in error for error in validate_benchmark(self.document)))

    def test_run_must_cover_every_success_criterion(self):
        self.document["runs"][0]["criterion_results"].pop()
        self.assertTrue(any("missing results for" in error for error in validate_benchmark(self.document)))

    def test_duplicate_criterion_result_is_rejected(self):
        result = self.document["runs"][0]["criterion_results"][0]
        self.document["runs"][0]["criterion_results"][1]["criterion_id"] = result["criterion_id"]
        self.assertTrue(any("duplicate criterion result" in error for error in validate_benchmark(self.document)))

    def test_outcome_must_match_criterion_results(self):
        self.document["runs"][1]["criterion_results"][0]["status"] = "not_met"
        self.assertTrue(any("success requires every criterion" in error for error in validate_benchmark(self.document)))

    def test_failed_run_is_valid_when_no_criterion_is_met(self):
        run = self.document["runs"][0]
        run["outcome"] = "failed"
        run["criterion_results"] = [
            {"criterion_id": "contact_page", "status": "not_met", "evidence": "The expected page was not reached."},
            {"criterion_id": "contact_method", "status": "not_met", "evidence": "No valid contact method was identified."}
        ]
        run["findings"] = []
        self.assertEqual(validate_benchmark(self.document), [])

    def test_partial_run_cannot_claim_every_criterion_met(self):
        run = self.document["runs"][5]
        run["criterion_results"][1]["status"] = "met"
        self.assertTrue(any("partial requires" in error for error in validate_benchmark(self.document)))

    def test_blocked_run_requires_a_critical_or_major_finding(self):
        self.document["runs"][0]["findings"] = []
        self.assertTrue(any("blocked requires unknown criteria" in error for error in validate_benchmark(self.document)))

    def test_not_attempted_run_cannot_claim_steps_or_duration(self):
        run = next(item for item in self.document["runs"] if item["outcome"] == "not_attempted")
        run["steps"] = 0
        self.assertTrue(any("not_attempted must not include" in error for error in validate_benchmark(self.document)))

    def test_invalid_input_mode_is_rejected(self):
        self.document["runs"][0]["environment"]["input_mode"] = "telepathy"
        self.assertTrue(any("input_mode" in error for error in validate_benchmark(self.document)))

    def test_negative_duration_is_rejected(self):
        self.document["runs"][0]["duration_seconds"] = -0.1
        self.assertTrue(any("duration_seconds" in error for error in validate_benchmark(self.document)))

    def test_nan_duration_is_rejected(self):
        self.document["runs"][0]["duration_seconds"] = float("nan")
        self.assertTrue(any("duration_seconds" in error for error in validate_benchmark(self.document)))

    def test_overflowing_duration_is_rejected_without_crashing(self):
        self.document["runs"][0]["duration_seconds"] = 10 ** 400
        self.assertTrue(any("duration_seconds" in error for error in validate_benchmark(self.document)))

    def test_finding_requires_evidence(self):
        self.document["runs"][0]["findings"][0]["evidence"] = "  "
        self.assertTrue(any("evidence" in error for error in validate_benchmark(self.document)))

    def test_unknown_finding_category_is_rejected(self):
        self.document["runs"][0]["findings"][0]["category"] = "vibes"
        self.assertTrue(any("unsupported finding category" in error for error in validate_benchmark(self.document)))

    def test_unhashable_enumeration_values_are_reported_not_crashed(self):
        self.document["site"]["capture_status"] = []
        self.document["variants"][0]["role"] = {}
        self.document["runs"][0]["scenario_id"] = []
        self.document["runs"][0]["variant_id"] = {}
        self.document["runs"][0]["outcome"] = []
        self.document["runs"][0]["environment"]["input_mode"] = []
        self.document["runs"][0]["findings"][0]["category"] = []
        errors = validate_benchmark(self.document)
        self.assertGreaterEqual(len(errors), 7)


class BenchmarkAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_not_attempted_is_excluded_from_completion_denominator(self):
        report = analyze_benchmark(self.document)
        baseline = report["variants"]["original"]
        self.assertEqual(baseline["run_records"], 4)
        self.assertEqual(baseline["attempted_runs"], 3)
        self.assertEqual(baseline["outcome_counts"]["success"], 1)
        self.assertNotIn("completion_rate", baseline)

    def test_matched_condition_delta_is_computed(self):
        report = analyze_benchmark(self.document)
        match = next(item for item in report["matched_condition_comparisons"] if item["scenario_id"] == "find-contact")
        self.assertEqual(match["baseline"]["completion_rate"], 0.5)
        self.assertEqual(match["candidate"]["completion_rate"], 1.0)
        self.assertEqual(match["completion_rate_delta_percentage_points"], 50.0)
        self.assertEqual(match["median_success_duration_delta_seconds"], -9.0)
        self.assertEqual(match["median_success_steps_delta"], -1.5)

    def test_different_environment_does_not_compare(self):
        self.document["runs"] = [
            run for run in self.document["runs"]
            if run["scenario_id"] == "find-contact" and run["variant_id"] in {"original", "modernized"}
        ]
        for run in self.document["runs"]:
            if run["variant_id"] == "original":
                run["environment"]["viewport"] = "1280x800"
            else:
                run["environment"]["viewport"] = "390x844"
        report = analyze_benchmark(self.document)
        self.assertEqual(report["matched_condition_comparisons"], [])

    def test_duration_medians_use_successful_runs_only(self):
        report = analyze_benchmark(self.document)
        match = next(item for item in report["matched_condition_comparisons"] if item["scenario_id"] == "find-contact")
        self.assertEqual(match["baseline"]["median_success_duration_seconds"], 80.0)
        self.assertEqual(match["candidate"]["median_success_duration_seconds"], 71.0)

    def test_variant_rollups_do_not_mix_unlike_scenarios_into_rates(self):
        report = analyze_benchmark(self.document)
        self.assertNotIn("completion_rate", report["variants"]["original"])
        self.assertNotIn("median_success_duration_seconds", report["variants"]["original"])

    def test_no_composite_score_is_emitted(self):
        report = analyze_benchmark(self.document)
        self.assertNotIn("score", report)
        self.assertIn("No composite site score", " ".join(report["interpretation_limits"]))

    def test_report_is_deterministic(self):
        first = analyze_benchmark(self.document)
        second = analyze_benchmark(copy.deepcopy(self.document))
        self.assertEqual(first, second)

    def test_analysis_refuses_invalid_data(self):
        self.document["runs"][0]["outcome"] = "maybe"
        with self.assertRaises(ValueError):
            analyze_benchmark(self.document)


class CliTests(unittest.TestCase):
    def test_validate_command(self):
        self.assertEqual(main(["validate", str(FIXTURE)]), 0)

    def test_markdown_report_command(self):
        self.assertEqual(main(["report", str(FIXTURE), "--format", "markdown"]), 0)

    def test_invalid_json_exit_code(self):
        with tempfile.TemporaryDirectory() as directory:
            bad_file = Path(directory) / "bad.json"
            bad_file.write_text("{broken", encoding="utf-8")
            self.assertEqual(main(["validate", str(bad_file)]), 2)


if __name__ == "__main__":
    unittest.main()
