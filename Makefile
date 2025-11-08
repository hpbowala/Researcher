.PHONY: help install test lint format clean run

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	poetry install

test:  ## Run tests
	PYTHONPATH=src poetry run pytest tests/ -v

test-cov:  ## Run tests with coverage
	PYTHONPATH=src poetry run pytest tests/ --cov=researcher --cov-report=html --cov-report=term

lint:  ## Run linting tools
	poetry run flake8 --max-line-length=88 src/ tests/
	poetry run mypy src/

format:  ## Format code with black and isort
	poetry run black src/ tests/
	poetry run isort src/ tests/

format-check:  ## Check if code is formatted correctly
	poetry run black --check src/ tests/
	poetry run isort --check-only src/ tests/

clean:  ## Clean up generated files
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete

run:  ## Run the main application
	poetry run python src/researcher/main.py

run-hybrid:  ## Demonstrate hybrid configuration approach
	poetry run python src/researcher/hybrid_example.py

run-api-client:  ## Demonstrate API client configuration usage
	poetry run python src/researcher/api_client.py

setup-env:  ## Create sample .env file
	cp sample.env .env
	@echo "✅ Created .env file from sample.env"
	@echo "💡 Edit .env with your actual API keys"

dev-setup: install format lint test  ## Complete development setup 