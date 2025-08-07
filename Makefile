.PHONY: help install test lint format clean docker-build docker-run docker-test

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install the package in development mode
	pip install -e .

install-dev: ## Install development dependencies
	pip install -r requirements-dev.txt
	pre-commit install

test: ## Run tests
	pytest -v --cov=core --cov=backends --cov=storage --cov=metadata --cov=cli --cov-report=term-missing

test-html: ## Run tests with HTML coverage report
	pytest --cov=core --cov=backends --cov=storage --cov=metadata --cov=cli --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

lint: ## Run linting
	flake8 core/ backends/ storage/ metadata/ cli/ tests/
	mypy core/ backends/ storage/ metadata/ cli/

format: ## Format code
	black core/ backends/ storage/ metadata/ cli/ tests/
	isort core/ backends/ storage/ metadata/ cli/ tests/

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ htmlcov/ .coverage .pytest_cache/
	rm -rf docs/build/

docs: ## Build documentation
	@echo "Building documentation..."
	@./scripts/build-docs.sh

docs-serve: docs ## Build and serve documentation locally
	@echo "Serving documentation at http://localhost:8000"
	@cd docs/build && python3 -m http.server 8000

docker-build: ## Build Docker image
	docker build -t transactional-installer .

docker-run: ## Run Docker container
	docker run --privileged -v /var/lib/transactional-installer:/var/lib/transactional-installer transactional-installer

docker-test: ## Run tests in Docker
	docker-compose run test-runner

docker-clean: ## Clean up Docker containers and images
	docker-compose down
	docker rmi transactional-installer

create-example: ## Create example package metadata
	transactional-installer create-template example-package 1.0.0 -o examples/example.yml

validate-example: ## Validate example package
	transactional-installer validate examples/webapp.yml

check-all: format lint test ## Run all checks (format, lint, test)

ci: install-dev check-all ## Run CI pipeline locally 