# QuickPizza Test Environment Setup & Verification Guide

**Document Status:** Verified & Active  
**Execution Environment:** macOS (darwin/arm64, Apple Silicon)  
**Author:** Senior SDET / Performance Engineering Architect  

---

## 1. System Inventory and Verified Component Versions

| Component | Target Version / Tag | Verified Runtime Version | Port Mapping | Healthcheck Endpoint |
|---|---|---|---|---|
| **QuickPizza** | `ghcr.io/grafana/quickpizza-local:0.15.30` | QuickPizza Go 1.23+ | `3333:3333`, `3334:3334` | `http://localhost:3333/ready` |
| **PostgreSQL** | `postgres:18.6` | PostgreSQL 18.6 | `5432:5432` | `pg_isready -U postgres` |
| **Prometheus** | `prom/prometheus:v3.15.0` | Prometheus 3.15.0 | `9090:9090` | `http://localhost:9090/-/healthy` |
| **Grafana** | `grafana/grafana:13.0.1` | Grafana 13.0.1 | `3000:3000` | `http://localhost:3000/api/health` |
| **Grafana k6** | Homebrew formula `k6` | `k6 v2.4.0 (darwin/arm64)` | Local client | `k6 version` |
| **Python** | Python 3.9.6 | Python 3.9.6 (`.venv`) | Local client | `python3 -V` |
| **Docker** | Docker Desktop 29.9.2 | API 1.56, Compose v5.6.1 | Daemon | `docker info` |

---

## 2. Bootstrapping the Environment

### Automated Setup
To initialize the Python virtual environment and start all necessary services in one command:

```bash
./scripts/setup.sh
```

### Manual Setup Steps
1. **Initialize Python Virtual Environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **Start Docker Infrastructure:**
   ```bash
   docker compose -f docker/compose.yml up -d quickpizza-db quickpizza prometheus grafana
   ```

3. **Verify Environment Sanity:**
   ```bash
   ./scripts/environment-check.sh
   ```

---

## 3. Environment Teardown

To stop the containers while preserving database volume state:
```bash
./scripts/cleanup.sh
```

To perform a complete teardown including removing PostgreSQL volumes and orphan networks:
```bash
./scripts/cleanup.sh --all
```

---

## 4. Pre-Provisioned Observability Dashboards

Once Grafana is running at `http://localhost:3000`, the following pre-configured dashboards are provisioned and immediately accessible (anonymous admin access enabled):

- **k6 Prometheus (Native Histograms):** `http://localhost:3000/d/k6-native-histograms`
- **QuickPizza Overview:** `http://localhost:3000/d/quickpizza_overview`
- **QuickPizza Performance:** `http://localhost:3000/d/quickpizza_performance`
- **QuickPizza Logs:** `http://localhost:3000/d/quickpizza_logs`
