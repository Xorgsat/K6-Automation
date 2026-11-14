#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== Executing QuickPizza Operational Load Test ==="
mkdir -p "${REPO_ROOT}/results/raw"

k6 run \
  -e WORKLOAD_PROFILE=load \
  -e SUMMARY_OUTPUT="${REPO_ROOT}/results/raw/load-summary.json" \
  "${REPO_ROOT}/k6/tests/load/run-load.js"

echo "Load test complete. Output saved to results/raw/load-summary.json"
