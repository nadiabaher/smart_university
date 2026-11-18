import json
from datetime import datetime

import config
from src.access_logic import evaluate_access
from src.message_handler import MessageHandler


class HardwareSimulator:
    """Produces the same JSON messages the ESP32 boards will send."""

    def __init__(self, handler=None):
        self.handler = handler if handler is not None else MessageHandler()
        self.spaces = {space_id: "available" for space_id in config.PARKING_SPACES}
        self.latest_attendance = {}
        self.classroom = {
            "distance_cm": None,
            "person_near": False,
            "rfid_valid": None,
            "fingerprint_valid": None,
            "face_recognized": None,
            "access_granted": None,
            "door_state": "closed",
        }
        # Initial readings go to the dashboard but not into the history files
        self._publish("parking", "sensor_update", self.get_parking_data(), log=False)
        self._publish("classroom", "sensor_update", self.classroom, log=False)

    def _publish(self, module, message_type, data, log=True):
        message = {"module": module, "message_type": message_type, "data": data}
        return self.handler.handle_line(json.dumps(message), log=log)

    # ---------- parking ----------
    def park_car(self, space_id):
        if self.spaces.get(space_id) != "available":
            return False
        self.spaces[space_id] = "occupied"
        self._publish("parking", "sensor_update", self.get_parking_data())
        return True

    def remove_car(self, space_id):
        if self.spaces.get(space_id) != "occupied":
            return False
        self.spaces[space_id] = "available"
        self._publish("parking", "sensor_update", self.get_parking_data())
        return True

    def get_parking_data(self):
        occupied = sum(1 for s in self.spaces.values() if s == "occupied")
        return {
            "available_spaces": len(self.spaces) - occupied,
            "occupied_spaces": occupied,
            "parked_cars_count": occupied,
            "pressure_occupied_count": occupied,
            "spaces": [
                {"space_id": space_id, "status": status}
                for space_id, status in self.spaces.items()
            ],
        }

    # ---------- attendance ----------
    def record_attendance(self, student_id, student_name):
        self.latest_attendance = {
            "student_id": student_id,
            "student_name": student_name,
            "recognized": True,
            "attendance_recorded": True,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "session_id": config.SESSION_ID,
        }
        self._publish("attendance", "attendance_update", self.latest_attendance)
        return self.latest_attendance

    def unknown_student(self):
        self.latest_attendance = {
            "student_id": None,
            "student_name": None,
            "recognized": False,
            "attendance_recorded": False,
            "timestamp": None,
            "session_id": config.SESSION_ID,
        }
        self._publish("attendance", "attendance_update", self.latest_attendance)
        return self.latest_attendance

    # ---------- classroom ----------
    def update_classroom(self, distance_cm, rfid_valid, fingerprint_valid,
                         face_recognized):
        self.classroom = {
            "distance_cm": distance_cm,
            "rfid_valid": rfid_valid,
            "fingerprint_valid": fingerprint_valid,
            "face_recognized": face_recognized,
            **evaluate_access(distance_cm, rfid_valid, fingerprint_valid, face_recognized),
        }
        self._publish("classroom", "sensor_update", self.classroom)
        return self.classroom
