from src.data_logger import DataLogger
from src.message_handler import MessageHandler
from src.state import SystemState


def make(tmp_path):
    state = SystemState()
    return state, MessageHandler(state, DataLogger(str(tmp_path)))


def msg(module, data, message_type="sensor_update"):
    return {"module": module, "message_type": message_type, "data": data}


def test_parking_message(tmp_path):
    state, handler = make(tmp_path)
    result = handler.handle_message(msg("parking", {"available_spaces": 3, "occupied_spaces": 2}))
    assert result["success"] is True
    assert state.get_module("parking")["available_spaces"] == 3


def test_classroom_message(tmp_path):
    state, handler = make(tmp_path)
    result = handler.handle_message(
        msg("classroom", {"distance_cm": 15, "person_near": True, "door_state": "closed"})
    )
    assert result["success"] is True
    assert state.get_module("classroom")["distance_cm"] == 15


def test_classroom_allows_empty_initial_reading(tmp_path):
    _, handler = make(tmp_path)
    result = handler.handle_message(
        msg("classroom", {"distance_cm": None, "access_granted": None, "door_state": "closed"})
    )
    assert result["success"] is True


def test_attendance_message(tmp_path):
    state, handler = make(tmp_path)
    data = {"student_id": "ST001", "student_name": "Ahmed",
            "recognized": True, "attendance_recorded": True}
    assert handler.handle_message(msg("attendance", data, "attendance_update"))["success"]
    assert state.get_module("attendance")["student_id"] == "ST001"


def test_wrong_message_type_rejected(tmp_path):
    _, handler = make(tmp_path)
    assert not handler.handle_message(msg("parking", {}, "attendance_update"))["success"]
    assert not handler.handle_message(msg("attendance", {}, "sensor_update"))["success"]


def test_invalid_json_and_unknown_module(tmp_path):
    _, handler = make(tmp_path)
    assert not handler.handle_line("not json")["success"]
    assert not handler.handle_message(msg("garage", {}))["success"]


def test_negative_parking_rejected(tmp_path):
    _, handler = make(tmp_path)
    assert not handler.handle_message(msg("parking", {"available_spaces": -1, "occupied_spaces": 2}))["success"]


def test_parking_counts_must_match_spaces(tmp_path):
    _, handler = make(tmp_path)
    data = {"available_spaces": 1, "occupied_spaces": 1, "spaces": [{"space_id": "P1", "status": "occupied"}]}
    assert not handler.handle_message(msg("parking", data))["success"]


def test_negative_distance_rejected(tmp_path):
    _, handler = make(tmp_path)
    assert not handler.handle_message(msg("classroom", {"distance_cm": -10}))["success"]


def test_invalid_classroom_value_rejected(tmp_path):
    _, handler = make(tmp_path)
    assert not handler.handle_message(msg("classroom", {"distance_cm": 15, "person_near": "yes"}))["success"]


def test_attendance_without_student_id_rejected(tmp_path):
    _, handler = make(tmp_path)
    data = {"student_name": "Ahmed", "recognized": True, "attendance_recorded": True}
    assert not handler.handle_message(msg("attendance", data, "attendance_update"))["success"]


def test_log_false_skips_csv(tmp_path):
    _, handler = make(tmp_path)
    handler.handle_message(msg("parking", {"available_spaces": 1, "occupied_spaces": 0}), log=False)
    assert not (tmp_path / "parking_history.csv").exists()
