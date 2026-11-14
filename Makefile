.PHONY: help setup check test-unit smoke load stress spike soak regression compare report browser-headed browser-headless clean clean-all

help:
	@echo "QuickPizza Performance Engineering Framework"
	@echo "============================================"
	@echo "make setup             - Bootstrap environment, install dependencies, start containers"
	@echo "make check             - Verify environment health and readiness"
	@echo "make test-unit         - Run Python unit test suite"
	@echo "make smoke             - Run 30s smoke sanity test"
	@echo "make load              - Run operational load test (25 VUs)"
	@echo "make stress            - Run progressive stress test (up to 100 VUs)"
	@echo "make spike             - Run sudden spike test (50 VUs)"
	@echo "make soak              - Run sustained endurance soak test (15m)"
	@echo "make regression        - Run regression test and compare with baseline"
	@echo "make browser-headed    - Run browser automation in visible headed mode"
	@echo "make browser-headless  - Run browser automation in headless mode"
	@echo "make report            - Generate executive HTML, JSON, and CSV reports"
	@echo "make clean             - Stop containers and preserve database"
	@echo "make clean-all         - Stop containers and remove volumes"

setup:
	@./scripts/setup.sh

check:
	@./scripts/environment-check.sh

test-unit:
	@source .venv/bin/activate && pytest -v

smoke:
	@./scripts/run-smoke.sh
	@source .venv/bin/activate && python3 -m python.cli report --input results/raw/smoke-summary.json --html results/reports/smoke_report.html

load:
	@./scripts/run-load.sh
	@source .venv/bin/activate && python3 -m python.cli report --input results/raw/load-summary.json --html results/reports/load_report.html

stress:
	@./scripts/run-stress.sh
	@source .venv/bin/activate && python3 -m python.cli report --input results/raw/stress-summary.json --html results/reports/stress_report.html

spike:
	@./scripts/run-spike.sh
	@source .venv/bin/activate && python3 -m python.cli report --input results/raw/spike-summary.json --html results/reports/spike_report.html

soak:
	@./scripts/run-soak.sh
	@source .venv/bin/activate && python3 -m python.cli report --input results/raw/soak-summary.json --html results/reports/soak_report.html

regression:
	@./scripts/run-regression.sh
	@source .venv/bin/activate && python3 -m python.cli compare --current results/raw/regression-summary.json
	@source .venv/bin/activate && python3 -m python.cli report --input results/raw/regression-summary.json --baseline baselines/approved-baseline.json --html results/reports/regression_report.html

browser-headed:
	@./scripts/run-browser.sh true

browser-headless:
	@./scripts/run-browser.sh false

report:
	@source .venv/bin/activate && python3 -m python.cli report --input results/raw/regression-summary.json --baseline baselines/approved-baseline.json

clean:
	@./scripts/cleanup.sh

clean-all:
	@./scripts/cleanup.sh --all
