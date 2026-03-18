#!/bin/bash
# NAM Trainer launcher script
# Detects available Python and runs the queue window

set -e

cd "$(dirname "$0")"

# Find Python interpreter (try in order of preference)
for python_cmd in python3 python python3.12 python3.11 python3.10; do
    if command -v "$python_cmd" &> /dev/null; then
        PYTHON_CMD="$python_cmd"
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "Error: Python 3 not found. Please install Python 3.10 or later."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "Using Python $PYTHON_VERSION"

# Check if nam-full is available
if ! command -v nam-full &> /dev/null; then
    echo "Warning: nam-full not found in PATH."
    echo "Install with: pip install neural-amp-modeler[cli]"
    echo ""
fi

# Run the queue window
exec "$PYTHON_CMD" test_queue.py
