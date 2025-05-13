#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define virtual environment name (based on project name)
VENV_NAME="arize-toolkit-venv"

# Make sure poetry is on PATH
if ! command -v poetry &> /dev/null; then
    echo "poetry is not installed. Installing poetry..."
    pip install --user poetry
    # Add poetry to PATH for the duration of this script
    export PATH=$PATH:~/.local/bin
elif [[ -d ~/.local/bin ]] && [[ ! "$PATH" == *"/.local/bin"* ]]; then
    # If ~/.local/bin exists but is not in PATH, add it
    echo "Adding ~/.local/bin to PATH for this session..."
    export PATH=$PATH:~/.local/bin
fi

# Configure poetry to create virtual environments in-project with a specific name
echo "Configuring poetry to use named virtual environment..."
poetry config virtualenvs.in-project true
poetry config virtualenvs.path "./.venv"
poetry config virtualenvs.prompt "$VENV_NAME"


# Install dependencies using poetry (including dev and integration groups)
echo "Installing dependencies using poetry..."
poetry install --with dev,integration


# Success message
echo "Environment setup complete!"

# Print instructions for activating the virtual environment
echo "To activate the virtual environment, run:"
echo "source .venv/bin/activate"
