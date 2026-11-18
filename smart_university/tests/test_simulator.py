from src.data_logger import DataLogger
from src.message_handler import MessageHandler
from src.simulator import HardwareSimulator
from src.state import SystemState


def make(tmp_path):
    state = SystemState()
    handler = MessageHandler(state, DataLogger(str(tmp_path)))
    return state, HardwareSimulator(handler)


def test_parking(tmp_path):
    state, sim = make(tmp_path)
    assert sim.get_parking_data()["available_spaces"] == 5

    assert sim.park_car("P1") is True
    assert sim.park_car("P1") is False  # already occupied
    assert state.get_module("parking")["occupied_spaces"] == 1
    assert state.get_module("parking")["available_spaces"] == 4

    assert sim.remove_car("P1") is True
    assert sim.remove_car("P1") is False  # already free
    assert state.get_module("parking")["occupied_spaces"] == 0


def test_attendance(tmp_path):
    state, sim = make(tmp_path)
    result = sim.record_attendance("S001", "Ahmed")
    assert result["attendance_recorded"] is True
    assert state.get_module("attendance")["student_id"] == "S001"

    result = sim.unknown_student()
    assert result["recognized"] is False
    assert state.get_module("attendance")["attendance_recorded"] is False


def test_classroom(tmp_path):
    state, sim = make(tmp_path)
    result = sim.update_classroom(30, True, False, False)
    assert result["access_granted"] is True
    assert state.get_module("classroom")["door_state"] == "open"

    result = sim.update_classroom(30, False, False, False)
    assert result["access_granted"] is False
    assert state.get_module("classroom")["door_state"] == "closed"


def test_initial_readings_reach_state_but_not_history(tmp_path):
    state, _ = make(tmp_path)
    assert state.get_module("parking")["available_spaces"] == 5
    assert state.get_module("classroom")["door_state"] == "closed"
    assert not (tmp_path / "parking_history.csv").exists()
    assert not (tmp_path / "classroom_history.csv").exists()
