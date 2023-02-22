void setup() {
  Serial.begin(9600);
}

void loop() {
  String command;
  String response = "Unknown Command.";

  if (Serial.available()) {
    command = Serial.readStringUntil('\n');

    if (command == "COUN:C1?") {
      response = "10238";
    } else if (command == "COUN:C2?") {
      response = "34878";
    } else if (command == "COUN:CO?") {
      response = "349";
    } else if (command == ":CLEA") {
      response = "";
    } else if (command.startsWith(":DELA ")) {
      response = "";
    } else if (command == ":DELA?") {
      response = "1000";
    } else if (command.startsWith(":DWEL ")) {
      response = "";
    } else if (command == "DWEL?") {
      response = "2000";
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
}
