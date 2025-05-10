#!/bin/sh

# Show usage information
show_help() {
  echo "Usage: sh scripts/run_server.sh [ --development | --staging | --production ] [ --port <number> ]"
  echo ""
  echo "--development    Run the server on localhost using .env.development"
  echo "--staging        Run the server on staging IP using .env.staging"
  echo "--production     Run the server on production IP using .env.production"
  echo "--port           (Optional) Override default port (default: 14000)"
  echo "--help           Show this help message"
}

# Default values
ENV_FILE=""
RELOAD_FLAG=""
PORT="14000"

# Parse first argument (environment)
case "$1" in
  --development)
    echo "Using development environment configuration"
    ENV_FILE="env/.env.development"
    RELOAD_FLAG="--reload --reload-dir=src"
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
    echo "Error: Invalid or missing environment option: $1"
    show_help
    exit 1
    ;;
esac

# Parse optional second argument for port
# Check if second arg is --port
if [ "$2" = "--port" ]; then
  # Validate port is numeric and non-empty
  if echo "$3" | grep -qE '^[0-9]+$'; then
    PORT="$3"
  else
    echo "Error: Invalid port number '$3'. Must be numeric."
    show_help
    exit 1
  fi
elif [ -n "$2" ]; then
  echo "Error: Invalid argument: $2"
  show_help
  exit 1
fi

# Load the environment variables
export $(grep -v '^#' $ENV_FILE | xargs)

# Set HOST from IP_HOST in .env file (default to 127.0.0.1)
HOST=${IP_HOST:-"127.0.0.1"}


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
echo "Running uvicorn server on $HOST:$PORT"
uvicorn src.main:app --host "$HOST" --port "$PORT" $RELOAD_FLAG
