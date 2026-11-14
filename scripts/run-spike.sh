#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== Executing QuickPizza Sudden Spike Test ==="
mkdir -p "${REPO_ROOT}/results/raw"

k6 run \
  -e WORKLOAD_PROFILE=spike \
  -e SUMMARY_OUTPUT="${REPO_ROOT}/results/raw/spike-summary.json" \
  "${REPO_ROOT}/k6/tests/spike/run-spike.js"

echo "Spike test complete. Output saved to results/raw/spike-summary.json"
