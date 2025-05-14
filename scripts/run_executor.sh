#!/bin/bash

show_help() {
    echo "Usage: sh scripts/run_executor.sh [ --path <filepath> ] | [ --development | --staging | --production ] | [ --help ]"
    echo ""
    echo "--development    Run the server on localhost using .env.development"
    echo "--staging        Run the server on staging IP using .env.staging"
    echo "--production     Run the server on production IP using .env.production"
    echo "--path           Run the executor with full path"
    echo "--help           Show this help message"
    echo ""
    echo "Example:"
    echo "  sh scripts/run_executor.sh --path /home/dfactory/Project/DiVA-streamlit-be/services/custom_model/siglip.py --development"
}

PROJECT_DIR="/home/$USER/Project/DiVA-streamlit-be"
ENV_FILE=""

case "$3" in
  --development)
    echo "Using development environment configuration"
    ENV_FILE="env/.env.development"
    ;;
  --staging)
    echo "Using staging environment configuration"
    ENV_FILE="env/.env.staging"
    ;;
  --production)
    echo "Using production environment configuration"
    ENV_FILE="env/.env.production"
    ;;
  --help)
    show_help
    exit 0
    ;;
  *)
    echo "Error: Invalid or missing environment option: '$3'"
    echo "Expected one of: --development | --staging | --production"
    show_help
    exit 1
    ;;
esac

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

# Load environment variables
if [ -f "$ENV_FILE" ]; then
    echo "Loading environment variables from $ENV_FILE"
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    echo "Error: Env file not found: $ENV_FILE"
    exit 1
fi

# Run the target script
echo "Running script: $TARGET_SCRIPT"
python3 "$TARGET_SCRIPT"

if [ $? -ne 0 ]; then
    echo "Error: Failed to run executor.py"
    exit 1
fi
