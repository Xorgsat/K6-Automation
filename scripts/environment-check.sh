#!/usr/bin/env bash
set -eo pipefail

BASE_URL="${BASE_URL:-http://localhost:3333}"
PROMETHEUS_URL="${PROMETHEUS_URL:-http://localhost:9090}"
GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"

echo "=========================================================="
echo " QuickPizza Performance Framework: Environment Check"
echo "=========================================================="
echo "Target Base URL:     ${BASE_URL}"
echo "Prometheus URL:      ${PROMETHEUS_URL}"
echo "Grafana URL:         ${GRAFANA_URL}"
echo "----------------------------------------------------------"

# 1. Check CLI prerequisites
echo -n "[1/7] Checking CLI tools (k6, docker, python3)... "
command -v k6 >/dev/null 2>&1 || { echo "FAIL: k6 not found in PATH"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "FAIL: docker not found in PATH"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "FAIL: python3 not found in PATH"; exit 1; }
echo "OK (k6 $(k6 version | awk '{print $2}'), $(python3 --version))"

# 2. Check Docker daemon
echo -n "[2/7] Checking Docker daemon status... "
docker info >/dev/null 2>&1 || { echo "FAIL: Docker daemon is not running"; exit 1; }
echo "OK"

# 3. Check QuickPizza Liveness
echo -n "[3/7] Probing QuickPizza liveness (${BASE_URL}/healthz)... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/healthz" || echo "000")
if [ "$HTTP_CODE" -ne 200 ]; then
    echo "FAIL: Expected HTTP 200, got ${HTTP_CODE}"
    exit 1
fi
echo "OK (HTTP 200)"

# 4. Check QuickPizza Readiness
echo -n "[4/7] Probing QuickPizza readiness (${BASE_URL}/ready)... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/ready" || echo "000")
if [ "$HTTP_CODE" -ne 200 ]; then
    echo "FAIL: Expected HTTP 200, got ${HTTP_CODE}"
    exit 1
fi
echo "OK (HTTP 200)"

# 5. Check Prometheus
echo -n "[5/7] Probing Prometheus health (${PROMETHEUS_URL}/-/healthy)... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${PROMETHEUS_URL}/-/healthy" || echo "000")
if [ "$HTTP_CODE" -ne 200 ]; then
    echo "WARNING: Prometheus unhealthy or not started (HTTP ${HTTP_CODE})"
else
    echo "OK (HTTP 200)"
fi

# 6. Check Grafana
echo -n "[6/7] Probing Grafana health (${GRAFANA_URL}/api/health)... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${GRAFANA_URL}/api/health" || echo "000")
if [ "$HTTP_CODE" -ne 200 ]; then
    echo "WARNING: Grafana unhealthy or not started (HTTP ${HTTP_CODE})"
else
    echo "OK (HTTP 200)"
fi

# 7. Check Functional Recommendation & Auth API
echo -n "[7/7] Validating Pizza Recommendation & Auth Token API... "
REC_RESP=$(curl -s -X POST "${BASE_URL}/api/pizza" \
    -H "Content-Type: application/json" \
    -H "Authorization: Token abcdef0123456789" \
    -d '{"maxCaloriesPerSlice": 800, "mustBeVegetarian": false}')

PIZZA_NAME=$(echo "$REC_RESP" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('pizza', {}).get('name', ''))" 2>/dev/null || echo "")

if [ -z "$PIZZA_NAME" ]; then
    echo "FAIL: Invalid recommendation response: ${REC_RESP}"
    exit 1
fi
echo "OK (Generated: \"${PIZZA_NAME}\")"

echo "----------------------------------------------------------"
echo "All critical environment checks PASSED successfully."
echo "=========================================================="
exit 0
