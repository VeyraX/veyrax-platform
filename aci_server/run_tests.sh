#!/usr/bin/env bash

set -eo pipefail  # Exit on error and ensure pipeline errors are caught

echo "Starting Test Runner..."

# Navigate to project root if necessary
cd "$(dirname "$0")"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found, proceeding without it."
else
    echo "Loading environment variables..."
    set -a 
    source .env
    set +a
fi

# Clean up Python cache files
echo "Cleaning up Python cache files..."
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete

# Determine test path
SEARCH_PATH="./integrations"
if [ -n "$1" ]; then
    SEARCH_PATH="./integrations/$1"
    echo "Running tests for integration: $1"
fi

# Run tests
EXIT_CODE=0  # Track test failures

echo "Finding test files..."
for test_file in $(find "$SEARCH_PATH" -name "tests.py"); do
    echo "Running tests in: $test_file"
    echo "----------------------------------------"
    
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PYTHONPATH:. pytest "$test_file" -v -s -W ignore::DeprecationWarning -W ignore::UserWarning || EXIT_CODE=$?
    
    echo "----------------------------------------"
    echo
done

echo "Test execution finished."

# Exit with failure code if any test failed
exit $EXIT_CODE
