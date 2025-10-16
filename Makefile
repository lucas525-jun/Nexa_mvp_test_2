.PHONY: help install install-dev clean lint format test test-cov validate check all run pre-commit-install pre-commit-run pre-commit-update

# Default target
help:
	@echo "Available commands:"
	@echo "  make install            - Install production dependencies"
	@echo "  make install-dev        - Install development dependencies"
	@echo "  make pre-commit-install - Install pre-commit hooks"
	@echo "  make pre-commit-run     - Run pre-commit on all files"
	@echo "  make pre-commit-update  - Update pre-commit hooks to latest versions"
	@echo "  make lint               - Run all linters (flake8, black check, isort check)"
	@echo "  make format             - Auto-format code with black and isort"
	@echo "  make test               - Run tests"
	@echo "  make test-cov           - Run tests with coverage report"
	@echo "  make validate           - Run full validation (lint + test)"
	@echo "  make check              - Same as validate (lint + test)"
	@echo "  make all                - Format, lint, and test"
	@echo "  make run                - Start the development server"
	@echo "  make clean              - Remove generated files and caches"

# Install dependencies
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# Pre-commit hooks
pre-commit-install:
	@echo "Installing pre-commit hooks..."
	@pre-commit install
	@pre-commit install --hook-type commit-msg
	@echo "✓ Pre-commit hooks installed!"

pre-commit-run:
	@echo "Running pre-commit on all files..."
	@pre-commit run --all-files

pre-commit-update:
	@echo "Updating pre-commit hooks..."
	@pre-commit autoupdate

# Linting
lint: lint-flake8 lint-black lint-isort

lint-flake8:
	@echo "Running flake8..."
	@flake8 app tests --count --select=E9,F63,F7,F82 --show-source --statistics
	@flake8 app tests --count --max-complexity=10 --max-line-length=100 --statistics

lint-black:
	@echo "Checking code formatting with black..."
	@black --check app tests

lint-isort:
	@echo "Checking import sorting with isort..."
	@isort --check-only app tests

# Auto-formatting
format: format-black format-isort

format-black:
	@echo "Formatting code with black..."
	@black app tests

format-isort:
	@echo "Sorting imports with isort..."
	@isort app tests

# Testing
test:
	@echo "Running tests..."
	@pytest tests/ -v

test-cov:
	@echo "Running tests with coverage..."
	@pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

test-quick:
	@echo "Running tests (fast mode, no coverage)..."
	@pytest tests/ -v -x

# Full validation (like CI)
validate: lint test
	@echo "✓ All validation checks passed!"

check: validate

# All: format, lint, and test
all: format lint test
	@echo "✓ Format, lint, and test completed!"

# Run development server
run:
	@echo "Starting development server..."
	@python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Cleanup
clean:
	@echo "Cleaning up generated files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".coverage" -exec rm -f {} + 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@find . -type f -name "coverage.xml" -delete 2>/dev/null || true
	@rm -f *.db 2>/dev/null || true
	@echo "✓ Cleanup complete!"

# Docker commands
docker-build:
	@echo "Building Docker image..."
	@docker-compose build

docker-up:
	@echo "Starting Docker containers..."
	@docker-compose up -d

docker-down:
	@echo "Stopping Docker containers..."
	@docker-compose down

docker-logs:
	@docker-compose logs -f

# CI simulation (run what CI runs)
ci: lint test-cov
	@echo "✓ CI checks passed!"
