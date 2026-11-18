import json

import config
from src.data_logger import data_logger
from src.state import system_state


def _fail(error):
    return {"success": False, "error": error}


class MessageHandler:
    """Validates one JSON message, updates the state and logs it."""

    def __init__(self, state=None, logger=None):
        self.state = state if state is not None else system_state
        self.logger = logger if logger is not None else data_logger

    def handle_line(self, line, log=True):
        try:
            message = json.loads(line)
        except (json.JSONDecodeError, TypeError):
            return _fail("Invalid JSON message")
        return self.handle_message(message, log=log)

    def handle_message(self, message, log=True):
        if not isinstance(message, dict):
            return _fail("Message must be a JSON object")

        module = message.get("module")
        message_type = message.get("message_type")
        data = message.get("data")

        if module not in config.MODULES:
            return _fail("Unknown module")
        if message_type not in ("sensor_update", "attendance_update"):
            return _fail("Unknown message type")

        expected = "attendance_update" if module == "attendance" else "sensor_update"
        if message_type != expected:
            return _fail(f"{module} must use {expected}")
        if not isinstance(data, dict):
            return _fail("Message data must be an object")

        validator = {
            "parking": self._validate_parking,
            "classroom": self._validate_classroom,
            "attendance": self._validate_attendance,
        }[module]
        error = validator(data)
        if error:
            return _fail(error)

        self.state.update(module, data)
        if log:
            self.logger.log_data(module, data)
        return {"success": True, "module": module, "message_type": message_type}

    @staticmethod
    def _validate_parking(data):
        for field in ("available_spaces", "occupied_spaces"):
            if field in data:
                value = data[field]
                if type(value) is not int or value < 0:
                    return f"{field} must be a non-negative integer"

        if all(k in data for k in ("available_spaces", "occupied_spaces", "spaces")):
            if not isinstance(data["spaces"], list):
                return "spaces must be a list"
            if data["available_spaces"] + data["occupied_spaces"] != len(data["spaces"]):
                return "Parking space counts do not match"
        return None

    @staticmethod
    def _validate_classroom(data):
        distance = data.get("distance_cm")
        if distance is not None:
            if (
                isinstance(distance, bool)
                or not isinstance(distance, (int, float))
                or distance < 0
            ):
                return "distance_cm must be a non-negative number"

        for field in ("person_near", "rfid_valid", "fingerprint_valid",
                      "face_recognized", "access_granted"):
            value = data.get(field)
            if value is not None and not isinstance(value, bool):
                return f"{field} must be True, False, or None"

        if "door_state" in data and data["door_state"] not in ("open", "closed"):
            return "door_state must be open or closed"
        return None

    @staticmethod
    def _validate_attendance(data):
        recognized = data.get("recognized")
        recorded = data.get("attendance_recorded")

        if recognized is not None and not isinstance(recognized, bool):
            return "recognized must be True or False"
        if recorded is not None and not isinstance(recorded, bool):
            return "attendance_recorded must be True or False"

        if recorded is True:
            if recognized is not True:
                return "Attendance cannot be recorded for an unrecognized student"
            if not data.get("student_id"):
                return "Student ID is required"
            name = data.get("student_name")
            if not isinstance(name, str) or not name.strip():
                return "Student name is required"
        return None
