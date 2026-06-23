# Sentron ISFET pH Evaluation Kit Raspberry Pi Interface

## Overview

This repository contains software, hardware designs, and documentation developed for a Raspberry Pi 5 interface to the Sentron ISFET pH Evaluation Kit.

Project components include pH measurement and calibration software, an LCD-based user interface, protocol decoding, and custom hardware enclosures. The software provides terminal-based and LCD-based workflows for calibration and measurement, including retrieval of pH, temperature, and slope values from the evaluation hardware.

## Features

* Serial communication with the Sentron ISFET Evaluation Kit
* Protocol decoding for pH, temperature, and slope values
* Terminal-based calibration workflow
* Terminal-based measurement interface
* LCD menu system with rotary encoder navigation
* Embedded Raspberry Pi 5 interface for calibration and measurement operations
* Custom hardware enclosure designs

## Hardware

* Raspberry Pi 5
* Sentron R&D pH Evaluation Kit

  * Analog Front-End
  * AD Converter
  * ISFET pH Sensor + Reference Electrode
  * USB Interface
* Sequent Microsystems Six-in-One LCD Adapter Kit (2004 or 1602 LCD Display)

## Repository Contents

### calibration_terminal.py

Terminal-based calibration workflow implementing the Sentron calibration protocol.

### readout_terminal.py

Terminal-based interface for retrieving and decoding pH, temperature, and slope values.

### lcd_interface.py

LCD-based user interface featuring menu navigation, calibration workflows, and real-time measurement display.

### docs/

Project notes, workflow diagrams, setup information, and documentation.

### stl/

3D-printable enclosure files and hardware accessories.

## Future Work

* Characterization curves for ionic strength effects on pH readings
* Data logging
* Measurement history and analysis

## Notes

This repository is intended as a companion software interface for the Sentron ISFET pH Evaluation Kit.

The implementation is based on the communication protocol and documentation supplied with the evaluation hardware.
