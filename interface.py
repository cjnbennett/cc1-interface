import serial
from serial import SerialException, SerialTimeoutException
import time

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
            pass # TODO -- better error reporting to user
        time.sleep(2)

    def get_count(self, channel):
        try:
            self.connection.write(b"COUN:C" + bytearray(str(channel+1), "utf-8") + b"?")
            response = self.connection.readline()
        except (SerialException, SerialTimeoutException):
            return 0
        return int(response)

    def get_count_coin(self):
        try:
            self.connection.write(b"COUN:CO?")
            response = self.connection.readline()
        except (SerialException, SerialTimeoutException):
            return 0
        return int(response)

    def get_dwell_time(self):
        try:
            self.connection.write(b"DWEL?")
            response = self.connection.readline()
        except (SerialException, SerialTimeoutException):
            return 1000
        return int(response)

    def set_dwell_time(self, dwell_time):
        try:
            self.connection.write(b"DWEL " + bytearray(dwell_time))
            response = self.connection.readline()
        except (SerialException, SerialTimeoutException):
            return ""
        return response

    def get_coin_window(self):
        try:
            self.connection.write(b"WIND?")
            response = self.connection.readline()
        except (SerialException, SerialTimeoutException):
            return ""
        return int(response)

    def set_coin_window(self, coin_window):
        try:
            self.connection.write(b":WIND " + bytearray(coin_window))
            response = self.connection.readline()
        except (SerialException, SerialTimeoutException):
            return ""
        return response

    def close_connection(self):
        try:
            self.connection.close()
        except (SerialException, SerialTimeoutException):
            pass # TODO -- better error reporting to user
