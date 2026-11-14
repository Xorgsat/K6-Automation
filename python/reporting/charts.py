"""
Automated visualization generator for performance test reports using Matplotlib.
"""

import os
from typing import Dict, Any, Optional

# Set non-interactive backend for headless execution in CI and servers
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


class ChartGenerator:
    """Generates charts for performance metrics and baseline comparisons."""

    @staticmethod
    def generate_latency_bar_chart(latency_metrics: Dict[str, float], output_path: str):
        """Generates a bar chart of response time percentiles."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        labels = ["Min", "Median (p50)", "p90", "p95", "p99", "Max", "Average"]
        keys = ["min", "med", "p90", "p95", "p99", "max", "avg"]
        values = [latency_metrics.get(k, 0.0) for k in keys]

        plt.figure(figsize=(9, 4.5))
        bars = plt.bar(labels, values, color=["#4e79a7", "#59a14f", "#f28e2b", "#e15759", "#b07aa1", "#9c755f", "#76b7b2"])

        plt.title("QuickPizza Response Time Latency Distribution", fontsize=14, pad=15)
        plt.xlabel("Percentile / Statistic", fontsize=11, labelpad=10)
        plt.ylabel("Duration (ms)", fontsize=11, labelpad=10)
        plt.grid(axis="y", linestyle="--", alpha=0.5)

        # Annotate bars with values
        for bar in bars:
            height = bar.get_height()
            plt.annotate(
                f"{height:.1f}ms",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold"
            )

        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()

    @staticmethod
    def generate_comparison_bar_chart(comparisons: Dict[str, Any], output_path: str):
        """Generates a grouped bar chart comparing Current Run vs Baseline."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        metrics = ["p95 Latency (ms)", "p90 Latency (ms)", "Median Latency (ms)", "Throughput (RPS)"]
        comp_keys = ["latency_p95", "latency_p90", "latency_median", "throughput_rps"]

        current_vals = [comparisons.get(k, {}).get("current", 0.0) for k in comp_keys]
        baseline_vals = [comparisons.get(k, {}).get("baseline", 0.0) for k in comp_keys]

        import numpy as np
        x = np.arange(len(metrics))
        width = 0.35

        plt.figure(figsize=(10, 5))
        plt.bar(x - width/2, baseline_vals, width, label="Baseline", color="#4e79a7", alpha=0.85)
        plt.bar(x + width/2, current_vals, width, label="Current", color="#e15759", alpha=0.85)

        plt.title("Baseline vs Current Performance Comparison", fontsize=14, pad=15)
        plt.xticks(x, metrics, fontsize=10)
        plt.ylabel("Measured Value", fontsize=11)
        plt.legend(loc="upper right", frameon=True)
        plt.grid(axis="y", linestyle="--", alpha=0.5)

        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()
