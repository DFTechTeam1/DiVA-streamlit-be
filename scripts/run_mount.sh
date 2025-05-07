#!/bin/sh

# Show usage information
show_help() {
  echo "Usage: sh scripts/mount_nas.sh"
  echo ""
  echo "Example: sh scripts/mount_nas.sh"
  echo ""
}

MOUNT_DIR="mount"
ENV_FILE="env/.env.development"
TEMP_DIR="temp"

# Check if the environment file exists
if [ ! -f "$ENV_FILE" ]; then
  echo "Error: Environment file $ENV_FILE not found."
  exit 1
fi

# Load environment variables
export $(grep -v '^#' "$ENV_FILE" | xargs)

# Ensure required variables are set
if [ -z "$NAS_USERNAME" ] || [ -z "$NAS_PASSWORD" ]; then
  echo "Error: NAS_USERNAME or NAS_PASSWORD is not set in $ENV_FILE."
  exit 1
fi

# Check if temp directory exists and is not empty
if [ ! -d "$TEMP_DIR" ] || [ -z "$(find "$TEMP_DIR" -mindepth 1 -type d 2>/dev/null)" ]; then
  echo "Error: No NAS data found. Directory '$TEMP_DIR' is missing or empty."
  exit 1
fi

# Loop through all subdirectories in temp/
for DIR in "$TEMP_DIR"/*/; do
  [ -d "$DIR" ] || continue

  NAS_IP=$(basename "$DIR")
  JSON_DIR="$TEMP_DIR/$NAS_IP"

  echo "Processing NAS IP: $NAS_IP"

  # Find the latest JSON file in the directory
  LATEST_JSON=$(ls -t "$JSON_DIR"/*.json 2>/dev/null | head -n 1)

  if [ -z "$LATEST_JSON" ]; then
    echo "Warning: No JSON file found in $JSON_DIR. Skipping..."
    continue
  fi

  echo "Using latest JSON file: $LATEST_JSON"

  # Read the JSON file and extract the paths
  NAS_PATHS=$(jq -r '.paths[]' "$LATEST_JSON")

  if [ -z "$NAS_PATHS" ]; then
    echo "Warning: No paths found in $LATEST_JSON. Skipping..."
    continue
  fi

  # Create a directory inside /mount for the NAS IP
  MOUNT_IP_DIR="$MOUNT_DIR/$NAS_IP"
  mkdir -p "$MOUNT_IP_DIR"

  # Mount each shared folder
  for NAS_PATH in $NAS_PATHS; do
    SHARE_NAME=$(basename "$NAS_PATH")
    MOUNT_PATH="$MOUNT_IP_DIR/$SHARE_NAME"

    mkdir -p "$MOUNT_PATH"
    echo "Mounting $NAS_PATH to $MOUNT_PATH..."

    sudo mount -t cifs "$NAS_PATH" "$MOUNT_PATH" -o username="$NAS_USERNAME",password="$NAS_PASSWORD",vers=3.0

    if mountpoint -q "$MOUNT_PATH"; then
      echo "Mounted successfully: $NAS_PATH -> $MOUNT_PATH"
    else
      echo "Error: Failed to mount $NAS_PATH"
    fi
  done

  echo "Completed mounting for NAS IP: $NAS_IP"
  echo ""
done

echo "All NAS folders mounted successfully."
