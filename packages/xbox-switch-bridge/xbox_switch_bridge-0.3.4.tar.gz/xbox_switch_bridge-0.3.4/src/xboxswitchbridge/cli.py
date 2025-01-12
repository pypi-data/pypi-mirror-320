#!/usr/bin/env python3.9
import argparse
import sys
import os
import logging
from pathlib import Path
import subprocess
import shutil

from .bridge import XboxSwitchBridge
from .service import install_service, uninstall_service, check_service_status

def setup_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def check_python_version():
    """Überprüft ob Python 3.9 oder höher verwendet wird"""
    if sys.version_info < (3, 9):
        print("Dieses Programm benötigt Python 3.9 oder höher!")
        sys.exit(1)

def check_root():
    """Überprüft ob das Programm als root ausgeführt wird"""
    if os.geteuid() != 0:
        print("Dieses Programm muss mit sudo ausgeführt werden!")
        sys.exit(1)

def run_bridge():
    """Startet die Bridge direkt"""
    check_root()
    bridge = XboxSwitchBridge()
    try:
        import asyncio
        asyncio.run(bridge.run())
    except KeyboardInterrupt:
        print("\nBridge beendet.")

def check_dependencies():
    """Überprüft ob alle notwendigen System-Dependencies installiert sind"""
    import logging
    logger = logging.getLogger(__name__)

    # Liste der möglichen Binaries für jedes Paket
    package_binaries = {
        'bluetooth': ['bluetoothd', 'bluetooth'],
        'bluez': ['bluetoothctl', 'hciconfig'],
        'bluez-tools': ['bt-device', 'bt-adapter']
    }

    missing = []

    # Prüfe zuerst ob die Pakete via dpkg installiert sind
    for package in package_binaries.keys():
        try:
            result = subprocess.run(['dpkg', '-l', package],
                                 capture_output=True,
                                 text=True)
            if "ii" not in result.stdout:
                logger.debug(f"Paket {package} nicht in dpkg gefunden")
                missing.append(package)
                continue

            # Wenn Paket installiert ist, prüfe die zugehörigen Binaries
            found_binary = False
            for binary in package_binaries[package]:
                binary_path = shutil.which(binary)
                logger.debug(f"Suche nach Binary {binary}: {binary_path}")
                if binary_path:
                    found_binary = True
                    break

            if not found_binary:
                logger.warning(f"Paket {package} ist installiert, aber keine Binaries gefunden")
                missing.append(package)

        except subprocess.CalledProcessError as e:
            logger.error(f"Fehler beim Prüfen von {package}: {e}")
            missing.append(package)

    # Prüfe Python Dependencies
    python_packages = ['evdev', 'nxbt', 'dbus']
    for package in python_packages:
        try:
            __import__(package)
        except ImportError as e:
            logger.error(f"Python Paket {package} fehlt: {e}")
            print(f"Fehlendes Python-Paket: {package}")
            print("Bitte installieren Sie die Python-Pakete mit:")
            print("sudo pip3.9 install -r requirements.txt")
            return False

    if missing:
        print(f"Fehlende System-Pakete: {', '.join(missing)}")
        print("Bitte installieren Sie diese mit:")
        print(f"sudo apt-get install {' '.join(missing)}")
        return False

    logger.info("Alle Dependencies gefunden")
    return True

def main():
    check_python_version()

    parser = argparse.ArgumentParser(description='Xbox Switch Bridge')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--run', action='store_true', help='Bridge starten')
    group.add_argument('--install', action='store_true', help='Service installieren')
    group.add_argument('--uninstall', action='store_true', help='Service deinstallieren')
    group.add_argument('--status', action='store_true', help='Service Status anzeigen')
    parser.add_argument('--debug', action='store_true', help='Debug-Modus aktivieren')

    args = parser.parse_args()
    setup_logging(args.debug)

    if args.run:
        if check_dependencies():
            run_bridge()
    elif args.install:
        check_root()
        if check_dependencies():
            install_service()
    elif args.uninstall:
        check_root()
        uninstall_service()
    elif args.status:
        check_service_status()

if __name__ == '__main__':
    main()