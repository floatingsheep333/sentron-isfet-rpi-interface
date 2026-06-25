"""
Sentron ISFET Multi-Point pH Calibration
"""

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


# =========================
# FORMATTING
# =========================

RESET = "\033[0m"
BOLD = "\033[1m"

CYAN = "\033[96m"
WHITE = "\033[97m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"

LINE = "─" * 60
THICK_LINE = "═" * 60


# =========================
# SENTRON COMMANDS
# =========================

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
        "timeout": 10,
    },
    "4": {
        "cmd": "112",
        "expected": "002 013 010",
        "timeout": 120,
    },
    "7": {
        "cmd": "113",
        "expected": "003 013 010",
        "timeout": 120,
    },
    "10": {
        "cmd": "114",
        "expected": "004 013 010",
        "timeout": 120,
    },
    "complete": {
        "cmd": "QIT",
        "expected": "084 013 010",
        "timeout": 10,
    },
}


# =========================
# DISPLAY HELPERS
# =========================

def title(text):
    print(f"\n{BOLD}{CYAN}{THICK_LINE}")
    print(text.center(60))
    print(f"{THICK_LINE}{RESET}\n")


def section(text):
    print(f"\n{BOLD}{CYAN}{LINE}")
    print(text)
    print(f"{LINE}{RESET}")


def operation(text):
    print(f"\n{CYAN}{text}{RESET}\n")


def success(text):
    print(f"{MAGENTA}✓ {text}{RESET}")


def warning(text):
    print(f"{MAGENTA}✗ {text}{RESET}")


def decimal_bytes(data):
    """
    Convert raw bytes returned by the Sentron module into
    zero-padded decimal byte strings.
    """
    return " ".join(f"{b:03d}" for b in data)


# =========================
# SCREENS
# =========================

def startup_screen():
    title("SENTRON ISFET pH CALIBRATION")
    print(f"{WHITE}Serial connection opened{RESET}")
    print(f"{WHITE}Port:{RESET}      {YELLOW}{PORT}{RESET}")
    print(f"{WHITE}Baud rate:{RESET} {YELLOW}{BAUD}{RESET}\n")


def show_setup_screen():
    section("CALIBRATION SETUP")

    print(f"{WHITE}• Rinse the probe with demineralized water.{RESET}")
    print(f"{WHITE}• Place ISFET sensor and reference electrode in the first calibration buffer solution.{RESET}")
    print(f"{WHITE}• For 2-point calibration: pH 4→7 or pH 7→10.{RESET}")
    print(f"{WHITE}  For 3-point calibration: pH 4→7→10 or pH 10→7→4.{RESET}\n")


def show_main_menu():
    section("MAIN MENU")

    print(f"{WHITE}i{RESET}    Initiate calibration mode")
    print(f"{WHITE}q{RESET}    Complete calibration and save")
    print(f"{WHITE}x{RESET}    Exit without completing calibration")
    print()


def show_calibration_menu():
    section("CALIBRATION MENU")

    print(f"{WHITE}4{RESET}     pH 4 calibration")
    print(f"{WHITE}7{RESET}     pH 7 calibration")
    print(f"{WHITE}10{RESET}    pH 10 calibration")
    print(f"{WHITE}q{RESET}     End calibration and save")
    print(f"{WHITE}x{RESET}     Exit without saving")
    print()


def buffer_instruction(choice):
    operation(f"pH {choice} calibration")

    print(f"{WHITE}Confirm ISFET sensor and reference electrode are in pH {choice} buffer.{RESET}\n")
    input(f"{CYAN}Press Enter to send pH {choice} command...{RESET}")


# =========================
# SERIAL FUNCTIONS
# =========================

def wait_for_response(ser, expected, timeout):
    start = time.time()

    while True:
        elapsed = int(time.time() - start)

        if ser.in_waiting:
            data = ser.read(ser.in_waiting)
            received = decimal_bytes(data)

            print()
            print(f"{WHITE}Received:{RESET}   {YELLOW}{received}{RESET}")

            if received == expected:
                print(f"{WHITE}Verify:{RESET}     {MAGENTA}✓ PASSED{RESET}\n")
                return True
            else:
                print(f"{WHITE}Verify:{RESET}     {MAGENTA}✗ FAILED{RESET}")
                print(f"{WHITE}Expected:{RESET}   {YELLOW}{expected}{RESET}\n")
                return False

        if elapsed >= timeout:
            print()
            warning("No response received before timeout.")
            return False

        sys.stdout.write(
            f"\r{WHITE}Waiting...{RESET}  {MAGENTA}{elapsed}/{timeout} s{RESET}"
        )
        sys.stdout.flush()
        time.sleep(1)


def send_step(ser, key):
    info = COMMANDS[key]
    full_cmd = f"{info['cmd']}!\r".encode()

    if key == "initiate":
        operation("Starting calibration...")
    elif key == "complete":
        operation("Ending calibration...")
    else:
        operation(f"Starting pH {key} calibration...")

    print(f"{WHITE}Command:{RESET}    {YELLOW}{info['cmd']}!<CR>{RESET}")
    print(f"{WHITE}Expected:{RESET}   {YELLOW}{info['expected']}{RESET}")
    print(f"{WHITE}Timeout:{RESET}    {MAGENTA}{info['timeout']} s{RESET}\n")

    ser.reset_input_buffer()
    ser.write(full_cmd)
    ser.flush()

    if key in ["4", "7", "10"]:
        print(f"{WHITE}Allow time for the module to stabilize.{RESET}")
        print(f"{WHITE}This may take up to 2 minutes maximum.{RESET}\n")

    ok = wait_for_response(
        ser,
        info["expected"],
        info["timeout"]
    )

    if ok:
        if key == "initiate":
            success("Calibration mode active.")
        elif key == "complete":
            success("Calibration completed.")
        else:
            success(f"pH {key} calibration completed.")
    else:
        warning("Protocol verification failed.")

    print()
    return ok


# =========================
# MAIN
# =========================

try:
    ser = serial.Serial(
        PORT,
        BAUD,
        bytesize=8,
        parity="N",
        stopbits=1,
        timeout=1
    )

    initiated = False

    startup_screen()
    show_setup_screen()

    while True:
        if initiated:
            show_calibration_menu()
        else:
            show_main_menu()

        choice = input(f"{BOLD}{CYAN}> {RESET}").strip().lower()

        if choice == "i":
            initiated = send_step(ser, "initiate")

        elif choice in ["4", "7", "10"]:
            if not initiated:
                warning("Send CLR first.")
                continue

            buffer_instruction(choice)
            send_step(ser, choice)

        elif choice == "q":
            send_step(ser, "complete")
            break

        elif choice == "x":
            warning("Exited without QIT.")
            break

        else:
            warning("Unknown command.")

except serial.SerialException as e:
    warning("Could not open serial connection.")
    print(e)

finally:
    try:
        ser.close()
        print()
        success("Serial connection closed.")
    except NameError:
        pass
