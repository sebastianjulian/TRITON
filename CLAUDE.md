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

**Raspberry Pi (Data Collection, Motor Control & Transmission):**
- `test.py` - **Main unified script**: sensor collection, LoRa transmission, motor command reception, and ESC control
- `lorasendertest.py` - LoRa transmission testing and basic functionality

**PC (Data Reception, Motor Commands & Dashboard):**
- `app.py` - Flask web server with dashboard, motor control UI, and continuous LoRa command transmission
- `lorareceivertest.py` - LoRa data reception with logging, statistics, and web integration
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
- `pi_motor_receiver.py` - Standalone motor receiver (now merged into `test.py`)

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

## Motor Control System

### Overview

TRITON includes brushless motor control via ESC (Electronic Speed Controller) for propulsion. The system uses LoRa for bidirectional communication between the PC (web dashboard) and Raspberry Pi (motor controller).

**Components:**
- **Quicrun ESC**: Electronic speed controller for brushless motor
- **pigpio**: GPIO library for precise PWM signal generation
- **LoRa modules**: Half-duplex wireless communication

### Motor Control Architecture

```
[Web Dashboard] --HTTP--> [PC app.py] --LoRa--> [Pi test.py] --PWM--> [ESC] --> [Motor]
                                       <--ACK--
```

**Command Format:** `CMD:<type>:<value>\n`
- `CMD:THROTTLE:50` - Set throttle to 50%
- `CMD:STOP:0` - Stop motor
- `CMD:ESTOP:0` - Emergency stop

**ACK Format:** `ACK:<type>:<actual_value>:<OK|FAIL>`
- `ACK:THROTTLE:50:OK` - Confirmed motor at 50%

### ESC/PWM Configuration

```python
ESC_GPIO_PIN = 18           # GPIO pin for PWM output
PWM_FREQUENCY = 50          # Standard servo frequency (50Hz)
PWM_MIN_US = 1000           # Full reverse/brake (1000 microseconds)
PWM_NEUTRAL_US = 1500       # Neutral/Stop (1500 microseconds)
PWM_MAX_US = 2000           # Full forward (2000 microseconds)
MAX_THROTTLE_PERCENT = 75   # Safety limit
```

### Hybrid Transmission Protocol

The PC uses a **hybrid transmission approach** that balances motor control responsiveness with sensor data reception. This is critical because LoRa modules are **half-duplex** - they cannot receive while transmitting.

**The Problem:**
- Continuous transmission (e.g., every 150ms) blocks sensor data reception
- The PC would be transmitting so often it never has a window to receive Pi's sensor data

**The Solution - Adaptive Transmission:**
```python
MOTOR_TX_INTERVAL_FAST = 0.15  # 150ms when actively changing throttle
MOTOR_TX_INTERVAL_SLOW = 2.0   # 2 seconds when throttle is stable
MOTOR_ACTIVE_DURATION = 3.0    # Stay in fast mode for 3 seconds after change
```

**How it works:**
1. User changes throttle via web dashboard
2. PC enters "active mode" - transmits every 150ms for 3 seconds
3. After 3 seconds of no changes, PC enters "idle mode" - transmits every 2 seconds
4. In idle mode, PC spends more time listening (500ms vs 100ms windows)
5. This allows sensor data from Pi to be received between transmissions

**Key Insight:** Motor control only needs fast transmission when actively changing. Once stable, slow heartbeat transmission is sufficient while prioritizing sensor data reception.

## Raspberry Pi Auto-Start Setup (systemd)

### Creating the Service File

The Raspberry Pi runs `test.py` automatically on boot using systemd.

**Step 1: Create the service file**
```bash
sudo nano /etc/systemd/system/triton-sensors.service
```

**Step 2: Add this content** (adjust User and paths as needed):
```ini
[Unit]
Description=TRITON Sensor & Motor Control
After=network.target

[Service]
Type=simple
User=az
WorkingDirectory=/home/az/TRITON/TRITON
ExecStart=/usr/bin/python3 /home/az/TRITON/TRITON/src/test.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Step 3: Enable and start the service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable triton-sensors
sudo systemctl start triton-sensors
```

### Service Management Commands

| Command | Description |
|---------|-------------|
| `sudo systemctl status triton-sensors` | Check service status |
| `sudo systemctl start triton-sensors` | Start the service |
| `sudo systemctl stop triton-sensors` | Stop the service |
| `sudo systemctl restart triton-sensors` | Restart the service |
| `sudo systemctl enable triton-sensors` | Enable auto-start on boot |
| `sudo systemctl disable triton-sensors` | Disable auto-start |
| `journalctl -u triton-sensors -f` | View live logs |

### Removing a Service

```bash
sudo systemctl stop triton-sensors
sudo systemctl disable triton-sensors
sudo rm /etc/systemd/system/triton-sensors.service
sudo systemctl daemon-reload
```

### Common systemd Errors

| Error Code | Meaning | Solution |
|------------|---------|----------|
| `status=217/USER` | User doesn't exist | Check username with `whoami`, update `User=` line |
| `status=200/CHDIR` | Directory doesn't exist | Verify `WorkingDirectory` path exists |
| `status=203/EXEC` | Executable not found | Check `ExecStart` path is correct |

## Troubleshooting Guide

### Motor Control Issues

#### Problem: Motor doesn't respond to web commands

**Symptoms:** Clicking throttle buttons on dashboard has no effect.

**Root Cause:** Originally, two separate scripts (`test.py` for sensors, `pi_motor_receiver.py` for motor) tried to use the same serial port (`/dev/ttyUSB0`). Only one process can hold a serial port.

**Solution:** Combined both scripts into single `test.py` that handles sensors AND motor commands. Now only one service is needed.

---

#### Problem: Motor commands work manually but not via systemd service

**Symptoms:** Running `python3 test.py` manually works, but the systemd service doesn't control the motor.

**Possible Causes:**
1. Wrong user in service file (check with `whoami`)
2. Wrong working directory path
3. pigpiod daemon not starting (needs sudo)

**Solution:** Verify service file has correct `User=` and `WorkingDirectory=`. The script auto-starts pigpiod.

---

#### Problem: LoRa commands not received by Pi

**Symptoms:** PC shows "Sent command" but Pi logs show no `[LORA-RX]` messages.

**Root Cause:** LoRa modules are **half-duplex** - they cannot receive while transmitting. The Pi was transmitting sensor data continuously, leaving no window to receive commands.

**Failed Approaches:**
1. **Simple send-and-wait:** PC sends command, waits for ACK. Failed because command often arrived while Pi was transmitting.
2. **ACK-based retry:** PC retries if no ACK. Still unreliable due to timing.

**Working Solution:** Added explicit receive window after each sensor transmission:
```python
# After transmitting sensor data, listen for 500ms
time.sleep(0.1)  # Allow module to switch to receive mode
for _ in range(10):
    if lora_serial.in_waiting:
        # Process incoming command
    time.sleep(0.05)
```

---

#### Problem: Ramp test skips commands

**Symptoms:** Ramp test (gradual throttle increase) skips values or ends at wrong throttle.

**Root Cause:** Send-and-wait protocol moved to next command before confirming previous command executed.

**Working Solution:** Hybrid transmission protocol with fast mode during active changes:
- When throttle changes, PC enters "fast mode" (150ms intervals) for 3 seconds
- This ensures rapid command delivery during ramp tests
- After stabilizing, slows down to allow sensor data through

---

#### Problem: Sensor data not appearing on dashboard (but motor control works)

**Symptoms:** Motor control works from web dashboard, but sensor graphs show no data. Pi logs show `[LORA-TX]` lines for sensor data.

**Root Cause:** The PC was transmitting motor commands too frequently (every 150ms), leaving no receive window for incoming sensor data. LoRa is half-duplex - can't receive while transmitting.

**Diagnosis:**
- Motor control works = PC→Pi communication OK
- No sensor data = Pi→PC communication blocked
- PC transmitting 7x/second blocks all incoming data

**Working Solution:** Implemented hybrid transmission protocol:
```python
MOTOR_TX_INTERVAL_FAST = 0.15  # Fast when changing throttle
MOTOR_TX_INTERVAL_SLOW = 2.0   # Slow when stable
MOTOR_ACTIVE_DURATION = 3.0    # Fast mode duration after change
```

The PC now:
1. Transmits frequently only when throttle is actively changing
2. Slows to 2-second intervals when stable
3. Uses longer listen windows (500ms) in slow mode
4. This allows sensor data to get through between transmissions

---

#### Problem: pigpiod not running

**Symptoms:** Motor control fails with "Failed to connect to pigpio daemon"

**Solution:** The script auto-starts pigpiod, but you can manually start it:
```bash
sudo pigpiod
```

To check if running:
```bash
pgrep -x pigpiod
```

### Sensor Issues

#### Problem: BME280/MPU6050 not detected

**Symptoms:** Script shows "init failed" for sensors.

**Solutions:**
1. Enable I2C: `sudo raspi-config` → Interface Options → I2C → Enable
2. Check wiring (SDA to GPIO2, SCL to GPIO3)
3. Verify I2C addresses: `i2cdetect -y 1` (should show 0x76 for BME280, 0x68 for MPU6050)

### LoRa Issues

#### Problem: Serial port not found

**Symptoms:** "Could not open /dev/ttyUSB0"

**Solutions:**
1. Check USB connection
2. Verify port: `ls /dev/ttyUSB*`
3. Check permissions: `sudo usermod -a -G dialout $USER` (then logout/login)

## System Architecture (Updated)

**Single Script Architecture:**
- `test.py` now handles BOTH sensor collection AND motor control
- Eliminates serial port conflicts
- Single systemd service manages everything

**Data Flow:**
```
                    ┌─────────────────────────────────────┐
                    │         Raspberry Pi                │
                    │  ┌─────────────────────────────┐    │
                    │  │         test.py             │    │
                    │  │  - Sensor collection        │    │
                    │  │  - LoRa TX (sensor data)    │    │
                    │  │  - LoRa RX (motor commands) │    │
                    │  │  - Motor/ESC control        │    │
                    │  └─────────────────────────────┘    │
                    │              │ LoRa                 │
                    └──────────────┼──────────────────────┘
                                   │
                    ┌──────────────┼──────────────────────┐
                    │              │ LoRa                 │
                    │         PC / Laptop                 │
                    │  ┌───────────▼─────────────────┐    │
                    │  │         app.py              │    │
                    │  │  - Web dashboard            │    │
                    │  │  - LoRa RX (sensor data)    │    │
                    │  │  - LoRa TX (motor commands) │    │
                    │  │  - Continuous TX thread     │    │
                    │  └─────────────────────────────┘    │
                    │              │ HTTP :5000           │
                    │  ┌───────────▼─────────────────┐    │
                    │  │      Web Browser            │    │
                    │  │  - Dashboard UI             │    │
                    │  │  - Motor controls           │    │
                    │  └─────────────────────────────┘    │
                    └─────────────────────────────────────┘
```

## TRITON Mission Notes

The TRITON system is designed for autonomous submarine operations with:
- Continuous environmental monitoring (pressure for depth calculation)
- Inertial navigation capability (accelerometer + gyroscope)
- Wireless data transmission for real-time monitoring
- Comprehensive data logging for post-mission analysis
- Web-based mission control interface
- **Brushless motor control via LoRa** with reliable continuous transmission protocol