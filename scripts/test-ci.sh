#!/bin/bash

# Test script to simulate CI environment locally
# This script runs the same commands as the GitHub Actions workflow

set -e

echo "🚀 Starting CI simulation..."

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: Not in a virtual environment. Consider using one."
fi

# Install system dependencies (Ubuntu/Debian)
echo "📦 Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y sqlite3 ansible sqlite3-dev

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .

# Run linting
echo "🔍 Running linting..."
flake8 core/ backends/ storage/ metadata/ cli/ tests/
mypy core/ backends/ storage/ metadata/ cli/

# Run all tests
echo "🧪 Running all tests..."
pytest tests/ -v --cov=core --cov=backends --cov=storage --cov=metadata --cov=cli --cov-report=html --cov-report=term-missing

# Run integration tests specifically
echo "🔗 Running integration tests..."
pytest tests/test_integration_demo_stack.py -v
pytest tests/test_integration_demo_stack_fixtures.py -v

# Run security checks
echo "🔒 Running security checks..."
pip install bandit safety
bandit -r core/ backends/ storage/ metadata/ cli/
safety check

# Test Docker build
echo "🐳 Testing Docker build..."
docker build -t transactional-installer .
docker run --rm transactional-installer --help

echo "✅ CI simulation completed successfully!"
echo "📊 Coverage report available in htmlcov/index.html" 