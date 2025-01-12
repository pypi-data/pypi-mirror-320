# Python commands
PYTHON := python3
PIP := $(PYTHON) -m pip

.PHONY: install build clean publish test lint format

# Install dependencies
install:
	$(PIP) install -e .

# Development setup
dev-setup:
	$(PIP) install hatch twine build black isort flake8

# Build the package
build: clean
	$(PYTHON) -m build

# Clean build artifacts
clean:
	rm -rf dist/ build/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +

# Run tests
test:
	$(PYTHON) -m pytest

# Run linting
lint:
	flake8 src/arma3cli
	black --check src/arma3cli
	isort --check-only src/arma3cli

# Format code
format:
	black src/arma3cli
	isort src/arma3cli

# Build and publish to PyPI
publish: build
	twine upload dist/*

# Help command
help:
	@echo "Available commands:"
	@echo "  make install        - Install package locally"
	@echo "  make dev-setup     - Install development tools"
	@echo "  make build         - Build the package"
	@echo "  make clean         - Remove build artifacts"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linting checks"
	@echo "  make format        - Format code"
	@echo "  make publish       - Publish to PyPI"


