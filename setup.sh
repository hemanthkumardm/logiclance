#!/bin/bash

cd "$(dirname "$0")"

# Optional: Create and activate a virtual environment
# python3 -m venv venv
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the GUI
python3 setup_gui/main.py


