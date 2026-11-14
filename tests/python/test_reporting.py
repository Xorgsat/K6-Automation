"""
Unit tests for python.reporting.report_generator.
"""

import os
import shutil
import tempfile
import pytest
from python.analysis.metrics_parser import MetricsParser
from python.reporting.report_generator import ReportGenerator


def test_report_generation_from_fixture():
    temp_dir = tempfile.mkdtemp()
    try:
        parser = MetricsParser("datasets/fixtures/synthetic_summary.json")
        model = parser.parse()

        html_path = os.path.join(temp_dir, "test_report.html")
        csv_path = os.path.join(temp_dir, "test_summary.csv")
        json_path = os.path.join(temp_dir, "test_metrics.json")
        charts_dir = os.path.join(temp_dir, "charts")

        reporter = ReportGenerator()
        reporter.generate_html_report(model, html_path, charts_dir=charts_dir)
        reporter.export_csv_summary(model, csv_path)
        reporter.export_json_summary(model, json_path)

        assert os.path.exists(html_path)
        assert os.path.getsize(html_path) > 500

        assert os.path.exists(csv_path)
        assert os.path.getsize(csv_path) > 100

        assert os.path.exists(json_path)
        assert os.path.getsize(json_path) > 100

        # Check chart generation
        charts = os.listdir(charts_dir)
        assert len(charts) >= 1
    finally:
        shutil.rmtree(temp_dir)
