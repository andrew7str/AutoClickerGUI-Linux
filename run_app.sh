#!/bin/bash

# Navigate to the directory where the script is located
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR"

# Activate the virtual environment
source venv/bin/activate

# Run the Python application
python3 main.py

# Deactivate the virtual environment (optional, but good practice)
deactivate
