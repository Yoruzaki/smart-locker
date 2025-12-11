/*
 * Smart Locker Arduino Mega firmware
 * Pins 22-52: relays (even)
 * Pins 23-53: sensors (odd)
 * Serial protocol (115200 baud):
 *  - OPEN:<id>    -> activates relay for locker id
 *  - READ:<id>    -> returns OPEN/CLOSED
 *  - STATUS       -> returns OK
 *  - PING         -> returns OK
 */

const int RELAY_PINS[16] = {22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52};
const int SENSOR_PINS[16] = {23,25,27,29,31,33,35,37,39,41,43,45,47,49,51,53};
const int RESERVED_LOCKER = 16; // Locker 16 reserved
const unsigned long RELAY_PULSE_MS = 1200;

String inputBuffer = "";

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < 16; i++) {
    pinMode(RELAY_PINS[i], OUTPUT);
    digitalWrite(RELAY_PINS[i], LOW);
    pinMode(SENSOR_PINS[i], INPUT_PULLUP);
  }
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      handleCommand(inputBuffer);
      inputBuffer = "";
    } else if (c != '\r') {
      inputBuffer += c;
    }
  }
}

void handleCommand(String cmd) {
  cmd.trim();
  if (cmd == "PING") {
    Serial.println("OK");
    return;
  }
  if (cmd == "STATUS") {
    Serial.println("OK");
    return;
  }
  if (cmd.startsWith("OPEN:")) {
    int id = cmd.substring(5).toInt();
    if (id == RESERVED_LOCKER) {
      Serial.println("ERROR:RESERVED");
      return;
    }
    if (id < 1 || id > 16) {
      Serial.println("ERROR:BAD_ID");
      return;
    }
    triggerRelay(id - 1);
    Serial.println("OK");
    return;
  }
  if (cmd.startsWith("READ:")) {
    int id = cmd.substring(5).toInt();
    if (id < 1 || id > 16) {
      Serial.println("ERROR:BAD_ID");
      return;
    }
    bool closed = readSensor(id - 1);
    Serial.println(closed ? "CLOSED" : "OPEN");
    return;
  }
  Serial.println("ERROR:UNKNOWN");
}

void triggerRelay(int idx) {
  digitalWrite(RELAY_PINS[idx], HIGH);
  delay(RELAY_PULSE_MS);
  digitalWrite(RELAY_PINS[idx], LOW);
}

bool readSensor(int idx) {
  // Assuming normally-closed magnetic sensor: LOW = closed
  int v = digitalRead(SENSOR_PINS[idx]);
  return v == LOW;
}

