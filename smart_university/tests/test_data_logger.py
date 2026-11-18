import csv

from src.data_logger import DataLogger


def read(path):
    with open(path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return reader.fieldnames, list(reader)


def test_old_records_kept_and_new_columns_added(tmp_path):
    logger = DataLogger(str(tmp_path))
    logger.log_data("parking", {"available_spaces": 3, "occupied_spaces": 2})
    logger.log_data("parking", {"available_spaces": 4, "occupied_spaces": 1,
                                "parked_cars_count": 1})

    fields, rows = read(tmp_path / "parking_history.csv")
    assert len(rows) == 2
    assert "parked_cars_count" in fields
    assert rows[0]["available_spaces"] == "3"
    assert rows[1]["parked_cars_count"] == "1"
    assert rows[0]["timestamp"] and rows[1]["timestamp"]


def test_space_list_is_readable(tmp_path):
    logger = DataLogger(str(tmp_path))
    logger.log_data("parking", {"spaces": [{"space_id": "P1", "status": "occupied"},
                                           {"space_id": "P2", "status": "available"}]})
    _, rows = read(tmp_path / "parking_history.csv")
    assert rows[0]["spaces"] == "P1=occupied;P2=available"


def test_clear_removes_history(tmp_path):
    logger = DataLogger(str(tmp_path))
    logger.log_data("parking", {"available_spaces": 1})
    logger.clear()
    assert not (tmp_path / "parking_history.csv").exists()
