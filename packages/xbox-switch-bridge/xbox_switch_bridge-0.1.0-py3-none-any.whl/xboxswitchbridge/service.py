import os
import subprocess
import logging
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)

SYSTEMD_SERVICE_PATH = "/etc/systemd/system/xbox-switch-bridge.service"
SERVICE_CONTENT = """[Unit]
Description=Xbox to Nintendo Switch Controller Bridge
After=bluetooth.service
Wants=bluetooth.service

[Service]
Type=simple
User=root
Group=root
ExecStart=/usr/local/bin/xbox-switch-bridge
Restart=on-failure
RestartSec=5
StandardOutput=append:/var/log/xbox-switch-bridge.log
StandardError=append:/var/log/xbox-switch-bridge.log

[Install]
WantedBy=multi-user.target
"""

def configure_bluetooth():
    """Konfiguriert Bluetooth für die Bridge"""
    try:
        # Bluetooth Input Plugin deaktivieren
        service_file = "/etc/systemd/system/bluetooth.service"
        if os.path.exists(service_file):
            with open(service_file, 'r') as f:
                content = f.read()

            if "input.service" not in content:
                content = content.replace(
                    'ExecStart=',
                    'ExecStart= --noplugin=input'
                )

                with open(service_file, 'w') as f:
                    f.write(content)

                subprocess.run(['systemctl', 'daemon-reload'])
                subprocess.run(['systemctl', 'restart', 'bluetooth'])
                logger.info("Bluetooth erfolgreich konfiguriert")
            else:
                logger.info("Bluetooth bereits konfiguriert")
    except Exception as e:
        logger.error(f"Fehler bei Bluetooth-Konfiguration: {e}")
        raise

def create_service_file():
    """Erstellt die Systemd Service Datei"""
    try:
        with open(SYSTEMD_SERVICE_PATH, 'w') as f:
            f.write(SERVICE_CONTENT)
        logger.info("Service-Datei erstellt")
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Service-Datei: {e}")
        raise

def install_service():
    """Installiert und aktiviert den Service"""
    try:
        configure_bluetooth()
        create_service_file()

        # Log-Datei erstellen
        Path("/var/log/xbox-switch-bridge.log").touch(mode=0o644, exist_ok=True)

        # Service aktivieren und starten
        subprocess.run(['systemctl', 'daemon-reload'])
        subprocess.run(['systemctl', 'enable', 'xbox-switch-bridge'])
        subprocess.run(['systemctl', 'start', 'xbox-switch-bridge'])

        logger.info("Service erfolgreich installiert und gestartet")
    except Exception as e:
        logger.error(f"Installation fehlgeschlagen: {e}")
        raise

def uninstall_service():
    """Deinstalliert den Service"""
    try:
        # Service stoppen und deaktivieren
        subprocess.run(['systemctl', 'stop', 'xbox-switch-bridge'])
        subprocess.run(['systemctl', 'disable', 'xbox-switch-bridge'])

        # Service-Datei entfernen
        if os.path.exists(SYSTEMD_SERVICE_PATH):
            os.remove(SYSTEMD_SERVICE_PATH)

        # Log-Datei entfernen
        if os.path.exists("/var/log/xbox-switch-bridge.log"):
            os.remove("/var/log/xbox-switch-bridge.log")

        subprocess.run(['systemctl', 'daemon-reload'])

        logger.info("Service erfolgreich deinstalliert")
    except Exception as e:
        logger.error(f"Deinstallation fehlgeschlagen: {e}")
        raise

def check_service_status():
    """Prüft den Status des Services"""
    try:
        subprocess.run(['systemctl', 'status', 'xbox-switch-bridge'])
    except subprocess.CalledProcessError as e:
        # Status command returns non-zero exit code if service is not running
        logger.error("Service läuft nicht")
        return False
    return True