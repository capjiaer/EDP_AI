#!/bin/bash
# 
# EDP Main wrapper script for bash users
# The real script is in the same directory as the linked shell script
# ref: edp_center/main/cli.py

# Find the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
SRC_FILE="${SCRIPT_DIR}/edp.py"

# Execute file
# Default py path: use environment variable or system python3
# Users can set EDP_PYTHON_PATH environment variable to use specific Python interpreter
# Example: export EDP_PYTHON_PATH=/usrhome/chenanping/tools/python3.9.16/bin/python3.9

if [ -n "$EDP_PYTHON_PATH" ]; then
    # Use user-specified Python path
    PYTHON_PATH="$EDP_PYTHON_PATH"
elif command -v python3 >/dev/null 2>&1; then
    # Try python3 first
    PYTHON_PATH=$(command -v python3)
elif command -v python >/dev/null 2>&1; then
    # Fall back to python
    PYTHON_PATH=$(command -v python)
elif [ -f /usr/bin/python3 ]; then
    PYTHON_PATH=/usr/bin/python3
elif [ -f /usr/local/bin/python3 ]; then
    PYTHON_PATH=/usr/local/bin/python3
elif [ -f /usr/bin/python ]; then
    PYTHON_PATH=/usr/bin/python
elif [ -f /usr/local/bin/python ]; then
    PYTHON_PATH=/usr/local/bin/python
else
    # Last resort: try python3, then python
    PYTHON_PATH=python3 || PYTHON_PATH=python
fi

# Execute the Python script
exec "$PYTHON_PATH" "$SRC_FILE" "$@"

