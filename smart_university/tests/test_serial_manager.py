from src.serial_manager import SerialManager


def test_initial_state():
    manager = SerialManager()
    assert manager.baud_rate == 115200
    assert manager.connections == {}
    assert manager.threads == {}
    assert manager.get_status() == {"parking": False, "classroom": False}


def test_unknown_module_rejected():
    assert SerialManager().connect("garage", "COM9") is False


def test_send_without_connection_fails():
    assert SerialManager().send_message("parking", {"cmd": "ping"}) is False
