#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=========================================================="
echo " Bootstrapping QuickPizza Performance Framework"
echo "=========================================================="

cd "${REPO_ROOT}"

# 1. Setup Python Virtual Environment
if [ ! -d ".venv" ]; then
    echo "[1/4] Creating Python virtual environment in .venv..."
    python3 -m venv .venv
fi

echo "[2/4] Installing Python requirements..."
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

# 2. Start Core Docker Services
echo "[3/4] Starting Docker services (QuickPizza, PostgreSQL, Prometheus, Grafana)..."
docker compose -f docker/compose.yml up -d quickpizza-db quickpizza prometheus grafana

# 3. Wait for Readiness
echo "[4/4] Waiting for QuickPizza to pass readiness check..."
MAX_ATTEMPTS=30
ATTEMPT=0
READY=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -s -f http://localhost:3333/ready >/dev/null 2>&1; then
        READY=1
        break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    echo "  Waiting for service readiness (attempt ${ATTEMPT}/${MAX_ATTEMPTS})..."
    sleep 2
done

if [ $READY -ne 1 ]; then
    echo "ERROR: QuickPizza failed to become ready within $((MAX_ATTEMPTS * 2)) seconds."
    docker compose -f docker/compose.yml logs quickpizza
    exit 1
fi

echo ""
echo "=========================================================="
echo " QuickPizza Environment is READY!"
echo "=========================================================="
echo " Application:   http://localhost:3333"
echo " Prometheus:    http://localhost:9090"
echo " Grafana:       http://localhost:3000 (Admin / No Password)"
echo " Metrics:       http://localhost:3333/metrics"
echo "=========================================================="

# Run environment verification
"${SCRIPT_DIR}/environment-check.sh"
