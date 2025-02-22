#!/bin/sh

# Show usage information
show_help() {
  echo "Usage: sh scripts/umount_nas.sh [ --<NAS_IP> ]"
  echo ""
  echo "Example: sh scripts/umount_nas.sh --192.168.100.105"
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
  exit 1
fi

# Load environment variables
export $(grep -v '^#' "$ENV_FILE" | xargs)

# Ensure required variables are set
if [ -z "$NAS_USERNAME" ] || [ -z "$NAS_PASSWORD" ]; then
  echo "Error: NAS_USERNAME or NAS_PASSWORD is not set in $ENV_FILE."
  exit 1
fi

# Define the mounted directory path
MOUNT_IP_DIR="$MOUNT_DIR/$NAS_IP"

# Check if the mount directory exists
if [ ! -d "$MOUNT_IP_DIR" ]; then
  echo "Error: No mounted directories found for NAS IP $NAS_IP."
  exit 1
fi

echo "Unmounting NAS shares from $MOUNT_IP_DIR..."

# Unmount each mounted folder inside the NAS IP directory
for MOUNT_PATH in "$MOUNT_IP_DIR"/*; do
  if mountpoint -q "$MOUNT_PATH"; then
    echo "Unmounting $MOUNT_PATH..."
    sudo umount "$MOUNT_PATH"

    # Verify if unmount was successful
    if mountpoint -q "$MOUNT_PATH"; then
      echo "Error: Failed to unmount $MOUNT_PATH"
    else
      echo "Unmounted successfully: $MOUNT_PATH"
    fi
  else
    echo "Skipping $MOUNT_PATH (not a mount point)"
  fi
done

# Remove the NAS IP directory if all mounts were successfully unmounted
# if ! mountpoint -q "$MOUNT_IP_DIR"; then
#   echo "Removing empty directory: $MOUNT_IP_DIR"
#   rmdir "$MOUNT_IP_DIR"
# fi

echo "All NAS shares unmounted for IP $NAS_IP."
