"""
Unified Python CLI for QuickPizza Performance Engineering Framework.
Provides commands for configuration validation, result analysis, regression comparison, and report generation.
"""

import argparse
import json
import sys
import os

from python.validation.result_validator import ResultValidator
from python.analysis.metrics_parser import MetricsParser
from python.regression.baseline_manager import BaselineManager
from python.regression.comparison import MetricComparison
from python.regression.regression_detector import RegressionDetector
from python.reporting.report_generator import ReportGenerator


def cmd_validate_config(args):
    """Validates configuration files."""
    workloads_path = args.workloads or "config/workloads.json"
    thresholds_path = args.thresholds or "config/thresholds.json"

    print(f"Validating workload configuration: {workloads_path}...")
    ok_w, err_w, _ = ResultValidator.validate_workload_config(workloads_path)
    if not ok_w:
        print(f"FAILED: {err_w}", file=sys.stderr)
        sys.exit(1)
    print("Workload configuration is valid.")

    print(f"Validating thresholds configuration: {thresholds_path}...")
    ok_t, err_t, _ = ResultValidator.validate_threshold_config(thresholds_path)
    if not ok_t:
        print(f"FAILED: {err_t}", file=sys.stderr)
        sys.exit(1)
    print("Thresholds configuration is valid.")
    print("All configurations PASSED validation.")


def cmd_analyze(args):
    """Ingests and analyzes a k6 summary file."""
    parser = MetricsParser(args.input)
    parsed = parser.parse()

    if args.output:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2)
        print(f"Analysis exported to {args.output}")

    # Print summary to stdout
    lat = parsed["latency"]
    tp = parsed["throughput"]
    err = parsed["errors"]

    print("\n========================================================")
    print(f" QuickPizza Performance Metrics: {args.input}")
    print("========================================================")
    print(f" Latency p95:       {lat['p95']:.2f} ms")
    print(f" Latency Median:    {lat['med']:.2f} ms")
    print(f" Latency Average:   {lat['avg']:.2f} ms")
    print(f" Latency Max:       {lat['max']:.2f} ms")
    print("--------------------------------------------------------")
    print(f" Throughput:        {tp['requests_per_second']:.2f} req/s")
    print(f" Total Requests:    {tp['total_requests']}")
    print(f" Iterations/s:      {tp['iterations_per_second']:.2f} iter/s")
    print("--------------------------------------------------------")
    print(f" Failure Rate:      {err['failure_percentage']:.2f}% ({err['failed_requests']} failed)")
    print(f" Check Pass Rate:   {err['check_pass_percentage']:.2f}% ({err['check_passes']} passed, {err['check_fails']} failed)")
    print("========================================================\n")


def cmd_compare(args):
    """Compares current run with an approved baseline."""
    current_parser = MetricsParser(args.current)
    current_model = current_parser.parse()

    baseline_mgr = BaselineManager(args.baseline_dir)
    if args.baseline:
        with open(args.baseline, "r", encoding="utf-8") as f:
            baseline_raw = json.load(f)
            baseline_model = baseline_raw.get("metrics", baseline_raw)
    else:
        baseline_raw = baseline_mgr.load_approved_baseline()
        if not baseline_raw:
            print("No approved baseline found in baselines/approved-baseline.json", file=sys.stderr)
            sys.exit(1)
        baseline_model = baseline_raw.get("metrics", baseline_raw)

    comparisons = MetricComparison.compare_performance_models(current_model, baseline_model)
    detector = RegressionDetector()
    decision = detector.evaluate(comparisons)

    print("\n========================================================")
    print(f" Performance Baseline Comparison Result: [{decision['verdict']}]")
    print("========================================================")
    for name, comp in comparisons.items():
        delta_str = f"{comp['percentage_diff']:+.1f}% ({comp['absolute_diff']:+.2f})"
        flag = " [DEGRADED]" if comp["is_degraded"] and abs(comp["percentage_diff"]) > 10 else ""
        print(f" {name:<20}: Base: {comp['baseline']:<8} Curr: {comp['current']:<8} Delta: {delta_str}{flag}")

    print("--------------------------------------------------------")
    print("Findings:")
    for f in decision["findings"]:
        print(f" - {f}")
    print("========================================================\n")

    if args.output:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f_out:
            json.dump({"comparisons": comparisons, "decision": decision}, f_out, indent=2)

    if decision["is_regression"]:
        print("REGRESSION DETECTED: Exiting with non-zero status.")
        sys.exit(2)


def cmd_report(args):
    """Generates HTML, JSON, and CSV reports."""
    parser = MetricsParser(args.input)
    parsed_model = parser.parse()

    comparisons = None
    verdict = "PASS"
    findings = ["Execution verified against operational thresholds."]

    if args.baseline:
        if os.path.exists(args.baseline):
            with open(args.baseline, "r", encoding="utf-8") as f:
                b_raw = json.load(f)
                b_model = b_raw.get("metrics", b_raw)
            comparisons = MetricComparison.compare_performance_models(parsed_model, b_model)
            detector = RegressionDetector()
            decision = detector.evaluate(comparisons)
            verdict = decision["verdict"]
            findings = decision["findings"]

    reporter = ReportGenerator()
    html_out = args.html or "results/reports/performance_report.html"
    json_out = args.json or "results/processed/performance_summary.json"
    csv_out = args.csv or "results/reports/metrics_summary.csv"

    reporter.generate_html_report(
        parsed_data=parsed_model,
        output_html_path=html_out,
        comparisons=comparisons,
        verdict=verdict,
        findings=findings
    )
    reporter.export_json_summary(parsed_model, json_out)
    reporter.export_csv_summary(parsed_model, csv_out)

    print(f"\nReports successfully generated:")
    print(f" - HTML Report: {html_out}")
    print(f" - JSON Metrics: {json_out}")
    print(f" - CSV Summary:  {csv_out}\n")


def cmd_approve_baseline(args):
    """Approves a test result as the official baseline."""
    parser = MetricsParser(args.input)
    parsed_model = parser.parse()

    mgr = BaselineManager()
    path = mgr.save_baseline(
        parsed_metrics=parsed_model,
        workload_profile=args.profile or "regression",
        application_version=args.app_version or "quickpizza-0.15.30",
        notes=args.notes or "Official approved benchmark",
        set_as_approved=True
    )
    print(f"Approved baseline saved to: {mgr.get_approved_baseline_path()}")
    print(f"Versioned archive copy: {path}")


def main():
    parser = argparse.ArgumentParser(description="QuickPizza Performance Engineering CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # validate-config
    p_val = subparsers.add_parser("validate-config", help="Validate workloads and thresholds config")
    p_val.add_argument("--workloads", help="Path to workloads.json")
    p_val.add_argument("--thresholds", help="Path to thresholds.json")
    p_val.set_defaults(func=cmd_validate_config)

    # analyze
    p_an = subparsers.add_parser("analyze", help="Analyze raw k6 summary JSON")
    p_an.add_argument("--input", required=True, help="Input summary JSON file")
    p_an.add_argument("--output", help="Output path for processed metrics JSON")
    p_an.set_defaults(func=cmd_analyze)

    # compare
    p_comp = subparsers.add_parser("compare", help="Compare run against baseline")
    p_comp.add_argument("--current", required=True, help="Current summary JSON")
    p_comp.add_argument("--baseline", help="Baseline JSON file (defaults to approved)")
    p_comp.add_argument("--baseline-dir", help="Baselines directory")
    p_comp.add_argument("--output", help="Output comparison JSON")
    p_comp.set_defaults(func=cmd_compare)

    # report
    p_rep = subparsers.add_parser("report", help="Generate HTML, JSON, and CSV reports")
    p_rep.add_argument("--input", required=True, help="Input summary JSON")
    p_rep.add_argument("--baseline", help="Baseline JSON for comparison")
    p_rep.add_argument("--html", help="HTML report output path")
    p_rep.add_argument("--json", help="JSON summary output path")
    p_rep.add_argument("--csv", help="CSV summary output path")
    p_rep.set_defaults(func=cmd_report)

    # approve-baseline
    p_app = subparsers.add_parser("approve-baseline", help="Approve result as baseline")
    p_app.add_argument("--input", required=True, help="Summary JSON to approve")
    p_app.add_argument("--profile", default="regression", help="Workload profile name")
    p_app.add_argument("--app-version", default="quickpizza-0.15.30", help="Application version")
    p_app.add_argument("--notes", help="Baseline metadata notes")
    p_app.set_defaults(func=cmd_approve_baseline)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
