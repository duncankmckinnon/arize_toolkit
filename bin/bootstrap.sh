#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Check if poetry is installed, and install it if not
if ! command -v poetry &> /dev/null; then
    echo "poetry is not installed. Installing poetry..."
    pip install --user poetry
    export PATH=$PATH:~/.local/bin
fi

# Install dependencies using poetry
echo "Installing dependencies using poetry..."
poetry install

# Success message
echo "Environment setup complete. You can now activate the environment using 'poetry env activate'."