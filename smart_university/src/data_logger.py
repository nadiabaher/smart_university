import csv
import glob
import json
import os
import threading
from datetime import datetime

import config


class DataLogger:
    """Appends every valid message to data/<module>_history.csv."""

    def __init__(self, folder=config.DATA_DIR):
        self.folder = folder
        self.lock = threading.Lock()
        os.makedirs(self.folder, exist_ok=True)

    def _path(self, module):
        return os.path.join(self.folder, f"{module}_history.csv")

    @staticmethod
    def _format(value):
        # Keep lists readable in a CSV cell
        if isinstance(value, list) and all(
            isinstance(item, dict) and "space_id" in item for item in value
        ):
            return ";".join(
                f"{item['space_id']}={item.get('status', '?')}" for item in value
            )
        if isinstance(value, (list, dict)):
            return json.dumps(value)
        return value

    def log_data(self, module, data):
        row = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        row.update({key: self._format(value) for key, value in data.items()})
        path = self._path(module)

        with self.lock:
            fieldnames, old_rows = ["timestamp"], []
            if os.path.isfile(path):
                with open(path, "r", newline="", encoding="utf-8") as file:
                    reader = csv.DictReader(file)
                    fieldnames = list(reader.fieldnames or fieldnames)
                    old_rows = list(reader)

            # New columns are added without losing old records
            for field in row:
                if field not in fieldnames:
                    fieldnames.append(field)

            with open(path, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(old_rows)
                writer.writerow(row)
        return True

    def clear(self):
        """Delete all history files."""
        with self.lock:
            for path in glob.glob(os.path.join(self.folder, "*_history.csv")):
                os.remove(path)


data_logger = DataLogger()
