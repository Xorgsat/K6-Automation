#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== Executing QuickPizza Regression Test ==="
mkdir -p "${REPO_ROOT}/results/raw"

k6 run \
  -e WORKLOAD_PROFILE=regression \
  -e SUMMARY_OUTPUT="${REPO_ROOT}/results/raw/regression-summary.json" \
  "${REPO_ROOT}/k6/tests/regression/run-regression.js"

echo "Regression test complete. Output saved to results/raw/regression-summary.json"
