"""
Sentron ISFET Evaluation Kit Readout Utility

This script provides a terminal-based interface for retrieving
pH, temperature, and slope values from the Sentron ISFET pH
Evaluation Kit.

Functions:
    - Retrieve and decode pH readings
    - Retrieve and decode temperature readings
    - Retrieve and decode slope values
    - Print raw and decoded protocol responses for debugging

Based on the communication protocol supplied with the
Sentron Evaluation Kit documentation.
"""

import serial
import time

# Serial port used by the Sentron USB interface.
# This device name may vary between computers and operating systems.
#
# Examples:
#
# macOS:
#   /dev/cu.usbserial-FTE868J4
#
# Raspberry Pi / Linux:
#   /dev/ttyUSB0
#
# To locate the serial port:
#
# macOS:
#   ls /dev/cu.*
#
# Raspberry Pi / Linux:
#   ls /dev/ttyUSB*
PORT = "/dev/cu.usbserial-FTE868J4"

# Serial settings for the Sentron AD Converter / USB interface.
BAUD = 115200
TIMEOUT = 2


def decimal_bytes(data):
    """
    Convert raw bytes returned by the Sentron module into
    zero-padded decimal byte strings.
    """
    return " ".join(f"{b:03d}" for b in data)


def send_command(ser, command):
    """
    Send a command to the Sentron module and return the raw response.
    """
    ser.reset_input_buffer()
    ser.write(command)
    ser.flush()

    return ser.read_until(b"\r\n")


def decode_ph(data):
    """
    Decode pH from the Sentron pH response.

    Protocol format:
        pH command returns bytes A B C ...
    Formula:
        pH = A*4096 + B*64 + C
    The returned value is divided by 1000 so the result is in pH units.
    """
    if len(data) < 3:
        return None

    A, B, C = data[0], data[1], data[2]

    return (A * 4096 + B * 64 + C) / 1000


def decode_temp_f(data):
    """
    Decode temperature from the Sentron temperature response.
    Protocol format:
        Temperature command returns bytes A B ...
    Formula:
        temperature = A*64 + B
    The returned value is divided by 10 so the result is in degrees Fahrenheit.
    """
    if len(data) < 2:
        return None

    A, B = data[0], data[1]

    return (A * 64 + B) / 10


def decode_slopes(data):
    """
    Decode slope values from the Sentron slope response.

    Returned slopes are reported as percentages for pH ranges:
        - pH 2-4
        - pH 4-7
        - pH 7-10
        - pH 10-12
    """
    if len(data) < 12:
        return None

    return {
        "pH 2-4": (data[1] * 64 + data[2]) / 10,
        "pH 4-7": (data[4] * 64 + data[5]) / 10,
        "pH 7-10": (data[7] * 64 + data[8]) / 10,
        "pH 10-12": (data[10] * 64 + data[11]) / 10,
    }


def print_raw_response(label, data):
    """
    Print raw byte values and decimal byte format for debugging.
    """
    print(f"\nRaw {label} bytes:", list(data))
    print(f"Decimal {label} bytes:", decimal_bytes(data))


# Open serial connection to the Sentron Evaluation Kit.
#
# Settings:
#   115200 baud
#   8 data bits
#   no parity
#   1 stop bit
ser = serial.Serial(
    PORT,
    BAUD,
    bytesize=8,
    parity="N",
    stopbits=1,
    timeout=TIMEOUT
)

print("Connected to:", PORT)


# Retrieve slope values once before continuous pH/temperature readout.
# Sentron slope command: 000!<CR>
slope_data = send_command(ser, b"000!\r")
print_raw_response("slope", slope_data)

slopes = decode_slopes(slope_data)
print("Decoded slopes %:", slopes)


# Retrieve pH and temperature readings repeatedly.
#
# Sentron pH command:
#   999!<CR>
#
# Sentron temperature command:
#   777!<CR>
for i in range(10):
    print(f"\n--- Reading {i + 1}/10 ---")

    ph_data = send_command(ser, b"999!\r")
    print_raw_response("pH", ph_data)

    ph = decode_ph(ph_data)

    if ph is None:
        print("Decoded pH: None")
    else:
        print("Decoded pH:", ph)

    time.sleep(1)

    temp_data = send_command(ser, b"777!\r")
    print_raw_response("temp", temp_data)

    temp_f = decode_temp_f(temp_data)

    if temp_f is None:
        print("No temperature recorded. Decoded temp = None")

    elif temp_f < 32 or temp_f > 120:
        print("Decoded temp F:", temp_f)
        print("Temperature reading looks invalid.")

    else:
        temp_c = (temp_f - 32) * 5 / 9

        print("Decoded temp F:", temp_f)
        print("Decoded temp C:", temp_c)


ser.close()
print("\nSerial closed.")
