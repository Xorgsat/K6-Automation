# QuickPizza Performance Engineering Framework

A production-grade, evidence-driven Performance Engineering and SDET framework designed for comprehensive workload modeling, automated load generation, telemetry correlation, regression detection, and executive reporting against Grafana QuickPizza.

---

## 1. Project Overview

The **QuickPizza Performance Engineering Framework** is an enterprise-ready performance testing system built to assess, monitor, and gate the reliability, latency profiles, throughput limits, and resource utilization of [Grafana QuickPizza](https://github.com/grafana/quickpizza).

Moving beyond trivial load scripts, this framework implements rigorous SDET and Performance Architecture principles:
- **Mathematical Workload Modeling:** Little's Law, open vs. closed workload models, think-time distributions.
- **Controlled Multi-Tier Execution:** Sanity smoke, steady-state load, progressive stress, sudden spike, long-term soak, and regression suites.
- **Automated Regression Engine:** Statistical percentile analysis (p50, p90, p95, p99), variance and noise thresholds, automated baseline storage, and pass/fail gate evaluation.
- **Deep Observability:** Integration with Prometheus metrics, Grafana dashboards, OpenTelemetry traces, and Tempo distributed tracing.
- **Executive Reporting:** Standalone interactive HTML reports with responsive CSS, embedded SVG/PNG charts, JSON metadata, and CSV summary exports.
- **Continuous Performance CI/CD:** Native GitHub Actions pipelines for automated smoke gating, regression checks, and manual load runs with strict safety bounds.

---

## 2. Engineering Objectives

1. **Measurement Before Assumptions:** All performance limits, degradation curves, and saturation points are backed by empirical telemetry, not arbitrary estimates.
2. **Realistic User Journeys:** Emulate authentic user behavior through weighted, modular user flows (catalog browsing, recommendation requests, and authenticated rating submissions) with Gaussian think time.
3. **Automated Quality Gating:** Prevent performance degradation in CI/CD by comparing PR execution metrics against approved historical baselines with statistical confidence intervals.
4. **Safety & Responsible Testing:** Enforce target domain allowlisting, concurrency caps, and duration bounds to prevent accidental denial-of-service against unauthorized environments.
5. **Observability Alongside Load Generation:** Correlate client-side k6 metrics with server-side system telemetry and distributed traces using unique correlation IDs.

---

## 3. Architecture Diagram

```
+---------------------------------------------------------------------------------------+
|                                CI/CD & CLI Interface                                   |
|   - GitHub Actions (Smoke, Regression Gate, Manual Workflow)                          |
|   - GNU Makefile & Shell Runners (make setup, smoke, load, stress, regression)         |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                                k6 Load Generation Layer                               |
|   +-------------------+  +--------------------+  +---------------------------------+  |
|   |  Shared HTTP Lib  |  |  User Journeys     |  | Workload Config & Scenarios    |  |
|   |  (Auth, Checks,   |  |  (Browse Catalog,  |  | (Ramping VUs, Arrival Rates,    |  |
|   |   Metrics)        |  |   Pizza, Ratings)  |  |  Soak, Spike, Stress)          |  |
|   +-------------------+  +--------------------+  +---------------------------------+  |
+---------------------------------------------------------------------------------------+
                     | (HTTP / REST)                            | (Telemetry Export)
                     v                                          v
+------------------------------------------+    +---------------------------------------+
|      Application Under Test (AUT)        |    |    Observability Stack (Docker)       |
|          Grafana QuickPizza              |    |                                       |
|  - REST API (:3333)                      |--->|  - Prometheus (:9090)                 |
|  - Health & Readiness (/healthz, /ready) |    |  - Grafana Dashboards (:3000)         |
|  - OpenTelemetry Tracing Exporter        |    |  - Tempo Distributed Tracing (:3200)  |
|  - SQLite / In-Memory DB                 |    |  - Pyroscope Continuous Profiling     |
+------------------------------------------+    +---------------------------------------+
                     |
                     v (Summary JSON Output)
+---------------------------------------------------------------------------------------+
|                           Python Analysis & Reporting Engine                          |
|   +------------------------------------+  +----------------------------------------+  |
|   | Result Ingestion & Validation      |  | Statistical Analysis (Percentiles,     |  |
|   | (Pydantic / Custom Schemas)        |  |  StdDev, IQR, Confidence Intervals)   |  |
|   +------------------------------------+  +----------------------------------------+  |
|   +------------------------------------+  +----------------------------------------+  |
|   | Baseline Manager & Comparator      |  | Automated HTML/JSON/CSV Report Gen     |  |
|   | (Noise filtering, Regr Detection)  |  | (Standalone HTML, Charts, CI summary)  |  |
|   +------------------------------------+  +----------------------------------------+  |
+---------------------------------------------------------------------------------------+
```

---

## 4. Technology Stack

- **Load Generator:** Grafana k6 (JavaScript ES6+, multi-executor support).
- **Target Application:** Grafana QuickPizza (Go, Chi router, SQLite/PostgreSQL, OpenTelemetry).
- **Analysis & Reporting Engine:** Python 3.9+ (`matplotlib`, `jinja2`, `pytest`).
- **Telemetry & Visualization:** Prometheus, Grafana, Grafana Tempo, OpenTelemetry Collector.
- **Orchestration & Automation:** Docker & Docker Compose, GNU Make, Bash, GitHub Actions.

---

## 5. Application Under Test (AUT)

The target application is **Grafana QuickPizza** (commit `a000faecae2201877b7a3fda4aaeb37848bb04d1`).
QuickPizza provides:
- **Catalog Services:** `GET /api/doughs`, `GET /api/tools`, `GET /api/ingredients/{type}`.
- **Recommendation Engine:** `POST /api/pizza` (calculates combinatorial toppings and calories).
- **Ratings & Reviews:** `GET /api/ratings`, `POST /api/ratings`, `PUT /api/ratings/{id}`.
- **Health & Telemetry:** `GET /ready`, `GET /healthz`, `GET /metrics`.

---

## 6. Framework Features

1. **Modular k6 Architecture:** Centralized client (`k6/lib/http-client.js`), automated authentication handling, and reusable journey modules (`k6/scenarios/`).
2. **Comprehensive Workload Profiles:** Pre-configured and parameterized profiles in `config/workloads.json` for smoke, load, stress, spike, soak, and regression.
3. **Statistical Ingestion Engine:** Parses raw k6 summary JSON into structured metric objects calculating p50, p90, p95, p99, mean, standard deviation, and interquartile range.
4. **Baseline Management & Regression Detection:** Evaluates current test runs against verified baselines, categorizing results as `IMPROVEMENT`, `NEGLIGIBLE`, `WARNING`, or `CRITICAL_REGRESSION` with noise suppression.
5. **Multi-Format Reporting:** Generates self-contained HTML dashboards with embedded base64 CSS, charts, JSON summaries, and machine-readable CSV files.
6. **Safety Allowlisting:** Hardcoded localhost/127.0.0.1 validation prevents unintended traffic injection into production environments.
7. **Comprehensive Unit Test Suite:** 22 unit tests validating Python parsers, statistical functions, regression detectors, and report generators.

---

## 7. Repository Structure

```
.
├── Makefile                     # Root workflow orchestration
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration
├── config/                      # Test configurations
│   ├── environments/            # Environment profiles (local, ci)
│   ├── thresholds.json          # SLA/SLO threshold boundaries
│   ├── workloads.json           # Execution stage definitions
│   └── test-settings.json       # General framework parameters
├── baselines/                   # Approved historical baselines
│   ├── approved-baseline.json   # Active reference baseline
│   └── metadata/                # Archival metadata & provenance
├── docker/                      # Observability stack definitions
│   ├── compose.yml              # Local QuickPizza + Grafana/Prometheus
│   ├── grafana/                 # Dashboards & datasource configurations
│   └── monitoring/              # Prometheus, Tempo, Alloy configs
├── docs/                        # Engineering documentation
│   ├── application-analysis.md  # Deep architectural discovery of QuickPizza
│   ├── architecture.md          # Framework design decisions & component roles
│   ├── environment-setup.md     # Deployment & local reproducibility guide
│   ├── workload-model.md        # Workload calculations & Little's Law rationale
│   ├── performance-strategy.md  # Testing philosophy, SLAs, & execution lifecycle
│   └── bottleneck-investigation.md # Empirical investigation & case study
├── k6/                          # k6 test scripts & libraries
│   ├── config/                  # JS configuration loaders
│   ├── lib/                     # Shared client, auth, checks, metrics, test data
│   ├── scenarios/               # User journey modules (catalog, pizza, ratings)
│   ├── runner/                  # Unified multi-scenario runner
│   ├── setup/                   # Pre-flight environment verifier
│   └── tests/                   # Scenario wrappers (smoke, load, stress, spike, soak, regression)
├── python/                      # Python analysis & reporting engine
│   ├── analysis/                # Statistical, percentile, throughput, error parsers
│   ├── regression/              # Baseline manager & regression detector
│   ├── reporting/               # HTML template, chart generator, CLI exporters
│   ├── validation/              # Schema validator for k6 JSON outputs
│   └── cli.py                   # Unified CLI entrypoint
├── results/                     # Test outputs (raw JSON, charts, reports)
├── scripts/                     # Shell automation wrappers
├── tests/                       # Framework unit tests
└── .github/workflows/           # CI/CD pipelines
```

---

## 8. Prerequisites

- **macOS** or **Linux (Ubuntu 20.04+)**
- **Docker & Docker Compose** (v24+)
- **k6** (v0.48.0+)
- **Python** (v3.9+) with `pip` and `venv`
- **GNU Make** and **Git**

---

## 9. Installation

Clone this repository and initialize the Python virtual environment:

```bash
git clone <repo-url> performance-engineering-framework
cd performance-engineering-framework

# Create Python virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Verify framework unit tests:
```bash
pytest -v
```

---

## 10. Environment Setup

Bootstrap the local target application and observability infrastructure:

```bash
make setup
# or: ./scripts/setup.sh
```

Verify application readiness and telemetry endpoints:

```bash
make check
# or: ./scripts/environment-check.sh
```

Service endpoints initialized:
- **QuickPizza Web & API:** `http://localhost:3333`
- **Prometheus Metrics:** `http://localhost:9090`
- **Grafana Dashboards:** `http://localhost:3000` (admin / admin)
- **Tempo Distributed Tracing:** `http://localhost:3200`

---

## 11. Running Performance Tests

### 11.1 Smoke Test
*Purpose: Fast sanity check (1-2 VUs, 30s) verifying connectivity, authentication, and HTTP 200s.*
```bash
make smoke
# or: ./scripts/run-smoke.sh
```

### 11.2 Load Test
*Purpose: Evaluate steady-state performance under expected normal operations (25 VUs, 5 minutes).*
```bash
make load
# or: ./scripts/run-load.sh
```

### 11.3 Stress Test
*Purpose: Step-up concurrency (up to 100 VUs) to detect knee points, resource saturation, and DB lock contention.*
```bash
make stress
# or: ./scripts/run-stress.sh
```

### 11.4 Spike Test
*Purpose: Immediate surge (from 1 to 50 VUs in 10s) to assess recovery behavior and error absorption.*
```bash
make spike
# or: ./scripts/run-spike.sh
```

### 11.5 Soak Test
*Purpose: Sustained moderate load (10 VUs for 15 minutes) to evaluate memory leaks and connection exhaustion.*
```bash
make soak
# or: ./scripts/run-soak.sh
```

---

## 12. Analysing Results, Baselines & Regression

### 12.1 Comparing Against Approved Baseline
Execute a regression run and automatically compare against `baselines/approved-baseline.json`:

```bash
make regression
# or: ./scripts/run-regression.sh
```

To run the comparison manually against any raw test result:

```bash
source .venv/bin/activate
python -m python.cli compare \
  --current results/raw/current-run-summary.json \
  --baseline baselines/approved-baseline.json \
  --output results/processed/comparison_result.json
```

### 12.2 Managing Baselines
Save the latest verified run as an approved baseline:

```bash
source .venv/bin/activate
python -m python.cli baseline-save \
  --input results/raw/load-summary.json \
  --tag "v1.0.0-release-baseline"
```

---

## 13. Generating Performance Reports

Generate a self-contained executive HTML report with responsive CSS, charts, and metrics:

```bash
source .venv/bin/activate
python -m python.cli report \
  --input results/raw/stress-summary.json \
  --baseline baselines/approved-baseline.json \
  --html results/reports/executive_report.html \
  --json results/processed/executive_metrics.json \
  --csv results/reports/metrics_summary.csv
```

View the generated report by opening `results/reports/executive_report.html` in any browser.

---

## 14. Grafana Dashboards

Access pre-provisioned Grafana dashboards at `http://localhost:3000`:
- **QuickPizza Performance Overview:** Real-time request rates, p50/p90/p99 response times, and HTTP status distributions.
- **k6 Load Generator Dashboard:** VU concurrency, request iterations, check success percentages, and network I/O.
- **System Resource Telemetry:** Host CPU, memory usage, and container health.

---

## 15. GitHub Actions Workflows

The framework includes automated CI/CD workflows:
1. **`validation.yml`**: Runs Python unit tests and validates k6 JavaScript syntax on all pull requests.
2. **`smoke.yml`**: Boots the Docker stack, runs a smoke test, generates an HTML report, and uploads artifacts.
3. **`performance-regression.yml`**: Gating pipeline comparing pull request performance against the approved baseline. Fails if critical regressions are detected.
4. **`manual-workload.yml`**: Dispatched manual testing allowing parameterized execution of `load`, `stress`, `spike`, or `soak` tests with duration and URL safety limits.

---

## 16. Technical Decision Justifications

### 16.1 Workload Selection Rationale
- **Smoke (1-2 VUs, 30s):** Minimal overhead, rapid execution in CI pull requests to catch breaking changes before deploying heavy load.
- **Load (25 VUs, 5m):** Derived via Little's Law ($N = X \times R$) based on an operational expectation of 20-30 requests/sec with realistic 500ms think time.
- **Stress (Step-up to 100 VUs):** Probes the limits of the single-process Go monolithic runtime and identifies SQLite lock contention points.
- **Spike (1 $\to$ 50 VUs in 10s):** Validates thread pool expansion and queueing behavior under flash-crowd conditions.
- **Soak (10 VUs, 15m):** Long-duration steady traffic to surface memory leaks, goroutine leaks, or file descriptor exhaustion.

### 16.2 Threshold Criteria Selection
- `http_req_duration: ['p(95)<300']`: QuickPizza's API is designed for interactive web sessions; 300ms represents the maximum acceptable threshold for recommendation generation before degrading user experience.
- `http_req_failed: ['rate<0.01']`: 99% success rate required across all test runs; transient connection glitches cannot exceed 1%.
- `checks: ['rate>0.99']`: Ensures that 99% of business logic assertions (status 200, valid JSON payload, non-empty pizza name) succeed.

### 16.3 k6 Executor Selection
- **`ramping-vus`**: Selected for smoke, stress, and spike workloads to smoothly transition concurrency levels and observe knee-points.
- **`constant-arrival-rate` / `ramping-arrival-rate`**: Used in open-model throughput tests to prevent virtual user coordinated omission and measure true system throughput independent of server response latency.

### 16.4 Test Data Management
- Read operations (`/api/doughs`, `/api/tools`, `/api/ingredients/{type}`) operate on immutable seed data.
- Write operations (`POST /api/ratings`) generate unique UUID-tagged payloads and cleanup generated resources via automated k6 `teardown()` hooks to ensure test idempotency.

### 16.5 Regression Classification Methodology
- Performance variations within $\pm 5\%$ are categorized as `NEGLIGIBLE` (expected system noise).
- Increases between $5\%$ and $15\%$ trigger `WARNING` status.
- Increases exceeding $+15\%$ or error rate increases exceeding $+1\%$ trigger `CRITICAL_REGRESSION`, failing the CI pipeline.

### 16.6 Bottleneck Investigation Methodology
- Correlate client-side k6 latency distribution with server-side OpenTelemetry span durations.
- Identify database write serialization by monitoring `database is locked` SQLite events during high-concurrency rating updates.

---

## 17. Safety & Data Protection

- **Localhost Default:** All tests target `http://localhost:3333` by default.
- **Domain Allowlisting:** Execution scripts reject non-localhost URLs unless explicitly overridden with authorization flags.
- **Zero Hardcoded Secrets:** Authentication credentials and tokens are loaded from environment variables or mock test accounts. Sensitive tokens are masked in logs and reports.

---

## 18. Troubleshooting

| Issue | Cause | Resolution |
| :--- | :--- | :--- |
| `failed to connect to localhost:3333` | QuickPizza container is starting or crashed | Check container logs: `docker compose -f docker/compose.yml logs quickpizza` |
| `k6: command not found` | k6 is not installed on the system | Install via Homebrew (`brew install k6`) or run containerized k6 |
| `ModuleNotFoundError` during report gen | Virtual environment is not activated | Activate virtualenv: `source .venv/bin/activate` |
| `database is locked` in logs | High concurrency on SQLite during ratings | Expected during stress testing (>50 VUs). Switch to WAL mode or PostgreSQL. |

---

## 19. Known Limitations

1. **SQLite Database Concurrency:** Default monolithic QuickPizza uses SQLite in journal mode, which limits concurrent write operations during heavy stress tests.
2. **Local Load Generator Affinity:** When running both k6 and QuickPizza on the same physical host, CPU resource contention can influence high-VU measurements. In enterprise production, k6 should be executed on an isolated load generator host.
3. **Profiling Overhead:** Enabling continuous Pyroscope profiling adds ~2-5% CPU overhead to the target application process.

---

## 20. Clean-Up

To stop application containers while preserving database state:
```bash
make clean
# or: ./scripts/cleanup.sh
```

To perform a complete teardown and purge all containers, networks, and volumes:
```bash
make clean-all
# or: ./scripts/cleanup.sh --all
```
