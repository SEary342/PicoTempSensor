#!/bin/bash

# --- Configuration ---
REPO_ROOT=$(pwd)
QUADLET_DIR="$HOME/.config/containers/systemd"
# Get port from first argument or default to 5000
PORT=${1:-5000}

echo "🚀 Installing PicoTempSensor on Port: $PORT"

# 1. Build the Podman image
podman build -t picotempsensor:latest -f Containerfile .

# 2. Setup Quadlet directory
mkdir -p "$QUADLET_DIR"

# 3. Create the Quadlet file dynamically with the chosen port
cat <<EOF > "$QUADLET_DIR/PicoTempSensor.container"
[Unit]
Description=PicoTempSensor Podman Container
After=network-online.target

[Container]
Image=picotempsensor:latest
# HostPort:ContainerPort
PublishPort=$PORT:5000
UserNS=keep-id

[Service]
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 4. Reload and Start
echo "⚙️  Reloading systemd and starting service..."
systemctl --user daemon-reload
systemctl --user enable --now PicoTempSensor.service

# 5. Fedora Firewall (Firewalld)
if command -v firewall-cmd &> /dev/null; then
    echo "🛡️  Opening port $PORT in firewalld..."
    sudo firewall-cmd --permanent --add-port=$PORT/tcp
    sudo firewall-cmd --reload
fi

# 6. Persistence
sudo loginctl enable-linger $(whoami)

echo "✅ PicoTempSensor is live!"
echo "📊 Dashboard: http://$(hostname -I | awk '{print $1}'):$PORT"
echo "📜 View Logs: journalctl --user -u PicoTempSensor -f"