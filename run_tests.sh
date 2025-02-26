#!/usr/bin/env bash

set -e  # Exit on error

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found"
    exit 1
fi

# Clean up __pycache__ directories and .pyc files
echo "Cleaning up Python cache files..."
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete

# Start Docker If Needed!
# docker-compose up -d

# Load .env variables
set -a 
source .env 2>/dev/null || { echo "Error loading .env file"; exit 1; }
set +a

# Set search path based on optional folder argument
SEARCH_PATH="aci_server/integrations"
if [ ! -z "$1" ]; then
    SEARCH_PATH="aci_server/integrations/$1"
    echo "Running tests for integration: $1"
fi

# Find and run tests one by one
find $SEARCH_PATH -name "tests.py" | while read -r test_file; do
    echo "Running tests in: $test_file"
    echo "----------------------------------------"
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PYTHONPATH:./aci_server pytest "$test_file" -v -s -W ignore::DeprecationWarning -W ignore::UserWarning
    echo "----------------------------------------"
    echo
done
