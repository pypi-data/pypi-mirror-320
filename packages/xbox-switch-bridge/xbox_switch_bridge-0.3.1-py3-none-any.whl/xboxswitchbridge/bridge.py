#!/usr/bin/env python3

import asyncio
import logging
import sys
import os
import signal
import evdev
from evdev import InputDevice, ecodes
import nxbt
import re
import time
import threading

class XboxSwitchBridge:
    def __init__(self):
        # Basis-Setup
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        logging.getLogger("nxbt").setLevel(logging.WARNING)

        # Controller Setup
        self.nx = nxbt.Nxbt()
        self.controller_index = None
        self.xbox_device = None

        # Input State
        self.current_state = None

        # Konfiguration
        self.config = {
            'deadzone': 5000,          # Angepasste Deadzone
            'stick_sensitivity': 1.0,   # Stick Empfindlichkeit
            'update_rate': 120         # Hz für Pro Controller
        }

        # Thread Control
        self.keep_running = True
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, sig, frame):
        """Behandelt STRG+C"""
        self.logger.info("Beende Bridge...")
        self.keep_running = False
        if self.controller_index is not None:
            try:
                self.nx.remove_controller(self.controller_index)
            except Exception as e:
                self.logger.error(f"Fehler beim Beenden: {e}")
        sys.exit(0)

    def map_stick_value(self, value):
        """Verbesserte nicht-lineare Stick-Mapping Funktion"""
        XBOX_MAX = 32767

        # Deadzone-Behandlung
        if abs(value) < self.config['deadzone']:
            return 0

        # Berechne den adjustierten Wert außerhalb der Deadzone
        adjusted_value = value - (self.config['deadzone'] * (1 if value > 0 else -1))
        max_adjusted = XBOX_MAX - self.config['deadzone']

        # Normalisiere den Wert
        normalized = (adjusted_value * XBOX_MAX) / (max_adjusted * XBOX_MAX)

        # Nicht-lineare Transformation für bessere Kontrolle
        curved = normalized ** 3 if abs(normalized) > 0.5 else normalized * 0.5

        # Skaliere auf Switch-Bereich und wende Sensitivität an
        return int(curved * 100 * self.config['stick_sensitivity'])

    async def handle_stick_event(self, event_code, value, stick_side):
        """Stick-Event Verarbeitung"""
        is_x_axis = event_code in [0, 3]
        axis = 'x' if is_x_axis else 'y'

        stick_position = self.map_stick_value(value)

        # Y-Achse für Switch-Kompatibilität invertieren
        if not is_x_axis:
            stick_position = -stick_position

        # Update controller state
        if stick_side == 'left':
            if axis == 'x':
                self.current_state['L_STICK']['X_VALUE'] = stick_position
            else:
                self.current_state['L_STICK']['Y_VALUE'] = stick_position
        else:
            if axis == 'x':
                self.current_state['R_STICK']['X_VALUE'] = stick_position
            else:
                self.current_state['R_STICK']['Y_VALUE'] = stick_position

    async def map_xbox_to_switch(self, event):
        """Button-Mapping Funktion"""
        if event.type == ecodes.EV_KEY:
            button_mapping = {
                304: 'A',      # A
                305: 'B',      # B
                307: 'X',      # X
                308: 'Y',      # Y
                310: 'L',      # LB
                311: 'R',      # RB
                314: 'MINUS',  # Select
                315: 'PLUS',   # Start
                316: 'HOME',   # Xbox Button
                317: 'ZL',     # LT
                318: 'ZR',     # RT
            }

            if event.code in button_mapping:
                button = button_mapping[event.code]
                self.current_state[button] = bool(event.value)

    def input_update_loop(self):
        """Thread für kontinuierliches Input-Update"""
        while self.keep_running:
            try:
                if self.controller_index is not None and self.current_state is not None:
                    self.nx.set_controller_input(self.controller_index, self.current_state)
            except Exception as e:
                self.logger.error(f"Input update error: {e}")
            time.sleep(1/self.config['update_rate'])

    async def run(self):
        """Hauptfunktion"""
        # Xbox Controller suchen
        devices = [InputDevice(path) for path in evdev.list_devices()]
        for dev in devices:
            dev_str = re.sub(r'[\W_]+', '', dev.name.lower())
            if "xbox" in dev_str:
                self.logger.info(f"Xbox Controller gefunden: {dev.name}")
                self.xbox_device = dev
                break
        else:
            self.logger.error("Kein Xbox Controller gefunden!")
            return

        # Switch Controller erstellen
        try:
            self.controller_index = self.nx.create_controller(
                nxbt.PRO_CONTROLLER,
                colour_body=[0, 0, 255],  # Blaue Farbe
                colour_buttons=[255, 255, 255]  # Weiße Buttons
            )
            self.logger.info("Warte auf Switch Verbindung...")
            self.nx.wait_for_connection(self.controller_index)
            self.logger.info("Switch verbunden!")
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen des Controllers: {e}")
            return

        # Input State initialisieren
        self.current_state = self.nx.create_input_packet()

        # Input Update Thread starten
        update_thread = threading.Thread(target=self.input_update_loop)
        update_thread.daemon = True
        update_thread.start()

        self.logger.info("=== Xbox zu Switch Bridge aktiv ===")
        self.logger.info("1. Öffne 'Controller' → 'Change Grip/Order' auf der Switch")
        self.logger.info("2. STRG+C zum Beenden")

        try:
            async for event in self.xbox_device.async_read_loop():
                if event.type == ecodes.EV_KEY:
                    await self.map_xbox_to_switch(event)
                elif event.type == ecodes.EV_ABS:
                    if event.code in [0, 1]:  # Linker Stick
                        await self.handle_stick_event(event.code, event.value, 'left')
                    elif event.code in [3, 4]:  # Rechter Stick
                        await self.handle_stick_event(event.code, event.value, 'right')
        except Exception as e:
            self.logger.error(f"Event Loop Fehler: {e}")
        finally:
            self.keep_running = False
            if self.controller_index is not None:
                self.nx.remove_controller(self.controller_index)

async def main():
    if os.geteuid() != 0:
        print("Dieses Skript muss mit sudo ausgeführt werden!")
        sys.exit(1)

    bridge = XboxSwitchBridge()
    await bridge.run()

if __name__ == "__main__":
    asyncio.run(main())