#!/bin/bash

show_help() {
    echo "Usage: sh scripts/run_executor.sh [ --path <filepath> ] | [ --help ]"
    echo ""
    echo "--help        Show this help message"
    echo "--path        Run the executor with full path"
    echo ""
    echo "Example:"
    echo "  sh scripts/run_executor.sh --path /home/dfactory/Project/DiVA-streamlit-be/services/custom_model/siglip.py"
}

PROJECT_DIR="/home/$USER/Project/DiVA-streamlit-be"

# Parse arguments
if [ "$1" = "--help" ]; then
    show_help
    exit 0
elif [ "$1" = "--path" ] && [ -n "$2" ]; then
    TARGET_SCRIPT="$2"
else
    echo "Error: Invalid arguments."
    show_help
    exit 1
fi

# Validate file exists
if [ ! -f "$TARGET_SCRIPT" ]; then
    echo "Error: The specified file does not exist: $TARGET_SCRIPT"
    exit 1
fi

# Activate virtual environment based on OS
echo "Checking OS Environment."
if grep -qEi "(Microsoft|WSL)" /proc/version &>/dev/null; then
    echo "WSL detected."
    . "$PROJECT_DIR/.venv/bin/activate"
else
    case "$OSTYPE" in
        linux*|darwin*)
            echo "Unix-based OS detected."
            source "$PROJECT_DIR/.venv/bin/activate"
            ;;
        *)
            echo "Unsupported OS."
            exit 1
            ;;
    esac
fi
echo "Virtual environment activated."

# Run the target script
echo "Running script: $TARGET_SCRIPT"
python3 "$TARGET_SCRIPT"

if [ $? -ne 0 ]; then
    echo "Error: Failed to run executor.py"
    exit 1
fi
