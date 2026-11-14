"""
Throughput and bandwidth analysis engine.
Computes request rates (RPS), iteration rates (IPS), and network throughput.
"""

from typing import Dict, Any


class ThroughputAnalysis:
    """Analyzes system throughput and transaction volumes."""

    @staticmethod
    def extract_throughput_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts throughput metrics from k6 summary metrics dictionary.
        """
        if not metrics:
            return {
                "total_requests": 0,
                "requests_per_second": 0.0,
                "total_iterations": 0,
                "iterations_per_second": 0.0,
                "data_received_bytes": 0,
                "data_received_kb": 0.0,
                "data_sent_bytes": 0,
                "data_sent_kb": 0.0,
            }

        http_reqs = metrics.get("http_reqs", {}).get("values", {})
        iterations = metrics.get("iterations", {}).get("values", {})
        data_recv = metrics.get("data_received", {}).get("values", {})
        data_sent = metrics.get("data_sent", {}).get("values", {})

        total_requests = int(http_reqs.get("count", 0))
        rps = float(http_reqs.get("rate", 0.0))

        total_iterations = int(iterations.get("count", 0))
        ips = float(iterations.get("rate", 0.0))

        recv_bytes = int(data_recv.get("count", 0))
        sent_bytes = int(data_sent.get("count", 0))

        return {
            "total_requests": total_requests,
            "requests_per_second": round(rps, 2),
            "total_iterations": total_iterations,
            "iterations_per_second": round(ips, 2),
            "data_received_bytes": recv_bytes,
            "data_received_kb": round(recv_bytes / 1024.0, 2),
            "data_sent_bytes": sent_bytes,
            "data_sent_kb": round(sent_bytes / 1024.0, 2),
        }
