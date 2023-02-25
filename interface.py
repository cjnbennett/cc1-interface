import serial
import time

class Connection():
    connection = None
    port = ""

    def __init__(self, port):
        self.port = port
        self.open_connection(self.port)

    def open_connection(self, port):
        self.connection = serial.Serial(port)
        time.sleep(2)

    def get_count(self, channel):
        self.connection.write(b"COUN:C" + bytearray(str(channel+1), "utf-8") + b"?")
        response = self.connection.readline()
        return int(response)

    # def get_count_AB(self):
    #     self.connection.write(b"COUN:CO?")
    #     response = self.connection.readline()
    #     return int(response)

    def get_dwell_time(self):
        self.connection.write(b"DWEL?")
        response = self.connection.readline()
        return int(response)

    def set_dwell_time(self, dwell_time):
        self.connection.write(b"DWEL " + bytearray(dwell_time))
        response = self.connection.readline()
        return response

    def get_coin_window(self):
        self.connection.write(b"WIND?")
        response = self.connection.readline()
        return int(response)

    def set_coin_window(self, coin_window):
        self.connection.write(b":WIND " + bytearray(coin_window))
        response = self.connection.readline()
        return response

    def close_connection(self):
        self.connection.close()
