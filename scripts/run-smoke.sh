#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== Executing QuickPizza Smoke Test ==="
mkdir -p "${REPO_ROOT}/results/raw"

k6 run \
  -e WORKLOAD_PROFILE=smoke \
  -e SUMMARY_OUTPUT="${REPO_ROOT}/results/raw/smoke-summary.json" \
  "${REPO_ROOT}/k6/tests/smoke/run-smoke.js"

echo "Smoke test complete. Output saved to results/raw/smoke-summary.json"
