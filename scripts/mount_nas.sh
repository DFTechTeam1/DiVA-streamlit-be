#!/bin/sh

# Show usage information
show_help() {
  echo "Usage: sh scripts/mount_nas.sh [ --<NAS_IP> ]"
  echo ""
  echo "Example: sh scripts/mount_nas.sh --192.168.100.105"
  echo ""
}

MOUNT_DIR="mount"
ENV_FILE="env/.env.development"

# Ensure an argument is provided
if [ -z "$1" ]; then
  echo "Error: Missing NAS IP parameter."
  show_help
  exit 1
fi

# Extract the NAS IP from the argument
if echo "$1" | grep -Eq "^--[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$"; then
  NAS_IP="${1#--}"  # Remove '--' prefix to get IP
else
  echo "Invalid NAS IP format: $1"
  show_help
  exit 1
fi

# Check if the environment file exists
if [ ! -f "$ENV_FILE" ]; then
  echo "Error: Environment file $ENV_FILE not found."
  echo "Please ensure the file exists and contains NAS credentials."
  exit 1
fi

# Load environment variables
export $(grep -v '^#' "$ENV_FILE" | xargs)

# Ensure required variables are set
if [ -z "$NAS_USERNAME" ] || [ -z "$NAS_PASSWORD" ]; then
  echo "Error: NAS_USERNAME or NAS_PASSWORD is not set in $ENV_FILE."
  exit 1
fi

# Define the JSON directory path
JSON_DIR="temp/$NAS_IP"

# Check if the JSON directory exists
if [ ! -d "$JSON_DIR" ]; then
  echo "Error: No extracted data found for $NAS_IP."
  echo "Please run the extraction script first: sh scripts/run_extractor.sh --$NAS_IP"
  exit 1
fi

# Find the latest JSON file in the directory
LATEST_JSON=$(ls -t "$JSON_DIR"/*.json 2>/dev/null | head -n 1)

if [ -z "$LATEST_JSON" ]; then
  echo "Error: No JSON file found in $JSON_DIR."
  echo "Please run the extraction script first."
  exit 1
fi

echo "Using latest JSON file: $LATEST_JSON"

# Read the JSON file and extract the paths
NAS_PATHS=$(jq -r '.paths[]' "$LATEST_JSON")

if [ -z "$NAS_PATHS" ]; then
  echo "Error: No paths found in $LATEST_JSON."
  exit 1
fi

# Create a directory inside /mount for the NAS IP
MOUNT_IP_DIR="$MOUNT_DIR/$NAS_IP"
mkdir -p "$MOUNT_IP_DIR"

# Mount each shared folder
for NAS_PATH in $NAS_PATHS; do
  SHARE_NAME=$(basename "$NAS_PATH")  # Extract last part of path
  MOUNT_PATH="$MOUNT_IP_DIR/$SHARE_NAME"

  # Create directory for mounting
  mkdir -p "$MOUNT_PATH"

  echo "Mounting $NAS_PATH to $MOUNT_PATH..."

  sudo mount -t cifs "$NAS_PATH" "$MOUNT_PATH" -o username="$NAS_USERNAME",password="$NAS_PASSWORD",vers=3.0

  # Verify if the mount was successful
  if mountpoint -q "$MOUNT_PATH"; then
    echo "Mounted successfully: $NAS_PATH -> $MOUNT_PATH"
  else
    echo "Error: Failed to mount $NAS_PATH"
  fi
done

echo "All NAS folders mounted under $MOUNT_IP_DIR."
