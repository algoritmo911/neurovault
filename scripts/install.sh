#!/bin/bash

# This script automates the installation of Mnemosyne Core.

echo "Setting up Mnemosyne Core..."

# Create a virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Installation complete."
