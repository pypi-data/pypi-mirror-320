.PHONY: init build test clean install dev fmt check help

# Install development dependencies
init:
	pip install maturin pytest black ruff

# Build Rust library and Python bindings
build:
	maturin develop --release

# Run Python tests
test:
	pytest tests -v

# Clean build artifacts
clean:
	cargo clean
	rm -rf target/
	rm -rf *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +

# Install in development mode
dev:
	pip install -e ".[dev]"

# Install for production
install:
	pip install .

# Format code
fmt:
	cargo fmt
	black tests/

# Run checks (formatting, linting)
check:
	cargo fmt -- --check
	cargo clippy -- -D warnings
	black --check tests/
	ruff check tests/

# Help target
help:
	@echo "Available targets:"
	@echo "  init     - Install development dependencies"
	@echo "  build    - Build Rust library and Python bindings"
	@echo "  test     - Run Python tests"
	@echo "  clean    - Clean build artifacts"
	@echo "  dev      - Install in development mode"
	@echo "  install  - Install for production"
	@echo "  fmt      - Format code"
	@echo "  check    - Run code checks"
	@echo "  help     - Show this help message"
