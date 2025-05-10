#!/bin/bash

show_help() {
    echo "Usage: sh scripts/run_executor.sh [ --fullpath ] | [ --help ]"
    echo ""
    echo "--help  Show this help message"
    echo "--fullpath  Run the executor with full path"
    echo ""
    echo "Example: sh scripts/run_executor.sh /home/dfactory/Project/DiVA-streamlit-be/services/custom_model/siglip.py"
}

TARGET_SCRIPT="$1"
PROJECT_DIR="/home/$USER/Project/DiVA-streamlit-be"

if [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

if [ ! -f "$TARGET_SCRIPT" ]; then
    echo "Error: The specified file does not exist: $TARGET_SCRIPT"
    exit 1
fi


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

echo "Running script: $TARGET_SCRIPT."
python3 $TARGET_SCRIPT

if [ $? -ne 0 ]; then
    echo "Error: Failed to run executor.py"
    exit 1
fi
