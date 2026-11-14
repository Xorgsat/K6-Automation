#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=========================================================="
echo " Stopping QuickPizza Performance Framework Environment"
echo "=========================================================="

if [ "$1" == "--all" ] || [ "$1" == "-v" ]; then
    echo "Tearing down containers, networks, and persistent database volumes..."
    docker compose -f "${REPO_ROOT}/docker/compose.yml" --profile full down -v --remove-orphans
else
    echo "Stopping containers (preserving volumes)..."
    docker compose -f "${REPO_ROOT}/docker/compose.yml" --profile full down --remove-orphans
fi

echo "Environment stopped cleanly."
