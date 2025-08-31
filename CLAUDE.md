# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **TRITON** project - an autonomous submarine navigation system that evolved from the original CanSat (satellite simulation) project. TRITON collects sensor data from BME280 (environmental) and MPU6050 (inertial measurement) sensors using a dual-platform architecture:

- **Raspberry Pi**: Runs sensor data collection and LoRa transmission
- **PC**: Handles data reception, logging, and real-time web dashboard

The system includes data logging, real-time web visualization, LoRa communication, and statistical analysis capabilities.

## Development Environment Setup

**Python Dependencies:**
- `adafruit-circuitpython-bme280` - BME280 sensor interface
- `mpu6050-raspberrypi` - MPU6050 sensor interface  
- `numpy` - Numerical calculations
- `flask` - Web server for dashboard
- `pyserial` - Serial communication for LoRa
- `requests` - HTTP requests for web updates
- `pytz` - Timezone handling

**Hardware Requirements:**
- Raspberry Pi Zero 2 W (or compatible)
- BME280 environmental sensor (I2C address 0x76)
- MPU6050 inertial measurement unit (I2C address 0x68)
- LoRa modules (sender on Pi, receiver on PC)
- LoRa serial connection on /dev/ttyUSB0 at 9600 baud

## Active Files Structure

### Currently Used Files

**Raspberry Pi (Data Collection & Transmission):**
- `test.py` - Main sensor data collection script with LoRa transmission and web updates
- `lorasendertest.py` - LoRa transmission testing and basic functionality

**PC (Data Reception & Dashboard):**
- `lorareceivertest.py` - LoRa data reception with logging, statistics, and web integration
- `app.py` - Flask web server with real-time dashboard and data visualization
- `web_server.py` - Alternative Flask server implementation with CSV download functionality

**Templates:**
- `templates/dashboard.html` - Real-time web dashboard with Chart.js visualizations

### Legacy Files

All legacy/obsolete files have been moved to `src/legacy/` for reference:
- Original CanSat implementations (`main.py`, `maincollector*.py`)
- Old sensor modules (`bme280sensor.py`, `MPU6050.py`, etc.)
- Previous communication modules (`lora.py`, `lorav5.py`, etc.)
- Development utilities (`Stopwatch.py`, `performance.py`, etc.)
- Test files (`combitest.py`, `packtest.py`, etc.)

## Common Commands

**On Raspberry Pi:**
```bash
python src/test.py              # main sensor collection with LoRa
python src/lorasendertest.py    # test LoRa transmission
```

**On PC:**
```bash
python src/lorareceivertest.py  # receive LoRa data with logging
python src/app.py               # run web dashboard server
python src/web_server.py        # alternative web server
```

**Access Web Dashboard:**
- Open browser to `http://localhost:5000` (or `http://[PC_IP]:5000` from other devices)
- Real-time data visualization with statistics
- CSV download functionality available

## System Architecture

**Data Flow:**
1. **Raspberry Pi** (`test.py`) collects sensor data and transmits via LoRa
2. **PC** (`lorareceivertest.py`) receives LoRa data and logs to CSV
3. **Web Server** (`app.py`) provides real-time dashboard with statistics
4. **Dashboard** updates automatically with live sensor readings

**Dual Platform Setup:**
- **Raspberry Pi**: Autonomous sensor data collection and wireless transmission
- **PC**: Data reception, logging, analysis, and web-based monitoring

## Data Format

**Sensor Array Structure (12 elements):**
- [0] - Elapsed time [s]
- [1] - BME280 Temperature [°C] 
- [2] - BME280 Humidity [%]
- [3] - BME280 Pressure [hPa]
- [4] - BME280 Altitude [m]
- [5] - MPU6050 Acceleration X [m/s²]
- [6] - MPU6050 Acceleration Y [m/s²] 
- [7] - MPU6050 Acceleration Z [m/s²]
- [8] - MPU6050 Gyro X [°/s]
- [9] - MPU6050 Gyro Y [°/s]
- [10] - MPU6050 Gyro Z [°/s]
- [11] - MPU6050 Temperature [°C]

**CSV Output:**
- Files saved to `logs/sensor_data_YYYYMMDD_HHMMSS.csv` with MET timestamps
- Automatic archiving of old logs to `logs/previous_data/`
- Min/Max statistics appended on graceful shutdown

**Data Transmission Thresholds:**
- Temp BME280: 0.25°C
- Humidity: 1.0%  
- Pressure: 0.5 hPa
- Altitude: 0.5m
- Acceleration: 0.25 m/s² all axes
- Gyroscope: 5.0°/s all axes  
- Temp MPU: 0.25°C

## Key Configuration

**BME280 Settings:**
- Sea level pressure: 993.9 hPa (adjust for location)
- I2C address: 0x76

**MPU6050 Settings:**
- Gyro range: ±2000°/s
- Accelerometer range: ±16g  
- I2C address: 0x68

**LoRa Settings:**
- Raspberry Pi: /dev/ttyUSB0
- PC: COM8 (adjust as needed)
- Baud rate: 9600
- Timeout: 1.0s

**Web Server:**
- Host: 0.0.0.0 (accessible from network)
- Port: 5000
- Update frequency: ~1 second
- History: Last 300 data points per metric

## Development Notes

- **Error Handling**: All sensor modules include comprehensive error handling and continue operation on sensor failures
- **Data Validation**: Threshold-based data transmission reduces network overhead
- **Statistics**: Real-time min/max/average calculations with web display
- **Graceful Shutdown**: Ctrl+C saves summary statistics to log files
- **Hardware Fallback**: Sensors fall back to error messages when hardware is unavailable
- **Raspberry Pi Setup**: Requires I2C enabled via `raspi-config`
- **File Organization**: Legacy code preserved in `src/legacy/` for reference

## Web Interface Features

### Theme Selector Implementation ✅ COMPLETED
**Status**: Both homepage and dashboard have fully functional dropdown theme selectors

**Implementation Details**:
- **Location**: Theme dropdown is located inside `<nav class="main-nav">` on both pages
- **Structure**: Uses `display: inline-block` positioning (NOT absolute positioning)
- **Font Color**: Dropdown options use `color: #ffffff !important` for white text
- **Themes Available**: Dark Ocean, Night, Light Ocean
- **Functionality**: Click-to-toggle, click-outside-to-close, theme persistence via localStorage
- **Mobile Responsive**: Proper mobile styles with adjusted widths and padding

**Critical Implementation Notes**:
- Theme selector MUST be inside navigation structure to be visible
- Absolute positioning causes visibility issues with fixed navigation
- Z-index conflicts resolved by using inline-block within nav
- Both pages use identical CSS and JavaScript for consistency

**Files Modified**:
- `src/templates/index.html` (homepage)
- `src/templates/dashboard.html` (dashboard)

**Verification**: Theme dropdowns are visible in top navigation bar on both pages with white font text

## TRITON Mission Notes

The TRITON system is designed for autonomous submarine operations with:
- Continuous environmental monitoring (pressure for depth calculation)
- Inertial navigation capability (accelerometer + gyroscope)
- Wireless data transmission for real-time monitoring
- Comprehensive data logging for post-mission analysis
- Web-based mission control interface