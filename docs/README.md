# Documentation

## Documentation Scope

This document contains setup notes, hardware references, and usage information for the Raspberry Pi and LCD interface developed for use with the Sentron ISFET pH Evaluation Kit.

For assembly instructions, communication protocol details, calibration procedures, and hardware specifications, refer to the official Sentron Evaluation Kit documentation.

---

## Hardware Setup

### LCD Assembly

* Assemble the Sequent Microsystems Six-in-One LCD Adapter Kit according to the manufacturer instructions.
* Solder the pushbuttons and rotary encoder.
* Mount the Raspberry Pi 5 and LCD display.

### Sentron Evaluation Hardware

* Connect the ISFET sensor, reference electrode, Analog Front-End, and AD Converter according to the Sentron documentation.

### Photos

#### Raspberry Pi + LCD Assembly

![Raspberry Pi and LCD assembly](images/full_system_setup_covers.png)

#### Sentron Evaluation Kit Connections

![Evaluation Kit connections](images/complete_system.png)

---

## Driver Installation

The Sentron Evaluation Kit requires installation of the appropriate VCP (Virtual COM Port) drivers.

[FTDI Virtual COM Port (VCP) Drivers](https://ftdichip.com/drivers/vcp-drivers/)

---

## Enclosures

### Raspberry Pi + LCD Enclosure

(STL link to be added)

### Sentron Front-End + ADC Holder

[Analog Front-End + ADC Holder](https://cad.onshape.com/documents/5ecbb51820f6faaca165b5f7/w/eac5ff36ebde372ce5c19050/e/d25b7e1138f7d20ba01514b2?renderMode=0&uiState=6a3afb3aa98aad16e2f25fca)

---

## macOS Interface

### Identify Serial Port

```bash
ls /dev/cu.*
```

Update the serial port variable in the Python scripts before execution.

### Calibration

Run:

```bash
python sentron_interface.py
```

Notes:

The terminal interface provides an interactive menu for:

* Multi-point pH calibration
* Real-time pH and temperature measurement
* Calibration slope retrieval

### Calibration

* Follow the prompts displayed in the terminal.
* Complete calibration using the desired buffer sequence.
* Select **q** after the final calibration point to send the **QIT** command and save the calibration.
* Calibration values are stored internally by the Sentron Evaluation Kit after completion.

### Measurement

The measurement interface supports:

* Continuous pH measurement
* Temperature display (°F/°C)
* Calibration slope retrieval
* Scrolling-list and live readout modes

According to the Sentron documentation, calibration slopes between consecutive buffer solutions should typically fall between approximately 95% and 105%. Values outside this range may indicate sensor contamination, sensor aging, or reference electrode issues.

---

## Raspberry Pi + LCD Interface

### Python Dependencies

Required packages:

```bash
pip install pyserial
pip install SMlcd
```

### LCD Library

The LCD interface was developed using the Sequent Microsystems LCD adapter library:

https://github.com/SequentMicrosystems/sm_lcd_rpi

### Serial Port Configuration

Verify that the serial port specified in `LCD_interface.py` matches the Sentron USB interface connected to the Raspberry Pi.

Example:

```bash
ls /dev/ttyUSB*
```

Update the serial port variable if necessary before execution.

### Run

```bash
python lcd_interface.py
```

The LCD interface provides:

* Guided calibration workflow
* pH measurement
* Temperature measurement
* Calibration slope retrieval
* Rotary encoder menu navigation

Follow the instructions displayed on the LCD screen.
