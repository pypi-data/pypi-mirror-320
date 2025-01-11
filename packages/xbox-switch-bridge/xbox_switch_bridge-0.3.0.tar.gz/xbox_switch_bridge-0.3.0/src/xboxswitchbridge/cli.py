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
    required_packages = ['bluetooth', 'bluez', 'bluez-tools']
    missing = []

    try:
        import evdev
        import nxbt
        import dbus
        import gi
    except ImportError as e:
        print(f"Fehlende Python-Pakete: {e}")
        print("Bitte installieren Sie diese mit:")
        print("sudo pip install -r requirements.txt")
        return False

    for package in required_packages:
        if not shutil.which(package):
            missing.append(package)

    if missing:
        print(f"Fehlende System-Pakete: {', '.join(missing)}")
        print("Bitte installieren Sie diese mit:")
        print(f"sudo apt-get install {' '.join(missing)}")
        return False
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