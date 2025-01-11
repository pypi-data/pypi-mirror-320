#!/usr/bin/env python3
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

def run_bridge():
    """Startet die Bridge direkt"""
    if os.geteuid() != 0:
        print("Dieses Programm muss mit sudo ausgeführt werden!")
        sys.exit(1)

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

    for package in required_packages:
        if not shutil.which(package):
            missing.append(package)

    if missing:
        print(f"Fehlende Pakete: {', '.join(missing)}")
        print("Bitte installieren Sie diese mit:")
        print(f"sudo apt-get install {' '.join(missing)}")
        return False
    return True

def main():
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
        if os.geteuid() != 0:
            print("Installation muss mit sudo ausgeführt werden!")
            sys.exit(1)
        if check_dependencies():
            install_service()
    elif args.uninstall:
        if os.geteuid() != 0:
            print("Deinstallation muss mit sudo ausgeführt werden!")
            sys.exit(1)
        uninstall_service()
    elif args.status:
        check_service_status()

if __name__ == '__main__':
    main()