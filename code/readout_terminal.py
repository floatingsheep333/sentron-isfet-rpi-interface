"""
Sentron ISFET pH + Temperature Readout
"""
"""

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
import sys

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
BAUD = 115200


RESET = "\033[0m"
BOLD = "\033[1m"

CYAN = "\033[96m"
WHITE = "\033[97m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"

LINE = "─" * 60
THICK_LINE = "═" * 60


def title(text):
    print(f"\n{BOLD}{CYAN}{THICK_LINE}")
    print(text.center(60))
    print(f"{THICK_LINE}{RESET}\n")


def section(text):
    print(f"\n{BOLD}{CYAN}{LINE}")
    print(text)
    print(f"{LINE}{RESET}")


def decimal_bytes(data):
    """
    Convert raw bytes returned by the Sentron module into
    zero-padded decimal byte strings.
    """
    return " ".join(f"{b:03d}" for b in data)


def decode_ph(data):
    """
    Decode pH from the Sentron pH response.
    Protocol format:
        pH command returns bytes A B C D E F G H I J K
        pH = A*4096 + B*64 + C, units = 0.001 pH
    """
    if len(data) < 3:
        return None
    A, B, C = data[0], data[1], data[2]
    return (A * 4096 + B * 64 + C) / 1000 #(Units 1.0 pH now)


def decode_temp_f(data):
    # temp command returns A B C D E F G
    # temp = A*64 + B, (units 0.1 F)

    if len(data) < 2:
        return None
    A, B = data[0], data[1]
    return (A * 64 + B) / 10 #(units now 1.0 F)

def f_to_c(temp_f):
    return (temp_f - 32) * 5 / 9


def decode_slopes(data):
    if len(data) < 12:
        return None

    return {
        "pH 2-4": (data[1] * 64 + data[2]) / 10,
        "pH 4-7": (data[4] * 64 + data[5]) / 10,
        "pH 7-10": (data[7] * 64 + data[8]) / 10,
        "pH 10-12": (data[10] * 64 + data[11]) / 10,
    }


def read_command(ser, command):
    """
    Send a command to the Sentron module and return the raw response.
    """
    ser.reset_input_buffer() #clear old leftover bytes before asking for new value
    ser.write(command)
    ser.flush()
    return ser.read_until(b"\r\n")


def read_ph(ser):
    data = read_command(ser, b"999!\r")

    # Uncomment for troubleshooting:
    # print("pH decimal bytes:", decimal_bytes(data))

    return decode_ph(data), data


def read_temp(ser):
    data = read_command(ser, b"777!\r")

    # Uncomment for troubleshooting:
    # print("Temperature decimal bytes:", decimal_bytes(data))

    temp_f = decode_temp_f(data)

    if temp_f is None:
        return None, None, data

    temp_c = f_to_c(temp_f)
    return temp_f, temp_c, data


def read_slopes(ser):
    data = read_command(ser, b"000!\r")
    slopes = decode_slopes(data)

    section("SLOPE VALUES")

    print(f"{WHITE}• Slopes are calculated between consecutive calibration points.{RESET}")
    print(f"{WHITE}• A slope of {MAGENTA}0%{RESET} indicates fewer than two calibration points for that pH range.{RESET}")
    print(f"{WHITE}• Normal slopes are {MAGENTA}95–105%{RESET}; values outside this range may indicate sensor or reference electrode contamination or aging.{RESET}\n")

    #print(f"{WHITE}• Decimal bytes:{RESET} {YELLOW}{decimal_bytes(data)}{RESET}\n")

    if slopes is None:
        print(f"{MAGENTA}Could not decode slope values.{RESET}\n")
        return

    print(f"{WHITE}pH 2-4:    {RESET}{MAGENTA}{slopes['pH 2-4']:.1f}%{RESET}")
    print(f"{WHITE}pH 4-7:    {RESET}{MAGENTA}{slopes['pH 4-7']:.1f}%{RESET}")
    print(f"{WHITE}pH 7-10:   {RESET}{MAGENTA}{slopes['pH 7-10']:.1f}%{RESET}")
    print(f"{WHITE}pH 10-12:  {RESET}{MAGENTA}{slopes['pH 10-12']:.1f}%{RESET}\n")


def format_reading(count, ph, temp_f, temp_c):
    count_text = f"{WHITE}{count:04d}{RESET}"

    if ph is None:
        ph_text = f"{WHITE}pH:{RESET} {MAGENTA}---{RESET}"
    else:
        ph_text = f"{WHITE}pH:{RESET} {YELLOW}{ph:.3f}{RESET}"

    if temp_f is None or temp_c is None:
        temp_text = f"{WHITE}Temp:{RESET} {MAGENTA}---{RESET}"
    else:
        temp_text = (
            f"{WHITE}Temp:{RESET} "
            f"{YELLOW}{temp_f:.1f} °F{RESET}  "
            f"{MAGENTA}{temp_c:.1f} °C{RESET}"
        )

    return f"{count_text}     {ph_text}        {temp_text}"


def continuous_list_mode(ser):
    section("SCROLLING LIST")

    print(f"{WHITE}Each reading prints on a new line.{RESET}")
    print(f"{WHITE}Press Ctrl+C to stop.{RESET}\n")

    count = 1

    while True:
        ph, ph_data = read_ph(ser)
        temp_f, temp_c, temp_data = read_temp(ser)

        print(format_reading(count, ph, temp_f, temp_c))

        count += 1
        time.sleep(1)


def continuous_update_mode(ser):
    section("LIVE READOUT")

    print(f"{WHITE}Press Ctrl+C to stop.{RESET}\n")

    count = 1

    while True:
        ph, ph_data = read_ph(ser)
        temp_f, temp_c, temp_data = read_temp(ser)

        line = format_reading(count, ph, temp_f, temp_c)

        sys.stdout.write("\r" + line + " " * 20)
        sys.stdout.flush()

        count += 1
        time.sleep(1)


try:
    ser = serial.Serial(
        PORT,
        BAUD,
        bytesize=8,
        parity="N",
        stopbits=1,
        timeout=2
    )
    # Baudrate=115200, AD Converter module: 8N1

    title("SENTRON ISFET READOUT")

    print(f"{WHITE}Connected port:{RESET} {YELLOW}{PORT}{RESET}")
    #print(f"{WHITE}Baud rate:{RESET}      {YELLOW}{BAUD}{RESET}\n")

    read_slopes(ser)

    section("READOUT MODE")

    print(f"{YELLOW}1{RESET}  Scrolling list")
    print(f"   {WHITE}Prints each pH/temperature reading on a new line.{RESET}\n")

    print(f"{YELLOW}2{RESET}  Live single-line display")
    print(f"   {WHITE}Updates the same line continuously.{RESET}\n")

    mode = input(f"{BOLD}{CYAN}> {RESET}").strip()

    if mode == "1":
        continuous_list_mode(ser)

    elif mode == "2":
        continuous_update_mode(ser)

    else:
        print(f"{MAGENTA}Unknown mode.{RESET}")

except KeyboardInterrupt:
    print(f"\n{MAGENTA}Stopped by user.{RESET}")

except serial.SerialException as e:
    print(f"{MAGENTA}Could not open serial connection.{RESET}")
    print(e)

finally:
    try:
        ser.close()
        print(f"{MAGENTA}Serial closed.{RESET}")
    except NameError:
        pass
