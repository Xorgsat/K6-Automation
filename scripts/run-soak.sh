#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== Executing QuickPizza Sustained Soak Test ==="
mkdir -p "${REPO_ROOT}/results/raw"

k6 run \
  -e WORKLOAD_PROFILE=soak \
  -e SUMMARY_OUTPUT="${REPO_ROOT}/results/raw/soak-summary.json" \
  "${REPO_ROOT}/k6/tests/soak/run-soak.js"

echo "Soak test complete. Output saved to results/raw/soak-summary.json"
