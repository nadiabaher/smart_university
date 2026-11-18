# Smart University System

IoT project: smart parking, classroom access and face-recognition attendance.
ESP32 boards -> serial JSON -> Python -> Streamlit dashboard + CSV history.

## Run
```
pip install -r requirements.txt
streamlit run app.py        # dashboard (simulation mode by default)
pytest                      # tests
```

## Project layout
```
app.py                  dashboard (run this)
config.py               ports, COM numbers, thresholds, HARDWARE_MODE
src/
  message_handler.py    validates incoming JSON, updates state, logs to CSV
  state.py              latest readings shared by the whole app
  data_logger.py        CSV history in data/
  access_logic.py       the door-access rule
  adapters.py           formats data for the dashboard
  simulator.py          fake sensors for demos without hardware
  serial_manager.py     reads the ESP32 boards over USB
  face_recognition.py   <- attendance teammate pastes here
firmware/parking/       <- parking teammate pastes ESP32 code here
firmware/door/          <- classroom teammate pastes ESP32 code here
docs/PROTOCOL.md        exact JSON each teammate must send
tests/
```

## Connecting the real hardware
1. In `config.py` set `PARKING_PORT`, `CLASSROOM_PORT` and `HARDWARE_MODE = True`.
2. `streamlit run app.py` — the dashboard starts the serial readers itself and auto-refreshes.
3. Each teammate's code must output the messages in `docs/PROTOCOL.md`.
