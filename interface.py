import serial
import time

connection = None

def open_connection():
    global connection
    connection = serial.Serial("/dev/ttyACM0")
    time.sleep(2)

def get_count_A():
    connection.write(b"COUN:C1?")
    response = connection.readline()
    return int(response)

def get_count_B():
    connection.write(b"COUN:C2?")
    response = connection.readline()
    return int(response)

def get_count_AB():
    connection.write(b"COUN:CO?")
    response = connection.readline()
    return int(response)

def get_count_Bprime():
    return 0

def get_count_BBprime():
    return 0

def get_count_ABBprime():
    return 0

def get_dwell_time():
    connection.write(b"DWEL?")
    response = connection.readline()
    return int(response)

def set_dwell_time(dwell_time):
    connection.write(b"DWEL " + bytearray(dwell_time))
    response = connection.readline()
    return response

def get_coin_window():
    connection.write(b"WIND?")
    response = connection.readline()
    return int(response)

def set_coin_window(coin_window):
    connection.write(b":WIND " + bytearray(coin_window))
    response = connection.readline()
    return response

def close_connection():
    connection.close()
