#!/bin/bash
# CloudPort Jellyfin Auto-Configuration Script
# Runs once on first deployment to pre-configure Jellyfin


# Exit immediately if any command fails, in order to prevent a broken Jellyfin install
set -e

JELLYFIN_URL="http://localhost:8096"
CONFIG_DIR="/config"

echo "Waiting for Jellyfin to start..."
# Wait until Jellyfin is responding before attempting configuration
# This loops frequently checks Jellyfin's health endpoint every 5 seconds, until it responds
until curl -sf "$JELLYFIN_URL/health" > /dev/null; do
    echo "Jellyfin not ready yet, retrying in 5 seconds..."
    sleep 5
done
echo "Jellyfin is up"

echo "Checking if Jellyfin is already configured..."
# Check if admin user already exists, setup is skipped if it does
#Checks if a hidden file called [.cloudport_configured] exists in config directory,
#If it does, Jellyfin has already been set up and exits immediately, preventing the script from being overwritten
if [ -f "$CONFIG_DIR/.cloudport_configured" ]; then
    echo "Jellyfin already configured, skipping setup"
    exit 0
fi

echo "Configuring Jellyfin admin account..."
# Create the initial admin account using Jellyfin's startup API,
# this endpoint is only available before the wizard is completed
# It will be set during the cloudport setup wizard, so the user never touches this script directly
curl -sf -X POST "$JELLYFIN_URL/Startup/User" \
    -H "Content-Type: application/json" \
    -d "{
        \"Name\": \"$JELLYFIN_ADMIN_USERNAME\",
        \"Password\": \"$JELLYFIN_ADMIN_PASSWORD\"
    }"

echo "Setting up media library directories..."
# Creates 3 default media library folders, [Movies, TV shows and Music],
# each points to a folder inside the container, maps to actual storage on the VM via Docker volumes
# when a user adds media files they appear in Jellyfin automatically
curl -sf -X POST "$JELLYFIN_URL/Library/VirtualFolders" \
    -H "Content-Type: application/json" \
    -d "{
        \"Name\": \"Movies\",
        \"CollectionType\": \"movies\",
        \"Paths\": [\"/media/movies\"],
        \"RefreshLibrary\": false
    }"

curl -sf -X POST "$JELLYFIN_URL/Library/VirtualFolders" \
    -H "Content-Type: application/json" \
    -d "{
        \"Name\": \"TV Shows\",
        \"CollectionType\": \"tvshows\",
        \"Paths\": [\"/media/tvshows\"],
        \"RefreshLibrary\": false
    }"

curl -sf -X POST "$JELLYFIN_URL/Library/VirtualFolders" \
    -H "Content-Type: application/json" \
    -d "{
        \"Name\": \"Music\",
        \"CollectionType\": \"music\",
        \"Paths\": [\"/media/music\"],
        \"RefreshLibrary\": false
    }"

# Mark Jellyfin as configured so this script doesn't run again
touch "$CONFIG_DIR/.cloudport_configured"
echo "Jellyfin configuration complete"
