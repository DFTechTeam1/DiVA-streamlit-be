#!/bin/bash

sh scripts/requirements.sh

# Change virtualenv dir location into root project dir and install dependencies
echo "Configuring virtual environment and installing dependencies..."
uv sync

echo "Setup complete."
