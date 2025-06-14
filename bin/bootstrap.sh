#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define virtual environment name (based on project name)
VENV_NAME="arize-toolkit-venv"

# Make sure uv is on PATH
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Add uv to PATH for the duration of this script
    export PATH="$HOME/.local/bin:$PATH"
    # Also try the cargo bin directory in case it was installed there
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create virtual environment using uv
echo "Creating virtual environment with uv..."
uv venv "$VENV_NAME"

# Activate the virtual environment
source "$VENV_NAME/bin/activate"

# Install dependencies using uv (including dev and integration groups)
echo "Installing dependencies using uv..."
uv pip install -e ".[dev,integration]"

# Success message
echo "Environment setup complete!"

# Print instructions for activating the virtual environment
echo "To activate the virtual environment, run:"
echo "source $VENV_NAME/bin/activate"
