"""
Functions:
    - Initiate calibration
    - Calibrate pH 4, pH 7, pH 10 points
    - Complete calibration (QIT)
    - Validate returned protocol byte sequences

Based on the communication protocol supplied with the
Sentron Evaluation Kit documentation.
"""

import serial
import time
import sys

# Serial port used by the Sentron USB interface.
# This device name will vary between computers and operating systems.
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

# Baud rate specified by the Sentron Evaluation Kit documentation.
BAUD = 115200

# Sentron calibration commands.
#
# Each command entry includes:
#   cmd      = command sent to the module
#   expected = expected decimal byte response
#   success  = message printed after a successful response
#   timeout  = maximum time to wait for a response, in seconds
#
# Expected byte sequences are based on the Sentron Evaluation Kit protocol.
COMMANDS = {
    "initiate": {
        "cmd": "CLR",
        "expected": "082 013 010",
        "success": "Ready for first calibration point.",
        "timeout": 10,
    },
    "4": {
        "cmd": "112",
        "expected": "002 013 010",
        "success": "pH 4 calibrated.",
        "timeout": 120,
    },
    "7": {
        "cmd": "113",
        "expected": "003 013 010",
        "success": "pH 7 calibrated.",
        "timeout": 120,
    },
    "10": {
        "cmd": "114",
        "expected": "004 013 010",
        "success": "pH 10 calibrated.",
        "timeout": 120,
    },
    "complete": {
        "cmd": "QIT",
        "expected": "084 013 010",
        "success": "Calibration completed.",
        "timeout": 10,
    },
}


def decimal_bytes(data):
    """
    Convert raw bytes returned by the Sentron module into
    zero-padded decimal byte strings.

    Example:
        b'R\\r\\n'

    becomes:
        "082 013 010"

    This format matches the response format used in the
    Sentron protocol documentation.
    """
    return " ".join(f"{b:03d}" for b in data)


def wait_for_response(ser, expected, timeout):
    """
    Wait for the Sentron module to return a response.

    Returns True if the received decimal byte sequence matches
    the expected response. Returns False if the response is
    unexpected or no response is received before the timeout.
    """
    start = time.time()

    while True:
        elapsed = int(time.time() - start)

        if ser.in_waiting:
            data = ser.read(ser.in_waiting)
            received = decimal_bytes(data)

            print("Received decimal bytes:", received)

            if received == expected:
                print("Match = yes!")
                return True
            else:
                print("Match = no!")
                return False

        if elapsed >= timeout:
            print("\nNo response received before timeout.")
            return False

        sys.stdout.write(f"\rWaiting... {elapsed}/{timeout} seconds")
        sys.stdout.flush()
        time.sleep(1)


def send_step(ser, key):
    
    info = COMMANDS[key]
    full_cmd = f"{info['cmd']}!\r".encode()

    print("Expected decimal bytes:", info["expected"])

    ser.reset_input_buffer()
    ser.write(full_cmd)
    ser.flush()

    ok = wait_for_response(
        ser,
        info["expected"],
        info["timeout"]
    )

    if ok:
        print("Result:", info["success"])
    else:
        print("Result: response missing or unexpected.")

    return ok


def show_main_menu():
 
    print("\nMenu :)")
    print("i = initiate calibration")
    print("q = complete calibration")
    print("x = exit script without completing")
    print("")
    print("--> Rinse the probe with demineralized water.")
    print("--> Place ISFET sensor and reference electrode in the first calibration buffer solution")
    print("--> pH 4, 7, or 10")


def show_calibration_menu():
    """
    Display calibration options after the calibration process
    has been initiated.
    """
    print("\nCalibration options:")
    print("4 = pH 4 calibration")
    print("7 = pH 7 calibration")
    print("10 = pH 10 calibration")
    print("q = quit calibration / complete")
    print("i = re-initiate calibration")
    print("x = exit script without completing")


# Open serial connection to the Sentron Evaluation Kit.
#
# Settings are specified by the Sentron protocol:
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
    timeout=1
)

# Tracks whether the Sentron module has been placed into
# calibration mode using the CLR command.
initiated = False

print("Sentron multi-point pH calibration!")

while True:
    if initiated:
        show_calibration_menu()
    else:
        show_main_menu()

    choice = input("\n> ").strip().lower()

    if choice == "i":
        print("\nInitiating calibration process...")

        initiated = send_step(ser, "initiate")

        if not initiated:
            print("Calibration initiation failed.")

    elif choice in ["4", "7", "10"]:
        if not initiated:
            print("You must initiate first. Initiate calibration by typing i.")
            continue

        input("Press Enter to calibrate.")
        print("--> Allow module to stabilize. This may take up to 2 minutes max.")

        send_step(ser, choice)

    elif choice == "q":
        print("\nEnding calibration process!")

        send_step(ser, "complete")
        break

    elif choice == "x":
        print("Exiting script without sending QIT.")
        break

    else:
        print("Unknown choice.")

ser.close()
print("Serial closed.")
