"""All settings in one place."""

# Keep False until the ESP32 boards are connected
HARDWARE_MODE = False

# Change these COM ports when you connect the ESP32 boards
PARKING_PORT = "COM3"
CLASSROOM_PORT = "COM4"
BAUD_RATE = 115200

# A person is "near" the classroom door at or below this distance
PERSON_NEAR_CM = 50

PARKING_SPACES = ["P1", "P2", "P3", "P4", "P5"]
SESSION_ID = "LAB_01"
DATA_DIR = "data"

MODULES = ("parking", "attendance", "classroom")
