# Xbox Switch Bridge

Use your Xbox controller with Nintendo Switch via Raspberry Pi.

## Requirements

- Raspberry Pi (tested on Pi 4 and Pi 3B+)
- Bluetooth capability
- Python 3.7+
- Root access for Bluetooth operations
- Xbox Controller (tested with Xbox Series X/S controllers)
- Nintendo Switch

## System Dependencies

Before installing, make sure you have the required system packages:

```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev bluetooth bluez bluez-tools
```

## Installation

1. Install the package:
```bash
pip install xbox-switch-bridge
```

2. Run the post-installation setup:
```bash
sudo xbox-switch-bridge --install
```

This will:
- Configure Bluetooth settings
- Install and enable the systemd service
- Set up required permissions

## Usage

### As a Service
Once installed, the bridge will start automatically on boot. You can manage it with:

```bash
sudo systemctl start xbox-switch-bridge   # Start the service
sudo systemctl stop xbox-switch-bridge    # Stop the service
sudo systemctl status xbox-switch-bridge  # Check status
```

### Manual Usage
Run directly (requires root):

```bash
sudo xbox-switch-bridge --run
```

## Troubleshooting

1. Check the logs:
```bash
sudo journalctl -u xbox-switch-bridge
```

2. Verify Bluetooth:
```bash
sudo systemctl status bluetooth
bluetoothctl show
```

3. Common issues:
- Controller not detected: Ensure it's in pairing mode
- Switch not connecting: Open the "Change Grip/Order" menu
- Permission errors: Make sure you're running as root

## Uninstallation

```bash
sudo xbox-switch-bridge --uninstall
pip uninstall xbox-switch-bridge
```

## License

MIT