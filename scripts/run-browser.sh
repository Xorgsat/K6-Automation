#!/usr/bin/env bash
# ==============================================================================
# Script: run-browser.sh
# Purpose: Execute k6 browser automation in headed or headless mode
# ==============================================================================
set -euo pipefail

HEADED=${1:-"true"}
BASE_URL=${BASE_URL:-"http://localhost:3333"}

echo "=========================================================="
echo " Starting QuickPizza Browser Performance Test"
echo " Target URL: $BASE_URL"
echo " Headed Mode: $HEADED"
echo "=========================================================="

mkdir -p results/charts results/raw

if [ "$HEADED" = "true" ] || [ "$HEADED" = "headed" ]; then
    echo ">> Launching browser in HEADED mode (visible window)..."
    K6_BROWSER_HEADLESS=false k6 run \
        -e BASE_URL="$BASE_URL" \
        k6/browser/run-browser-e2e.js
else
    echo ">> Launching browser in HEADLESS mode..."
    K6_BROWSER_HEADLESS=true k6 run \
        -e BASE_URL="$BASE_URL" \
        k6/browser/run-browser-e2e.js
fi

echo "=========================================================="
echo " Browser test completed successfully!"
echo " Screenshots saved to results/charts/"
echo "=========================================================="
