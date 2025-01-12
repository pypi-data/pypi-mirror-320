import os
import subprocess
import logging
from pathlib import Path
import shutil
import pkg_resources

logger = logging.getLogger(__name__)

SYSTEMD_SERVICE_PATH = "/etc/systemd/system/xbox-switch-bridge.service"

def get_service_content():
    """Liest den Service-Content aus der data/systemd/ Datei"""
    try:
        service_path = pkg_resources.resource_filename('xboxswitchbridge', 'data/systemd/xbox-switch-bridge.service')
        with open(service_path, 'r') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Fehler beim Lesen der Service-Datei: {e}")
        raise

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
        service_content = get_service_content()
        with open(SYSTEMD_SERVICE_PATH, 'w') as f:
            f.write(service_content)
        logger.info("Service-Datei erstellt")
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Service-Datei: {e}")
        raise

def install_xpadneo():
    """Installiert den xpadneo Treiber wenn nicht vorhanden"""
    try:
        # Prüfen ob xpadneo bereits installiert ist
        result = subprocess.run(['dkms', 'status'], capture_output=True, text=True)
        if 'xpadneo' in result.stdout:
            logger.info("xpadneo ist bereits installiert")
            return True

        logger.info("Installiere xpadneo Treiber...")

        # Temporäres Verzeichnis erstellen
        with tempfile.TemporaryDirectory() as temp_dir:
            # xpadneo klonen
            subprocess.run([
                'git', 'clone',
                'https://github.com/atar-axis/xpadneo.git',
                temp_dir
            ], check=True)

            # Installation ausführen
            subprocess.run(
                ['sudo', './install.sh'],
                cwd=temp_dir,
                check=True
            )

        logger.info("xpadneo Treiber erfolgreich installiert")
        logger.warning("Ein Systemneustart wird empfohlen!")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Fehler bei xpadneo Installation: {e}")
        return False

def install_service():
    """Installiert und aktiviert den Service"""
    try:
        # Systemabhängigkeiten prüfen/installieren
        subprocess.run([
            'apt-get', 'install', '-y',
            'raspberrypi-kernel-headers',
            'dkms',
            'git'
        ], check=True)

        # xpadneo installieren
        if not install_xpadneo():
            logger.error("xpadneo Installation fehlgeschlagen")
            return False

        configure_bluetooth()
        create_service_file()

        # Log-Datei erstellen
        Path("/var/log/xbox-switch-bridge.log").touch(mode=0o644, exist_ok=True)

        # Service aktivieren und starten
        subprocess.run(['systemctl', 'daemon-reload'])
        subprocess.run(['systemctl', 'enable', 'xbox-switch-bridge'])
        subprocess.run(['systemctl', 'start', 'xbox-switch-bridge'])

        logger.info("Service erfolgreich installiert und gestartet")

        # Neustart empfehlen wenn xpadneo neu installiert wurde
        logger.info("Installation abgeschlossen! Ein Systemneustart wird empfohlen.")
        return True

    except Exception as e:
        logger.error(f"Installation fehlgeschlagen: {e}")
        return False

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