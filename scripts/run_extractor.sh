#!/bin/bash

show_help() {
    echo "Usage: sh scripts/run_extractor.sh"
    echo ""
    echo "Options:"
    echo "  --help  Show this help message"
}

if [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

PROJECT_DIR="/home/dfactory/Project/DiVA-streamlit-be"

# Checking OS Environment
echo "Checking OS Environment."
if grep -qEi "(Microsoft|WSL)" /proc/version &>/dev/null; then
  echo "WSL detected."
  . "$PROJECT_DIR/.venv/bin/activate"
else
  case "$OSTYPE" in
    linux*)
      echo "Linux based OS detected."
      source
      ;;
    darwin*)
      echo "macOS detected."
      source "$PROJECT_DIR/.venv/bin/activate"
      ;;
    *)
      echo "Unsupported OS."
      exit 1
      ;;
  esac
fi
echo "Virtual environment activated."

echo "Running NAS extractor."
python3 $PROJECT_DIR/services/nas/executor.py

if [ $? -ne 0 ]; then
    echo "Error: Failed to run executor.py"
    exit 1
fi
