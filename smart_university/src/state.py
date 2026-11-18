import threading
from copy import deepcopy
from datetime import datetime, timezone

import config


class SystemState:
    """Latest readings of every module, shared between threads."""

    def __init__(self):
        self.lock = threading.Lock()
        self._clear()

    def _clear(self):
        self.data = {module: {} for module in config.MODULES}
        self.last_updated = {module: None for module in config.MODULES}

    def update(self, module, new_data):
        if module not in self.data:
            return False
        with self.lock:
            self.data[module].update(new_data)
            self.last_updated[module] = datetime.now(timezone.utc).isoformat()
        return True

    def reset(self):
        with self.lock:
            self._clear()

    def get_module(self, module):
        with self.lock:
            return deepcopy(self.data.get(module, {}))

    def get_all(self):
        with self.lock:
            return {
                "data": deepcopy(self.data),
                "last_updated": deepcopy(self.last_updated),
            }


# Shared state used by the whole application
system_state = SystemState()
