#!/bin/sh

show_help() {
  echo "Usage: sh scripts/run_test [ --development | --staging | --production ] [--unit_test | --api_test | --e2e | --help ]"
  echo ""
  echo "Environment Options:"
  echo "  --development    Set the environment to development."
  echo "  --staging        Set the environment to staging."
  echo "  --production     Set the environment to production."
  echo ""
  echo "Test Options:"
  echo "  --unit_test      Run unit tests located in tests/unit_test."
  echo "  --api_test       Run API tests located in tests/api_test."
  echo "  --e2e            Run end-to-end tests located in tests/e2e."
  echo ""
  echo "--help             Show this help message."
}

# Default values for environment and test type
ENV_FILE=""
TEST_DIR=""

# Parse arguments
while [ $# -gt 0 ]; do
  case "$1" in
    --development)
      ENV_FILE="env/.env.development"
      ;;
    --staging)
      ENV_FILE="env/.env.staging"
      ;;
    --production)
      ENV_FILE="env/.env.production"
      ;;
    --unit_test)
      TEST_DIR="tests/unit_test"
      ;;
    --api_test)
      TEST_DIR="tests/api_test"
      ;;
    --e2e)
      TEST_DIR="tests/e2e"
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
  shift
done

# Validate inputs
if [ -z "$ENV_FILE" ]; then
  echo "Error: No environment specified. Please provide one of --development, --staging or --production."
  show_help
  exit 1
fi

if [ -z "$TEST_DIR" ]; then
  echo "Error: No test type specified. Please provide one of --unit_test, --api_test or --e2e."
  show_help
  exit 1
fi

# Export the environment file for Python
export $(grep -v '^#' $ENV_FILE | xargs)

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

# Run the tests
echo "Running tests in $TEST_DIR on $ENV_FILE environment"
if ! coverage run -m --source=$TEST_DIR pytest $TEST_DIR; then
  echo "Tests failed!"
  exit 1
fi

# Generate the coverage report
echo "Generating coverage report"
coverage report -m --skip-empty
coverage html

echo "Test finished"
