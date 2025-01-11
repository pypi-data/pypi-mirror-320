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
apt-get install -y python3-pip python3-dev bluetooth bluez bluez-tools

# Configure bluetooth
echo "Configuring Bluetooth..."
if ! grep -q "input.service" /etc/systemd/system/bluetooth.service; then
    sed -i 's/ExecStart=.*/& --noplugin=input/g' /etc/systemd/system/bluetooth.service
fi

# Restart bluetooth service
systemctl restart bluetooth

# Install systemd service
echo "Installing systemd service..."
cp systemd/xbox-switch-bridge.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable xbox-switch-bridge
systemctl start xbox-switch-bridge

echo "Installation complete!"
echo "The bridge service is now running and will start automatically on boot."
echo "Check status with: sudo systemctl status xbox-switch-bridge"