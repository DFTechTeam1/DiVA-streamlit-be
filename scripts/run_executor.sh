#!/bin/bash

show_help() {
    echo "Usage: sh scripts/run_executor.sh [ --path <filepath> ] | [ --env <environment> ] | [ --help ]"
    echo ""
    echo "--path        Run the executor with full path (required)"
    echo "--env         Set environment: development | staging | production (default: development)"
    echo "--help, -h    Show this help message"
    echo ""
    echo "Example: sh scripts/run_executor.sh --path /path/to/script.py"
}

# Default values
PROJECT_DIR="$HOME/Project/DiVA-streamlit-be"
ENV_NAME="development"
TARGET_SCRIPT=""

# Parse arguments
while [ "$#" -gt 0 ]; do
    case "$1" in
        --help|-h)
            show_help
            exit 0
            ;;
        --path)
            TARGET_SCRIPT="$2"
            shift 2
            ;;
        --env)
            ENV_NAME="$2"
            shift 2
            ;;
        *)
            echo "Error: Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate target script
if [ -z "$TARGET_SCRIPT" ]; then
    echo "Error: --path is required."
    show_help
    exit 1
fi

if [ ! -f "$TARGET_SCRIPT" ]; then
    echo "Error: The specified file does not exist: $TARGET_SCRIPT"
    exit 1
fi

# Determine env file
case "$ENV_NAME" in
    development)
        echo "Using development environment configuration"
        ENV_FILE="$PROJECT_DIR/env/.env.development"
        ;;
    staging)
        echo "Using staging environment configuration"
        ENV_FILE="$PROJECT_DIR/env/.env.staging"
        ;;
    production)
        echo "Using production environment configuration"
        ENV_FILE="$PROJECT_DIR/env/.env.production"
        ;;
    *)
        echo "Error: Invalid environment: '$ENV_NAME'"
        echo "Expected one of: development | staging | production"
        exit 1
        ;;
esac

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

# Load env vars
if [ -f "$ENV_FILE" ]; then
    echo "Loading environment variables from $ENV_FILE"
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    echo "Error: Env file not found: $ENV_FILE"
    exit 1
fi

# Run the script
echo "Running script: $TARGET_SCRIPT"
python3 "$TARGET_SCRIPT"

if [ $? -ne 0 ]; then
    echo "Error: Script failed: $TARGET_SCRIPT"
    exit 1
fi
