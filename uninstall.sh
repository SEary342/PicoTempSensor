#!/bin/bash

# --- Configuration ---
SERVICE_NAME="PicoTempSensor.service"
QUADLET_FILE="$HOME/.config/containers/systemd/PicoTempSensor.container"
IMAGE_NAME="picotempsensor"

echo "🗑️  Starting uninstallation of PicoTempSensor..."

# 1. Detect the port currently in use (to clean up firewall)
if [ -f "$QUADLET_FILE" ]; then
    CURRENT_PORT=$(grep "PublishPort=" "$QUADLET_FILE" | cut -d'=' -f2 | cut -d':' -f1)
    echo "🔍 Detected active port: ${CURRENT_PORT:-unknown}"
else
    echo "⚠️  Quadlet file not found. Skipping port detection."
fi

# 2. Stop and Disable the Systemd Service
echo "🛑 Stopping and disabling service..."
systemctl --user stop "$SERVICE_NAME" 2>/dev/null
systemctl --user disable "$SERVICE_NAME" 2>/dev/null

# 3. Remove the Quadlet file
if [ -f "$QUADLET_FILE" ]; then
    echo "📄 Removing Quadlet definition..."
    rm "$QUADLET_FILE"
    systemctl --user daemon-reload
fi

# 4. Remove the Podman Image
echo "📦 Removing Podman image..."
podman rmi "$IMAGE_NAME:latest" 2>/dev/null

# 5. Clean up Fedora Firewall
if [[ -n "$CURRENT_PORT" ]] && command -v firewall-cmd &> /dev/null; then
    echo "🛡️  Closing port $CURRENT_PORT in firewalld..."
    sudo firewall-cmd --permanent --remove-port="$CURRENT_PORT/tcp" 2>/dev/null
    sudo firewall-cmd --reload
fi

# 6. Optional: Disable Linger
# We keep this as a prompt since you might have other services running
read -p "❓ Do you want to disable user linger? (y/N): " disable_linger
if [[ "$disable_linger" =~ ^[Yy]$ ]]; then
    sudo loginctl disable-linger $(whoami)
fi

echo "✅ PicoTempSensor has been completely removed."