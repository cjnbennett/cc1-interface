int dwell = 1000;

void setup() {
  Serial.begin(9600);
}

void loop() {
  String command;
  String response = "Unknown Command.";

  if (Serial.available()) {
    command = Serial.readStringUntil('\n');

    if (command == "COUN:C1?") {
      response = String(random(100000));
    } else if (command == "COUN:C2?") {
      response = String(random(100000));
    } else if (command == "COUN:CO?") {
      response = String(random(1000));
    } else if (command == ":CLEA") {
      response = "";
    } else if (command.startsWith(":DELA ")) {
      response = "";
    } else if (command == ":DELA?") {
      response = "0";
    } else if (command.startsWith(":DWEL ")) {
      response = "";
    } else if (command == "DWEL?") {
      response = String(dwell);
    } else if (command == "FIRM?") {
      response = "v1.0";
    } else if (command.startsWith(":GATE ")) {
      response = "";
    } else if (command == "GATE?") {
      response = "0";
    } else if (command.startsWith(":SUBT ")) {
      response = "";
    } else if (command == "SUBT?") {
      response = "1";
    } else if (command.startsWith(":TRIG ")) {
      response = "";
    } else if (command == "TRIG?") {
      response = "0";
    } else if (command.startsWith(":WIND ")) {
      response = "";
    } else if (command == "WIND?") {
      response = "1284";
    }

    Serial.println(response);
  }

  delay(dwell);
}
