#!/bin/bash

# Exit on error
set -e

echo "Installing Xbox Switch Bridge..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

# Install system dependencies
apt-get update
apt-get install -y python3.9 python3.9-dev python3.9-venv python3-pip bluetooth bluez bluez-tools \
    build-essential libdbus-1-dev libgirepository1.0-dev

# Create a virtual environment with Python 3.9
python3.9 -m venv /opt/xbox-switch-bridge
source /opt/xbox-switch-bridge/bin/activate

# Upgrade pip in the virtual environment
pip install --upgrade pip

# Install the package and its dependencies
pip install -r requirements.txt
pip install .

# Create wrapper script
cat > /usr/local/bin/xbox-switch-bridge << 'EOF'
#!/bin/bash
source /opt/xbox-switch-bridge/bin/activate
exec python3.9 -m xboxswitchbridge.cli "$@"
EOF

chmod +x /usr/local/bin/xbox-switch-bridge

# Configure bluetooth
echo "Configuring Bluetooth..."
if ! grep -q "input.service" /etc/systemd/system/bluetooth.service; then
    sed -i 's/ExecStart=.*/& --noplugin=input/g' /etc/systemd/system/bluetooth.service
fi

# Restart bluetooth service
systemctl restart bluetooth

# Install systemd service
echo "Installing systemd service..."
cp data/systemd/xbox-switch-bridge.service /etc/systemd/system/

systemctl daemon-reload
systemctl enable xbox-switch-bridge
systemctl start xbox-switch-bridge

echo "Installation complete!"
echo "The bridge service is now running and will start automatically on boot."
echo "Check status with: sudo systemctl status xbox-switch-bridge"