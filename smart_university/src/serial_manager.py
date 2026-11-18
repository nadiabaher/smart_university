import json
import threading

import serial

import config
from src.message_handler import MessageHandler

SERIAL_MODULES = ("parking", "classroom")


class SerialManager:
    """Reads JSON lines from the ESP32 boards (one thread per board)."""

    def __init__(self, handler=None, baud_rate=config.BAUD_RATE):
        self.handler = handler if handler is not None else MessageHandler()
        self.baud_rate = baud_rate
        self.connections = {}
        self.threads = {}
        self.running = {}
        self.connection_lock = threading.Lock()

    def connect(self, module, port):
        if module not in SERIAL_MODULES:
            print(f"Unknown module: {module}")
            return False

        thread = self.threads.get(module)
        if thread and thread.is_alive():
            print(f"{module} is already running.")
            return False

        stop_event = threading.Event()
        self.running[module] = stop_event
        self.threads[module] = threading.Thread(
            target=self._read_serial, args=(module, port, stop_event), daemon=True
        )
        self.threads[module].start()
        return True

    def _read_serial(self, module, port, stop_event):
        # Reconnects automatically if the board is unplugged
        while not stop_event.is_set():
            connection = None
            try:
                print(f"Connecting {module} to {port}...")
                with serial.Serial(port=port, baudrate=self.baud_rate,
                                   timeout=1, write_timeout=2) as connection:
                    with self.connection_lock:
                        self.connections[module] = connection
                    print(f"{module} connected.")

                    while not stop_event.is_set():
                        line = connection.readline()
                        if not line:
                            continue
                        try:
                            text = line.decode("utf-8").strip()
                        except UnicodeDecodeError:
                            print(f"Invalid text received from {module}")
                            continue
                        if not text:
                            continue
                        result = self.handler.handle_line(text)
                        if not result["success"]:
                            print(f"{module} message error: {result['error']}")

            except (serial.SerialException, OSError) as error:
                if not stop_event.is_set():
                    print(f"{module} connection error: {error}")
                stop_event.wait(2)
            finally:
                with self.connection_lock:
                    if self.connections.get(module) is connection:
                        self.connections.pop(module, None)

    def send_message(self, module, message):
        """Send a JSON command to a board (for example: open the door)."""
        try:
            payload = (json.dumps(message) + "\n").encode("utf-8")
        except (TypeError, ValueError):
            print("Message cannot be converted to JSON.")
            return False

        with self.connection_lock:
            connection = self.connections.get(module)
            if connection is None or not connection.is_open:
                print(f"{module} is not connected.")
                return False
            try:
                connection.write(payload)
                return True
            except (serial.SerialException, OSError) as error:
                print(f"Could not send message: {error}")
                return False

    def disconnect(self, module):
        if module in self.running:
            self.running[module].set()
        thread = self.threads.get(module)
        if thread and thread.is_alive():
            thread.join(timeout=3)

    def disconnect_all(self):
        for module in list(self.running):
            self.disconnect(module)

    def get_status(self):
        with self.connection_lock:
            return {
                module: (
                    self.connections.get(module) is not None
                    and self.connections[module].is_open
                )
                for module in SERIAL_MODULES
            }
