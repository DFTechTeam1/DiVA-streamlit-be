#!/bin/sh

# Show usage information
show_help() {
  echo "Usage: sh scripts/run_server.sh --env <environment> [ --port <number> ]"
  echo ""
  echo "--env            Set environment: development | staging | production"
  echo "--port           (Optional) Override default port (default: APPLICATION_PORT from .env)"
  echo "--help, -h       Show this help message"
}

# Default values
ENV=""
ENV_FILE=""
RELOAD_FLAG=""
PORT=""
CUSTOM_PORT=""

# Parse arguments
while [ $# -gt 0 ]; do
  case "$1" in
    --env)
      shift
      ENV="$1"
      case "$ENV" in
        development)
          echo "Using development environment configuration"
          ENV_FILE="env/.env.development"
          RELOAD_FLAG="--reload --reload-dir=src"
          ;;
        staging)
          echo "Using staging environment configuration"
          ENV_FILE="env/.env.staging"
          ;;
        production)
          echo "Using production environment configuration"
          ENV_FILE="env/.env.production"
          ;;
        *)
          echo "Error: Invalid environment '$ENV'"
          show_help
          exit 1
          ;;
      esac
      ;;
    --port)
      shift
      if echo "$1" | grep -qE '^[0-9]+$'; then
        CUSTOM_PORT="$1"
      else
        echo "Error: Invalid port number '$1'. Must be numeric."
        show_help
        exit 1
      fi
      ;;
    --help|-h)
      show_help
      exit 0
      ;;
    *)
      echo "Error: Unknown argument: $1"
      show_help
      exit 1
      ;;
  esac
  shift
done

# Validate env was provided
if [ -z "$ENV_FILE" ]; then
  echo "Error: Missing --env argument"
  show_help
  exit 1
fi

# Load environment variables
export $(grep -v '^#' "$ENV_FILE" | xargs)

# Set HOST from IP_HOST in .env file (default to 127.0.0.1)
HOST=${IP_HOST:-"127.0.0.1"}

# Set PORT from environment or override
if [ -n "$CUSTOM_PORT" ]; then
  PORT="$CUSTOM_PORT"
else
  if [ -z "$APPLICATION_PORT" ]; then
    echo "Error: APPLICATION_PORT not set in $ENV_FILE"
    exit 1
  fi
  PORT="$APPLICATION_PORT"
fi

# Checking OS Environment
echo "Checking OS Environment"
if grep -qEi "(Microsoft|WSL)" /proc/version &>/dev/null; then
  echo "WSL detected"
  . .venv/bin/activate
else
  case "$OSTYPE" in
    linux*|darwin*)
      echo "Unix-based OS detected"
      source .venv/bin/activate
      ;;
    cygwin*|msys*|mingw*)
      echo "Windows-based OS detected"
      source .venv/Scripts/activate
      ;;
    *)
      echo "Unsupported OS."
      exit 1
      ;;
  esac
fi

# Start the server
echo "Running uvicorn server on $HOST:$PORT"
uvicorn src.main:app --host "$HOST" --port "$PORT" $RELOAD_FLAG
