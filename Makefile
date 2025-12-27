.PHONY: test test-unit test-integration test-e2e test-smoke test-coverage test-verbose test-failed clean help

# Default Python interpreter
PYTHON := python3
PYTEST := pytest
# Ensure hotel module can be imported
export PYTHONPATH := $(PWD):$(PYTHONPATH)

help:
	@echo "Available targets:"
	@echo "  test              - Run all tests"
	@echo "  test-unit         - Run unit tests only"
	@echo "  test-integration  - Run integration tests only"
	@echo "  test-e2e          - Run end-to-end tests only"
	@echo "  test-smoke        - Run smoke tests (critical tests)"
	@echo "  test-booking      - Run booking-related tests"
	@echo "  test-customer     - Run customer-related tests"
	@echo "  test-room         - Run room-related tests"
	@echo "  test-coverage     - Run tests with coverage report"
	@echo "  test-verbose      - Run tests with verbose output"
	@echo "  test-failed       - Re-run only failed tests"
	@echo "  test-watch        - Run tests in watch mode (requires pytest-watch)"
	@echo "  clean             - Remove test artifacts and cache"

# Run all tests
test:
	$(PYTEST)

# Run unit tests
test-unit:
	$(PYTEST) -m unit

# Run integration tests
test-integration:
	$(PYTEST) -m integration

# Run end-to-end tests
test-e2e:
	$(PYTEST) -m e2e

# Run smoke tests (critical tests before deployment)
test-smoke:
	$(PYTEST) -m smoke

# Run domain-specific tests
test-booking:
	$(PYTEST) -m booking

test-customer:
	$(PYTEST) -m customer

test-room:
	$(PYTEST) -m room

# Run with coverage
test-coverage:
	$(PYTEST) --cov=hotel --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

# Run with verbose output
test-verbose:
	$(PYTEST) -vv

# Re-run only failed tests
test-failed:
	$(PYTEST) --lf

# Run in watch mode (requires pytest-watch)
test-watch:
	ptw

# Quick test (unit + smoke, no warnings)
test-quick:
	$(PYTEST) -m "unit and smoke" -q --disable-warnings

# Clean test artifacts
clean:
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -f tests.log
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Install test dependencies
install-test-deps:
	pip install pytest pytest-cov pytest-mock pytest-xdist pytest-watch

# Run tests in parallel (requires pytest-xdist)
test-parallel:
	$(PYTEST) -n auto

# Run tests and open coverage report
test-and-coverage: test-coverage
	@echo "Opening coverage report..."
	open htmlcov/index.html || xdg-open htmlcov/index.html
