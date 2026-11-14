"""
Executive performance report generator (HTML, JSON, CSV, and Matplotlib charts).
"""

import csv
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

from jinja2 import Environment, FileSystemLoader
from python.reporting.charts import ChartGenerator


class ReportGenerator:
    """Generates multi-format performance engineering reports."""

    def __init__(self, template_dir: str = None):
        if not template_dir:
            template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    def generate_html_report(
        self,
        parsed_data: Dict[str, Any],
        output_html_path: str,
        comparisons: Optional[Dict[str, Any]] = None,
        verdict: str = "PASS",
        findings: Optional[list] = None,
        charts_dir: str = "results/charts"
    ) -> str:
        """Renders comprehensive HTML report."""
        os.makedirs(os.path.dirname(output_html_path), exist_ok=True)
        os.makedirs(charts_dir, exist_ok=True)

        # Generate charts
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        latency_chart_name = f"latency_{timestamp}.png"
        latency_chart_full = os.path.join(charts_dir, latency_chart_name)
        ChartGenerator.generate_latency_bar_chart(parsed_data["latency"], latency_chart_full)

        comp_chart_name = None
        if comparisons:
            comp_chart_name = f"comparison_{timestamp}.png"
            comp_chart_full = os.path.join(charts_dir, comp_chart_name)
            ChartGenerator.generate_comparison_bar_chart(comparisons, comp_chart_full)

        template = self.jinja_env.get_template("report_template.html")

        # Use relative paths for images in HTML
        html_dir = os.path.dirname(os.path.abspath(output_html_path))
        rel_latency_chart = os.path.relpath(latency_chart_full, html_dir)
        rel_comp_chart = os.path.relpath(comp_chart_full, html_dir) if comp_chart_name else None

        rendered = template.render(
            test_name="QuickPizza Performance Engineering Report",
            environment=os.getenv("TEST_ENV", "local"),
            profile=os.getenv("WORKLOAD_PROFILE", "smoke"),
            execution_date=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            verdict=verdict,
            latency=parsed_data["latency"],
            throughput=parsed_data["throughput"],
            errors=parsed_data["errors"],
            vus=parsed_data["vus"],
            comparisons=comparisons,
            findings=findings or ["Test execution completed within acceptable parameters."],
            latency_chart_path=rel_latency_chart,
            comparison_chart_path=rel_comp_chart,
        )

        with open(output_html_path, "w", encoding="utf-8") as f:
            f.write(rendered)

        return output_html_path

    def export_csv_summary(self, parsed_data: Dict[str, Any], output_csv_path: str) -> str:
        """Exports key metrics as a CSV summary."""
        os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)

        rows = [
            ("Category", "Metric", "Value", "Unit"),
            ("Latency", "p50_median", parsed_data["latency"]["med"], "ms"),
            ("Latency", "p90", parsed_data["latency"]["p90"], "ms"),
            ("Latency", "p95", parsed_data["latency"]["p95"], "ms"),
            ("Latency", "p99", parsed_data["latency"]["p99"], "ms"),
            ("Latency", "average", parsed_data["latency"]["avg"], "ms"),
            ("Throughput", "requests_per_second", parsed_data["throughput"]["requests_per_second"], "req/s"),
            ("Throughput", "total_requests", parsed_data["throughput"]["total_requests"], "count"),
            ("Throughput", "iterations_per_second", parsed_data["throughput"]["iterations_per_second"], "iter/s"),
            ("Errors", "failure_percentage", parsed_data["errors"]["failure_percentage"], "%"),
            ("Errors", "failed_requests", parsed_data["errors"]["failed_requests"], "count"),
            ("Checks", "pass_percentage", parsed_data["errors"]["check_pass_percentage"], "%"),
        ]

        with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

        return output_csv_path

    def export_json_summary(self, parsed_data: Dict[str, Any], output_json_path: str) -> str:
        """Exports processed metrics as a clean JSON structure."""
        os.makedirs(os.path.dirname(output_json_path), exist_ok=True)

        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, indent=2)

        return output_json_path
