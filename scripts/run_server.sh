#!/bin/sh

# Show usage information
show_help() {
  echo "Usage: sh scripts/run_server.sh [ --development | --staging | --production ] | [ --help ]"
  echo ""
  echo "--development    Run the server on localhost and load the .env.development file"
  echo "--staging        Run the server on the staging IP and load the .env.staging file"
  echo "--production     Run the server on the production IP address and load the .env.production file"
  echo "--help           Show this help message"
}

# Ensure argument is provided
if [ -z "$1" ]; then
  echo "Error: No environment specified. Please provide one of --development, --staging, or --production."
  show_help
  exit 1
fi

ENV_FILE=""
DEFAULT_PORT="14000"

# Parse arguments
case "$1" in
  --development)
    echo "Using development environment configuration"
    export ENV_FILE="env/.env.development"
    RELOAD_FLAG="--reload --reload-dir=src"
    ;;
  --staging)
    echo "Using staging environment configuration"
    export ENV_FILE="env/.env.staging"
    RELOAD_FLAG=""
    ;;
  --production)
    echo "Using production environment configuration"
    export ENV_FILE="env/.env.production"
    RELOAD_FLAG=""
    ;;
  --help)
    show_help
    exit 0
    ;;
  *)
    echo "Invalid option: $1"
    show_help
    exit 1
    ;;
esac

# Load the environment variables
export $(grep -v '^#' $ENV_FILE | xargs)

# Set HOST from IP_HOST in .env file (default to 127.0.0.1)
HOST=${IP_HOST:-"127.0.0.1"}

# Check if APPLICATION_PORT is set, otherwise use DEFAULT_PORT and log a message
if [ -z "$APPLICATION_PORT" ]; then
  echo "Warning: APPLICATION_PORT not provided in $ENV_FILE. Using default port $DEFAULT_PORT."
  APPLICATION_PORT=$DEFAULT_PORT
fi

# Checking OS Environment
echo "Checking OS Environment"
if grep -qEi "(Microsoft|WSL)" /proc/version &>/dev/null; then
  echo "WSL detected"
  . .venv/bin/activate
else
  case "$OSTYPE" in
    linux*)
      echo "Linux based OS detected"
      source .venv/bin/activate
      ;;
    darwin*)
      echo "macOS detected"
      source .venv/bin/activate
      ;;
    cygwin* | msys* | mingw*)
      echo "Windows based OS detected"
      source .venv/Scripts/activate
      ;;
    *)
      echo "Unsupported OS."
      exit 1
      ;;
  esac
fi

# Start the server with the resolved host and port
echo "Running uvicorn server on $HOST:$APPLICATION_PORT"
uvicorn src.main:app --host "$HOST" --port "$APPLICATION_PORT" $RELOAD_FLAG
