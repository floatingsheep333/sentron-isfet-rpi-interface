"""

This script provides an LCD-based user interface for operating the
Sentron ISFET pH Evaluation Kit using a Raspberry Pi 5 and the
Sequent Microsystems Six-in-One LCD Adapter Kit.

Controls:
SW1 = Calibration menu
SW2 = Read pH / temperature
SW4 = Select / Continue
SW5 = Back
SW6 = Shut down interface

Based on the communication protocol supplied with the
Sentron Evaluation Kit documentation.
"""


import sm_lcd
import time
import serial
import sys

# -----------------------
# SETTINGS
# -----------------------

# Serial port used by the Sentron USB interface.
# This device name may vary between computers and operating systems.
#
# Raspberry Pi / Linux:
#   /dev/ttyUSB0
#
# macOS:
#   /dev/cu.usbserial-XXXXXXXX

PORT = "/dev/ttyUSB0"

BAUD = 115200

lcd = sm_lcd.SMlcd()

# -----------------------
# SENTRON CALIBRATION COMMANDS
# -----------------------

# Sentron calibration commands and expected responses.
#
# Each command consists of:
#   cmd      = command sent to the Sentron module
#   expected = expected decimal byte response
#   success  = LCD message displayed after successful completion
#   timeout  = maximum wait time in seconds

COMMANDS = {
    "initiate": {
        "cmd": "CLR",
        "expected": "082 013 010",
        "success": "Ready for first pt",
        "timeout": 10,
    },
    "4": {
        "cmd": "112",
        "expected": "002 013 010",
        "success": "pH 4 calibrated",
        "timeout": 120,
    },
    "7": {
        "cmd": "113",
        "expected": "003 013 010",
        "success": "pH 7 calibrated",
        "timeout": 120,
    },
    "10": {
        "cmd": "114",
        "expected": "004 013 010",
        "success": "pH 10 calibrated",
        "timeout": 120,
    },
    "complete": {
        "cmd": "QIT",
        "expected": "084 013 010",
        "success": "Calibration done",
        "timeout": 10,
    },
}

# -----------------------
# LCD HELPER FUNCTIONS
# -----------------------

def clear():
    lcd.cmd(0x01)          # clear LCD text
    lcd.display_init()     # fixes ghost/leftover characters on LCD
    time.sleep(0.1)

def write_line(line, text):
    lcd.text_write_at(line, 1, " " * 20)     # erase line
    lcd.text_write_at(line, 1, text[:20])    # write max 20 chars

def show_startup_menu():
    clear()
    write_line(1, "-- pH Sensor Menu --")
    write_line(2, "~SW1 Calibrate")
    write_line(3, "~SW2 Read pH")
    write_line(4, "~SW6 Off")

def turn_off():
    clear()
    write_line(1, "Turning off...")
    time.sleep(1)
    clear()
    lcd.cmd(0x08)      # display OFF
    lcd.bl_single(0)   # backlight OFF

# -----------------------
# SERIAL FUNCTIONS
# -----------------------

def open_serial():
    return serial.Serial(
        PORT,
        BAUD,
        bytesize=8,
        parity="N",
        stopbits=1,
        timeout=1
    )

def decimal_bytes(data):
    # Example: b'R\r\n' -> "082 013 010"
    return " ".join(f"{b:03d}" for b in data)

def send_cal_step(ser, key):
    info = COMMANDS[key]

    # Example: "CLR" becomes b"CLR!\r"
    full_cmd = f"{info['cmd']}!\r".encode()

    clear()
    write_line(1, "Sending command")
    write_line(2, full_cmd.decode().strip())
    write_line(3, "Waiting...")
    write_line(4, "~SW6 Off")

    # for debugging
    print("Sending:", full_cmd)
    print("Expected:", info["expected"])

    ser.reset_input_buffer()
    ser.write(full_cmd)
    ser.flush()

    start = time.time()

    while True:
        elapsed = int(time.time() - start)

        if ser.in_waiting:
            data = ser.read(ser.in_waiting)
            received = decimal_bytes(data)

            print("Received:", received)

            clear()

            if received == info["expected"]:

                # Special screen after initiating calibration
                if key == "initiate":
                    write_line(1, "Ready 1st point")
                    write_line(2, "Choose pH 4/7/10")
                    write_line(3, " ")
                    write_line(4, "~SW4 Continue")

                    while True:
                        if lcd.get_button(4) == 1:
                            time.sleep(0.3)
                            return True

                        if lcd.get_button(6) == 1:
                            turn_off()
                            ser.close()
                            sys.exit()

                        time.sleep(0.05)

                # Normal success screen for pH 4, 7, 10, complete
                else:
                    write_line(1, "Success!")
                    write_line(2, info["success"])
                    write_line(4, "~SW4 Continue")
                    #write_line(4, "SW5 Back") 

                    while True:
                        if lcd.get_button(4) == 1:
                            time.sleep(0.3)
                            return True  

                        if lcd.get_button(5) == 1:
                            time.sleep(0.3)
                            return True  

                        if lcd.get_button(6) == 1:
                            turn_off()
                            sys.exit()

                        time.sleep(0.05)

            else:
                write_line(1, "Unexpected resp")
                write_line(2, received[:20])
                write_line(3, "Expected:")
                write_line(4, info["expected"][:20])
                wait_for_back()
                return False

        write_line(3, f"Waiting {elapsed}s")

        if lcd.get_button(6) == 1:
            turn_off()
            ser.close()
            sys.exit()

        if elapsed >= info["timeout"]:
            clear()
            write_line(1, "Timeout")
            write_line(2, "No response")
            write_line(4, "~SW5 Back")
            wait_for_back()
            return False

        time.sleep(1)

# -----------------------
# BUTTON WAIT HELPERS
# -----------------------

def wait_for_back():
    while True:
        if lcd.get_button(5) == 1:
            time.sleep(0.3)
            return

        if lcd.get_button(6) == 1:
            turn_off()
            sys.exit()

        time.sleep(0.05)

def wait_confirm_or_back():
    while True:
        if lcd.get_button(4) == 1:
            time.sleep(0.3)
            return True

        if lcd.get_button(5) == 1:
            time.sleep(0.3)
            return False

        if lcd.get_button(6) == 1:
            turn_off()
            sys.exit()

        time.sleep(0.05)

# -----------------------
# CALIBRATION SCREENS
# -----------------------

def calibration_intro():
    clear()
    write_line(1, "Place ISFET+Ref")
    write_line(2, "in first buffer")
    write_line(3, "~SW4 Continue")
    write_line(4, "SW5 Back  SW6 Off")

    while True:

        if lcd.get_button(4) == 1:
            time.sleep(0.3)
            return True

        if lcd.get_button(5) == 1:
            time.sleep(0.3)
            return False

        if lcd.get_button(6) == 1:
            turn_off()
            sys.exit()

        time.sleep(0.05)

def confirm_ph_calibration(ser, ph_value):
    clear()
    write_line(1, f"Place in pH {ph_value}")
    write_line(2, " ")
    write_line(3, "~SW4 start cal")
    write_line(4, "~SW5 Back")

    if wait_confirm_or_back():
        send_cal_step(ser, ph_value)

def exit_without_qit(ser):
    clear()
    write_line(1, "Exit without QIT?")
    write_line(2, "Cal not completed")
    write_line(3, "~SW4 Yes")
    write_line(4, "~SW5 Back")

    if wait_confirm_or_back():
        clear()
        write_line(1, "Exiting script")
        #write_line(2, "No QIT sent")
        time.sleep(1)
        ser.close()
        turn_off()
        sys.exit()

def complete_calibration(ser):
    clear()
    write_line(1, "Complete calibration?")
    #write_line(2, "Sends QIT")
    write_line(3, "~SW4 Yes")
    write_line(4, "~SW5 Back")

    if wait_confirm_or_back():
        return send_cal_step(ser, "complete")

    return False

# -----------------------
# ROTARY MENU FUNCTION
# -----------------------

def rotary_select_menu(title, options):
    """
    Uses rotary encoder to choose from options.
    SW4 selects.
    SW5 goes back.
    SW6 shuts off.
    """

    clear()
    lcd.reset_encoder()

    selected = 0
    last_selected = None

    while True:
        encoder_val = lcd.get_encoder_val()

        # % keeps selected inside option list range
        selected = encoder_val % len(options)

        if selected != last_selected:
            clear()
            write_line(1, title)
            write_line(2, "> " + options[selected])
            write_line(3, "Rotary choose")
            write_line(4, "~SW4 Sel ~SW5 Back")
            last_selected = selected

        if lcd.get_button(4) == 1:
            time.sleep(0.3)
            return selected

        if lcd.get_button(5) == 1:
            time.sleep(0.3)
            return None

        if lcd.get_button(6) == 1:
            turn_off()
            sys.exit()

        time.sleep(0.05)

# -----------------------
# FULL CALIBRATION MENU
# -----------------------

def calibration_menu(ser):
    initiated = False

    if not calibration_intro():
        show_startup_menu()
        return

    # ------------------------
    # CALIBRATION WHILE LOOP
    # ------------------------
    while True:
        if initiated:
            # Same idea as original show_calibration_menu()
            options = [
                "Cal pH 4",
                "Cal pH 7",
                "Cal pH 10",
                "Complete QIT",
                "Re-initiate",
                "Exit no QIT",
            ]
        else:
    
            options = [
                "Initiate cal",
                "Exit no QIT",
            ]

        choice = rotary_select_menu("Calibration", options)

        if choice is None:
            show_startup_menu()
            return

        selected_text = options[choice]

        if selected_text == "Initiate cal":
            ok = send_cal_step(ser, "initiate")
            if ok:
                initiated = True

        elif selected_text == "Re-initiate":
            ok = send_cal_step(ser, "initiate")
            if ok:
                initiated = True

        elif selected_text == "Cal pH 4":
            confirm_ph_calibration(ser, "4")

        elif selected_text == "Cal pH 7":
            confirm_ph_calibration(ser, "7")

        elif selected_text == "Cal pH 10":
            confirm_ph_calibration(ser, "10")

      # QIT finalizes the calibration process and stores calibration data
      # on the Sentron evaluation hardware.
      
        elif selected_text == "Complete QIT":
            completed = complete_calibration(ser)
            if completed:
                show_startup_menu()
                return

        elif selected_text == "Exit no QIT":
            exit_without_qit(ser)

# -----------------------
# pH READ SCREEN
# -----------------------

# Decode pH using the formula defined in the Sentron protocol:
# pH = (A*4096 + B*64 + C) / 1000

def decode_ph(data):
    if len(data) < 3:
        return None

    A, B, C = data[0], data[1], data[2]
    return (A * 4096 + B * 64 + C) / 1000

# Decode temperature using the formula defined in the Sentron protocol:
# Temperature (°F) = (A*64 + B) / 10

def decode_temp_f(data):
    if len(data) < 2:
        return None

    A, B = data[0], data[1]
    return (A * 64 + B) / 10

def send_read_command(ser, command):
    ser.reset_input_buffer()
    ser.write(command)
    ser.flush()
    return ser.read_until(b"\r\n")

def read_ph_screen(ser):
    clear()
    write_line(1, "Reading pH...")
    write_line(4, "~SW5 Back ~SW6 Off")

    while True:
        ph_data = send_read_command(ser, b"999!\r")
        ph = decode_ph(ph_data)

        temp_data = send_read_command(ser, b"777!\r")
        temp_f = decode_temp_f(temp_data)

        #Display pH reading
        if ph is None:
            write_line(2, "pH: no data")
        else:
            write_line(2, f"pH: {ph:.3f}")

        #Display temperature in Fahrenheit
        if temp_f is None:
            write_line(3, "Temp: no data")

        else:
            write_line(3, f"Temp:{temp_f:.1f}F")



        if lcd.get_button(5) == 1:
            time.sleep(0.3)
            show_startup_menu()
            return

        if lcd.get_button(6) == 1:
            turn_off()
            ser.close()
            sys.exit()

        time.sleep(1)

# -----------------------
# MAIN PROGRAM LOOP
# -----------------------

lcd.display_init()
lcd.cmd(0x0C)
lcd.bl_single(50)
show_startup_menu()

try:
    ser = open_serial()
    print("Connected to:", PORT)

    while True:
        if lcd.get_button(1) == 1:
            time.sleep(0.3)
            calibration_menu(ser)

        elif lcd.get_button(2) == 1:
            time.sleep(0.3)
            read_ph_screen(ser)

        elif lcd.get_button(5) == 1:
            time.sleep(0.3)
            show_startup_menu()

        elif lcd.get_button(6) == 1:
            turn_off()
            break

        time.sleep(0.05)

except Exception as e:
    print("Error:", e)
    clear()
    write_line(1, "Error")
    write_line(2, str(e)[:20])
    write_line(4, "Check terminal")

finally:
    try:
        ser.close()
        print("Serial closed.")
    except:
        pass
