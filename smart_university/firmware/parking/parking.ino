// PLACEHOLDER for the parking teammate (ESP32 #1).
// Print ONE JSON line per update at 115200 baud, for example:
// {"module":"parking","message_type":"sensor_update","data":{"available_spaces":4,"occupied_spaces":1,"spaces":[{"space_id":"P1","status":"occupied"},{"space_id":"P2","status":"available"}]}}
// The pressure threshold (car vs person) is decided here, on the ESP32.
// See docs/PROTOCOL.md.

void setup() {
  Serial.begin(115200);
}

void loop() {
}
