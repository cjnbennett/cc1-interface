import serial
from serial import SerialException, SerialTimeoutException
import time
from enum import Enum


class Trigger(Enum):
    CONTINUOUS: int = 0
    START_STOP: int = 1


class Connection():
    connection = None
    port = ""

    def __init__(self, port):
        self.port = port
        self.open_connection(self.port)

    def open_connection(self, port):
        try:
            self.connection = serial.Serial(port)
        except (SerialException, SerialTimeoutException):
            pass # TODO -- better error reporting to user (and internally - i.e. no sentinel values)
        time.sleep(2)

    def send_serial(self, message):
        try:
            self.connection.write(bytearray(message, "utf-8"))
            response = self.connection.readline()
        except (SerialException, SerialTimeoutException):
            return ""
        return response

    def get_count(self, channel):
        response = self.send_serial("COUN:C" + str(channel+1) + "?")
        if response == "":
            return 0
        return int(response)

    def get_count_coin(self):
        response = self.send_serial("COUN:CO?")
        if response == "":
            return 0
        return int(response)

    def get_dwell_time(self):
        response = self.send_serial("DWEL?")
        if response == "":
            return 1000
        return int(response)

    def set_dwell_time(self, dwell_time):
        response = self.send_serial("DWEL " + str(dwell_time))
        return response

    def get_coin_window(self):
        response = self.send_serial("WIND?")
        if response == "":
            return 0
        return int(response)

    def set_coin_window(self, coin_window):
        response = self.send_serial(":WIND " + str(coin_window))
        return response

    def get_trigger(self):
        response = self.send_serial("TRIG?")
        if response == "":
            return 0
        return int(response)

    def set_trigger(self, trigger):
        response = self.send_serial(":TRIG " + str(trigger.value))
        return response

    def close_connection(self):
        try:
            self.connection.close()
        except (SerialException, SerialTimeoutException):
            pass # TODO -- better error reporting to user (and internally - i.e. no sentinel values)
