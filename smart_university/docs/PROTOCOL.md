# JSON Protocol

Every board (and the face recognition code) sends **one JSON object per line**
(115200 baud on serial, end each message with a newline). Invalid messages are
rejected and printed in the terminal; nothing is saved.

```
{"module": "...", "message_type": "...", "data": { ... }}
```

| module     | message_type        | sent by                  |
|------------|---------------------|--------------------------|
| parking    | `sensor_update`     | ESP32 #1                 |
| classroom  | `sensor_update`     | ESP32 #2                 |
| attendance | `attendance_update` | laptop (face recognition)|

You may send only the fields that changed; the dashboard merges them.

## parking
```json
{"module":"parking","message_type":"sensor_update","data":{
  "available_spaces":4,"occupied_spaces":1,
  "spaces":[{"space_id":"P1","status":"occupied"},{"space_id":"P2","status":"available"}]}}
```
- Counts are non-negative integers. If `spaces` is sent, `available + occupied` must equal its length.
- Optional: `parked_cars_count`, `pressure_occupied_count`.
- **The ESP32 decides car vs person** (pressure threshold, calibrated on the real sensor) and only reports `occupied` / `available`.

## classroom
```json
{"module":"classroom","message_type":"sensor_update","data":{
  "distance_cm":30,"person_near":true,"rfid_valid":true,
  "fingerprint_valid":null,"face_recognized":null,
  "access_granted":true,"door_state":"open"}}
```
- `distance_cm`: number >= 0 (or null). `door_state`: `"open"` or `"closed"`.
- Booleans may be `true`, `false` or `null` (= not checked).
- Rule used by the simulator (`src/access_logic.py`): person within 50 cm AND any one credential valid -> open.
  If nobody is near, `access_granted` is `null` (waiting).

## attendance
```json
{"module":"attendance","message_type":"attendance_update","data":{
  "student_id":"2024001","student_name":"Ahmed","recognized":true,
  "attendance_recorded":true,"timestamp":"2026-11-18 10:30:00","session_id":"LAB_01"}}
```
- `attendance_recorded: true` requires `recognized: true`, a `student_id` and a `student_name`.
- Unknown face: `recognized: false`, `attendance_recorded: false`.
