#!/bin/bash

# Exit on error
set -e

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    # Activate the virtual environment
    source venv/bin/activate
    
    # Upgrade pip and install requirements
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    # Just activate the existing virtual environment
    source venv/bin/activate
fi

# Run the FastAPI application
echo "Starting FastAPI application..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Deactivate virtual environment when done
deactivate
