#!/bin/bash
# Test runner script for AMPIS backend

set -e

echo "Running AMPIS Backend Test Suite"
echo "================================="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "pytest not found. Installing test dependencies..."
    pip install -r requirements.txt
fi

echo "Running unit tests..."
pytest tests/ -v --tb=short

echo ""
echo "Running integration tests..."
pytest tests/test_integration.py -v

echo ""
echo "Test coverage report:"
pytest tests/ --cov=app --cov-report=term-missing

echo ""
echo "✓ All tests passed!"
