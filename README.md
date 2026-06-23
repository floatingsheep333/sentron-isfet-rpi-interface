# Sentron ISFET pH Evaluation Kit Raspberry Pi Interface

## Overview

This repository contains software, hardware designs, and supporting documentation developed for interfacing the Sentron ISFET pH Evaluation Kit with a Raspberry Pi 5.

The project includes terminal-based and LCD-based interfaces for calibration and measurement, protocol decoding for pH, temperature, and slope retrieval, and supporting enclosure designs.

## Features

* Serial communication with the Sentron ISFET Evaluation Kit
* Protocol decoding for pH, temperature, and slope values
* Terminal-based calibration workflow
* Terminal-based measurement interface
* LCD-based user interface with rotary encoder navigation
* Embedded Raspberry Pi 5 operation
* Supporting enclosure and mounting hardware designs

## Hardware

* Raspberry Pi 5
* Sentron R&D pH Evaluation Kit

  * Analog Front-End
  * AD Converter
  * ISFET pH Sensor + Reference Electrode
  * USB Interface
* Sequent Microsystems Six-in-One LCD Adapter Kit (2004 or 1602 LCD Display)

---

## Repository Contents

### code/calibration_terminal.py

Terminal-based calibration workflow implementing the Sentron calibration protocol.

### code/readout_terminal.py

Terminal-based interface for retrieving and decoding pH, temperature, and calibration slope values.

### code/lcd_interface.py

LCD-based interface featuring rotary encoder navigation, guided calibration workflows, and real-time measurement display.

### docs/

Setup notes, hardware references, photos, and usage documentation.

### stl/

3D-printable enclosure and mounting components.

---

## Future Work

* Characterization curves for ionic strength effects on pH readings
* Data logging and export functionality
* Measurement history and trend visualization
* Additional sensor characterization tools

## Notes

This repository is intended as a companion software interface for the Sentron ISFET pH Evaluation Kit.

The implementation is based on the communication protocol and documentation supplied with the evaluation hardware.
