#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== Executing QuickPizza Progressive Stress Test ==="
mkdir -p "${REPO_ROOT}/results/raw"

k6 run \
  -e WORKLOAD_PROFILE=stress \
  -e SUMMARY_OUTPUT="${REPO_ROOT}/results/raw/stress-summary.json" \
  "${REPO_ROOT}/k6/tests/stress/run-stress.js"

echo "Stress test complete. Output saved to results/raw/stress-summary.json"
