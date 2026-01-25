# TRITON Autonomous Submarine Navigation System

[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%20%7C%20Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](https://github.com/topics/cross-platform)

**TRITON** is an autonomous submarine navigation system that evolved from the original CanSat (satellite simulation) project. It features real-time sensor data collection, LoRa wireless communication, and comprehensive web-based monitoring for underwater navigation applications.

## Features

- **Multi-Sensor Data Collection**: BME280 environmental sensor + MPU6050 inertial measurement unit
- **Dual-Platform Architecture**: Raspberry Pi for data collection, PC for monitoring and logging
- **Wireless Communication**: LoRa long-range radio transmission between platforms
- **Motor Control**: Web-based brushless motor control via LoRa with throttle presets and ramp testing
- **Real-Time Web Dashboard**: Live sensor visualization with Chart.js graphs
- **Data Logging**: Automatic CSV logging with timestamp and statistical analysis
- **Threshold-Based Transmission**: Intelligent data filtering to reduce network overhead
- **Cross-Platform Support**: Windows, Linux, macOS compatibility
- **Multiple Color Themes**: Dark Ocean, Night, Light Ocean, Nature, Retro, and Futuristic themes
- **Interactive Chart Controls**: Zoom, pan, and tooltips for detailed data analysis
- **Time Range Filtering**: Filter dashboard display and CSV exports by time range
- **Extended Statistics Panel**: Percentiles, rate of change, and comprehensive metrics
- **Multi-Metric Correlation View**: Dual Y-axis charts for comparing different sensor readings
- **Chart Export**: Export charts as PNG/JPEG or download all charts as ZIP
- **Mission Comparison**: Compare data across multiple mission CSV files with dual display
- **Mission Replay**: Playback recorded mission data with adjustable speed controls
- **Configuration Profiles**: Save and load dashboard configuration profiles
- **Sections Toggle Bar**: Quick All/None buttons and column layout selector (1-4 columns)
- **Analysis Row Layout**: Side-by-side Correlation and Compare sections

## Table of Contents

- [Hardware Requirements](#hardware-requirements)
- [Software Dependencies](#software-dependencies)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [System Architecture](#system-architecture)
- [Usage](#usage)
- [Data Format](#data-format)
- [Configuration](#configuration)
- [Web Dashboard](#web-dashboard)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Hardware Requirements

### Raspberry Pi Platform (Data Collection)
- **Raspberry Pi Zero 2 W** (or compatible)
- **BME280 Environmental Sensor** (I2C address: 0x76)
  - Temperature, humidity, pressure, altitude measurement
- **MPU6050 Inertial Measurement Unit** (I2C address: 0x68)
  - 3-axis accelerometer and gyroscope
- **LoRa Module** for wireless transmission
- MicroSD card (16GB+ recommended)
- Power supply (battery pack for autonomous operation)

### PC Platform (Monitoring and Logging)
- **Computer** running Windows, Linux, or macOS
- **LoRa Receiver Module** connected via USB/serial
- USB cable for LoRa module connection

### Wiring

#### Sensors (I2C)
- BME280: Connect via I2C (SDA/SCL pins)
- MPU6050: Connect via I2C (SDA/SCL pins)
- LoRa modules: UART/Serial connection

#### Motor ESC (Hobbywing Quicrun WP10BL120)

**ESC to Motor wiring** (left to right when viewing ESC connector):
| Position | Wire Color | Connection |
|----------|------------|------------|
| Left     | Black      | Motor wire 1 |
| Middle   | Yellow     | Motor wire 2 |
| Right    | Red        | Motor wire 3 |

**ESC to Raspberry Pi wiring:**
| ESC Wire | Raspberry Pi Pin | Description |
|----------|------------------|-------------|
| White (Signal) | Pin 12 (GPIO18) | PWM signal |
| Black (Ground) | Pin 39 (GND)    | Ground |

> **Note:** Do NOT connect the red wire from ESC to Raspberry Pi - the ESC is powered separately.

## Software Dependencies

### Raspberry Pi Dependencies
```bash
sudo apt update && sudo apt upgrade
sudo apt install python3-pip git
sudo pip3 install adafruit-circuitpython-bme280 --break-system-packages
sudo pip3 install mpu6050-raspberrypi --break-system-packages
```

### PC Dependencies
```bash
pip install flask pyserial requests pytz numpy
```

### Python Modules Used
- `adafruit-circuitpython-bme280` - BME280 sensor interface
- `mpu6050-raspberrypi` - MPU6050 sensor interface
- `flask` - Web server framework
- `pyserial` - Serial communication for LoRa
- `requests` - HTTP requests for web updates
- `pytz` - Timezone handling
- `numpy` - Numerical calculations

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/[username]/TRITON.git
cd TRITON
```

### 2. Raspberry Pi Setup
```bash
# Enable I2C interface
sudo raspi-config
# Navigate to: Interfacing Options > I2C > Enable

# Install dependencies
sudo apt update
sudo apt install python3-pip git
sudo pip3 install adafruit-circuitpython-bme280 --break-system-packages
sudo pip3 install mpu6050-raspberrypi --break-system-packages

# Test I2C devices
sudo i2cdetect -y 1
# Should show devices at 0x68 (MPU6050) and 0x76 (BME280)
```

### 3. PC Setup
```bash
# Install Python dependencies
pip install flask pyserial requests pytz numpy

# Verify LoRa receiver connection
# Windows: Check Device Manager for COM port
# Linux: ls /dev/ttyUSB*
# macOS: ls /dev/tty.usb*
```

## Raspberry Pi Auto-Start Setup (systemd)

To run TRITON automatically on boot, create a systemd service:

### Step 1: Create the Service File

```bash
sudo nano /etc/systemd/system/triton-sensors.service
```

Add this content (adjust `User` and paths as needed):

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

### Step 2: Enable and Start

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

## Quick Start

### PC Side

Start the Flask web server (includes LoRa receiver for motor control and sensor data):
```bash
python src/app.py
```

Access the dashboard at: `http://localhost:5000`

### Raspberry Pi Side

**For sensor data collection:**
```bash
python src/test.py
```

**For motor/ESC control:**
```bash
# Start pigpio daemon first (required for PWM)
sudo pigpiod

# Start motor command receiver
python src/pi_motor_receiver.py
```

**For both sensors AND motor control** (run in separate terminals):
```bash
# Terminal 1: Sensor collection
python src/test.py

# Terminal 2: Motor control (start pigpiod first)
sudo pigpiod
python src/pi_motor_receiver.py
```

### Summary Table

| Platform | File | Purpose |
|----------|------|---------|
| **PC** | `src/app.py` | Web dashboard + LoRa motor commands + sensor reception |
| **Raspberry Pi** | `src/test.py` | Sensor data collection + LoRa transmission |
| **Raspberry Pi** | `src/pi_motor_receiver.py` | Motor/ESC control via LoRa commands |

### Unified Script (Recommended)

As of the latest update, `test.py` now handles **both** sensor collection AND motor control in a single script. This eliminates serial port conflicts and simplifies deployment:

```bash
# Single command for everything on Raspberry Pi
python src/test.py
```

> **Note:** The separate `pi_motor_receiver.py` has been moved to `src/legacy/` for reference. The unified approach is now recommended.

## System Architecture

```
+---------------------+    LoRa Radio    +---------------------+
|   Raspberry Pi      | <--------------> |        PC           |
|                     |                   |                     |
| +-----------------+ |                   | +-----------------+ |
| | BME280 Sensor   | |                   | | LoRa Receiver   | |
| | MPU6050 Sensor  | |                   | | Data Logger     | |
| | LoRa Transmitter| |                   | | Web Server      | |
| +-----------------+ |                   | +-----------------+ |
+---------------------+                   +---------------------+
         |                                          |
         v                                          v
   Sensor Data                                Web Dashboard
   Collection                                 Real-time Visualization
```

### Unified Architecture (Current)

The system now uses a unified script on the Raspberry Pi that handles everything:

```
                    ┌─────────────────────────────────────┐
                    │         Raspberry Pi                │
                    │  ┌─────────────────────────────┐    │
                    │  │         test.py             │    │
                    │  │  - Sensor collection        │    │
                    │  │  - LoRa TX (sensor data)    │    │
                    │  │  - LoRa RX (motor commands) │    │
                    │  │  - Motor/ESC control (PWM)  │    │
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

### Motor Control Protocol

The system uses a **hybrid transmission protocol** for reliable motor control while maintaining sensor data reception over half-duplex LoRa.

**Command Format:** `CMD:<type>:<value>\n`
- `CMD:THROTTLE:50` - Set throttle to 50%
- `CMD:STOP:0` - Stop motor
- `CMD:ESTOP:0` - Emergency stop

**ACK Format:** `ACK:<type>:<actual_value>:<OK|FAIL>`
- `ACK:THROTTLE:50:OK` - Confirmed motor at 50%

#### Hybrid Transmission (Solving Half-Duplex LoRa)

LoRa modules are **half-duplex** - they cannot receive while transmitting. This creates a challenge: if the PC transmits motor commands too frequently, it blocks incoming sensor data from the Pi.

**The Solution - Adaptive Transmission:**
```python
MOTOR_TX_INTERVAL_FAST = 0.15  # 150ms when actively changing throttle
MOTOR_TX_INTERVAL_SLOW = 2.0   # 2 seconds when throttle is stable
MOTOR_ACTIVE_DURATION = 3.0    # Stay in fast mode for 3 seconds after change
```

| Mode | Transmission Rate | Listen Window | When Active |
|------|-------------------|---------------|-------------|
| **Fast** | Every 150ms | 100ms | 3 seconds after throttle change |
| **Slow** | Every 2 seconds | 500ms | When throttle is stable |

This ensures:
- Responsive motor control when actively adjusting throttle
- Reliable sensor data reception when motor is stable
- No data loss due to transmission conflicts

### Dual-Mode Operating Protocol

The system supports two operating modes for flexible control:

| Mode | Description | Motor Commands | Sensor Data | Best For |
|------|-------------|----------------|-------------|----------|
| **PASSIVE** | Pi autonomous | On change only | Priority | Autonomous missions |
| **ACTIVE** | PC manual control | Priority | Works | Manual control/testing |

**ESTOP (Emergency Stop)** always has highest priority and blocks all other operations until confirmed.

**Command Extensions:**
```
CMD:MODE:PASSIVE    - Switch to passive (Pi autonomous)
CMD:MODE:ACTIVE     - Switch to active (PC manual)
CMD:ESTOP:0         - Emergency stop (highest priority)
```

**Mode Selection UI:** The dashboard includes a mode selector with PASSIVE and ACTIVE buttons, plus a nav bar indicator showing current mode and connection status.

### Data Flow
1. **Raspberry Pi** (`test.py`) collects sensor data and transmits via LoRa
2. **PC** (`lorareceivertest.py`) receives LoRa data and logs to CSV
3. **Web Server** (`app.py`) provides real-time dashboard with statistics
4. **Dashboard** updates automatically with live sensor readings

## Usage

### Core Components

| File | Platform | Purpose |
|------|----------|---------|
| `src/app.py` | PC | Flask web server with dashboard + motor control API + continuous LoRa TX |
| `src/test.py` | Raspberry Pi | **Unified script**: sensor collection + LoRa TX/RX + motor control |
| `src/motor_control.py` | Raspberry Pi | Motor control library (PWM for ESC) |
| `src/lorareceivertest.py` | PC | LoRa data reception and CSV logging |
| `src/lorasendertest.py` | Raspberry Pi | LoRa transmission testing |
| `src/web_server.py` | PC | Alternative web server implementation |

> **Note:** `pi_motor_receiver.py` has been moved to `src/legacy/` - motor control is now integrated into `test.py`

### Running Individual Components

**Test LoRa Communication:**
```bash
# Raspberry Pi (sender)
python src/lorasendertest.py

# PC (receiver)
python src/lorareceivertest.py
```

**Web Dashboard Only:**
```bash
python src/app.py
# Access: http://localhost:5000
```

## Data Format

### Sensor Array Structure (12 elements)
| Index | Parameter | Unit | Description |
|-------|-----------|------|-------------|
| [0] | Elapsed Time | s | Time since system start |
| [1] | BME280 Temperature | C | Environmental temperature |
| [2] | BME280 Humidity | % | Relative humidity |
| [3] | BME280 Pressure | hPa | Atmospheric pressure |
| [4] | BME280 Altitude | m | Calculated altitude |
| [5] | MPU6050 Acceleration X | m/s2 | X-axis acceleration |
| [6] | MPU6050 Acceleration Y | m/s2 | Y-axis acceleration |
| [7] | MPU6050 Acceleration Z | m/s2 | Z-axis acceleration |
| [8] | MPU6050 Gyro X | deg/s | X-axis angular velocity |
| [9] | MPU6050 Gyro Y | deg/s | Y-axis angular velocity |
| [10] | MPU6050 Gyro Z | deg/s | Z-axis angular velocity |
| [11] | MPU6050 Temperature | C | IMU internal temperature |

### CSV Output Format
- **File Location**: `logs/sensor_data_YYYYMMDD_HHMMSS.csv`
- **Archive Location**: `logs/previous_data/`
- **Timestamp Format**: MET (Mission Elapsed Time)
- **Statistics**: Min/Max values appended on shutdown

## Configuration

### BME280 Settings
```python
# Sea level pressure (adjust for location)
SEA_LEVEL_PRESSURE = 993.9  # hPa
I2C_ADDRESS = 0x76
```

### MPU6050 Settings
```python
# Measurement ranges
GYRO_RANGE = 2000  # deg/s
ACCEL_RANGE = 16   # g
I2C_ADDRESS = 0x68
```

### LoRa Communication
```python
# Raspberry Pi
LORA_PORT = "/dev/ttyUSB0"

# PC (adjust as needed)
LORA_PORT = "COM8"  # Windows
LORA_PORT = "/dev/ttyUSB0"  # Linux

# Common settings
BAUD_RATE = 9600
TIMEOUT = 1.0
```

### Motor/ESC Configuration
```python
# GPIO and PWM settings
ESC_GPIO_PIN = 18           # GPIO pin for PWM output (Pin 12)
PWM_FREQUENCY = 50          # Standard servo frequency (50Hz = 20ms period)

# PWM pulse widths (microseconds)
PWM_MIN_US = 1000           # Full reverse/brake
PWM_NEUTRAL_US = 1500       # Neutral/Stop
PWM_MAX_US = 2000           # Full forward

# Safety limits
MAX_THROTTLE_PERCENT = 75   # Maximum allowed throttle (safety limit)
PWM_REFRESH_RATE = 50       # How often to refresh PWM signal (Hz)
```

### Hybrid Transmission Settings
```python
# PC-side motor command transmission (adaptive)
MOTOR_TX_INTERVAL_FAST = 0.15  # Fast mode: 150ms (when throttle changing)
MOTOR_TX_INTERVAL_SLOW = 2.0   # Slow mode: 2 seconds (when stable)
MOTOR_ACTIVE_DURATION = 3.0    # Stay in fast mode for 3 seconds after change
```

### Data Transmission Thresholds
| Parameter | Threshold | Purpose |
|-----------|-----------|---------|
| BME280 Temperature | 0.25 C | Reduce transmission frequency |
| Humidity | 1.0% | Filter minor fluctuations |
| Pressure | 0.5 hPa | Focus on significant changes |
| Altitude | 0.5m | Submarine depth tracking |
| Acceleration (all axes) | 0.25 m/s2 | Motion detection |
| Gyroscope (all axes) | 5.0 deg/s | Rotation detection |
| MPU Temperature | 0.25 C | Thermal monitoring |

## Web Dashboard

### Features
- **Real-time Data**: Live sensor readings with 1-second updates
- **Interactive Charts**: Chart.js-based visualizations with zoom and pan
- **Historical Data**: Last 300 data points per metric
- **Statistics**: Min/Max/Average calculations plus percentiles and rate of change
- **Data Download**: CSV export functionality with time range filtering
- **Test Mode**: Generate random data for testing
- **Theme Selection**: Six color themes (Dark Ocean, Night, Light Ocean, Nature, Retro, Futuristic)
- **Chart Export**: Download individual charts as PNG/JPEG or all charts as ZIP
- **Multi-Metric Correlation**: Compare multiple sensor readings on dual Y-axis charts
- **Mission Comparison**: Load and compare multiple CSV mission files side by side
- **Mission Replay**: Playback recorded missions with adjustable speed (0.5x to 10x)
- **Configuration Profiles**: Save and load dashboard layout and settings
- **Sections Toggle**: Quick All/None buttons with 1-4 column layout options
- **Analysis Row**: Side-by-side Correlation and Compare sections for data analysis

### Dashboard URLs
- **Main Dashboard**: `http://localhost:5000`
- **Data API**: `http://localhost:5000/data`
- **Update Endpoint**: `http://localhost:5000/update` (POST)

### Test Functions
- **Generate Test Data**: Creates realistic sensor data for testing
- **Clear Data**: Resets all dashboard data
- **Download CSV**: Export current session data

### Keyboard Shortcuts
- Use scroll wheel on charts to zoom in/out
- Click and drag to pan across time series data
- Double-click charts to reset zoom level

## Troubleshooting

### Common Issues

**I2C Sensor Not Detected:**
```bash
# Check I2C is enabled
sudo raspi-config
# Enable I2C interface

# Scan for devices
sudo i2cdetect -y 1
# Expected: 0x68 (MPU6050), 0x76 (BME280)
```

**LoRa Communication Failed:**
```bash
# Check serial port permissions
sudo usermod -a -G dialout $USER
# Logout and login again

# Test serial connection
ls -la /dev/ttyUSB*  # Linux
# Windows: Device Manager > Ports (COM & LPT)
```

**Web Dashboard Not Accessible:**
```bash
# Check if Flask is running
netstat -tulpn | grep :5000

# Firewall issues (Linux)
sudo ufw allow 5000

# Windows Firewall
# Allow Python through Windows Defender Firewall
```

**Sensor Error Messages:**
- `BME280 sensor not found`: Check I2C connection and address
- `MPU6050 error`: Verify power supply and I2C wiring
- `LoRa timeout`: Check serial connection and baud rate

**Motor/ESC Not Responding:**

If the ESC is not responding to commands or behaving erratically, perform this reset sequence:

1. Turn ESC **OFF**
2. Unplug the **red cable** from the ESC
3. Turn ESC **ON**
4. Plug the **red cable** back in
5. Turn ESC **OFF**
6. Turn ESC **ON**
7. ESC should now respond correctly

**pigpio Daemon Not Running:**
```bash
# Check if pigpiod is running
pgrep pigpiod

# Start the daemon
sudo pigpiod

# If it fails, check for existing instances
sudo killall pigpiod
sudo pigpiod
```

### Motor Control Troubleshooting

**Motor doesn't respond to web commands:**

This was a common issue caused by serial port conflicts. Originally, two scripts (`test.py` and `pi_motor_receiver.py`) tried to use the same serial port (`/dev/ttyUSB0`). Only one process can hold a serial port at a time.

**Solution:** Use the unified `test.py` which handles both sensors AND motor control.

---

**Commands work sometimes but not reliably:**

This is caused by LoRa modules being **half-duplex** - they cannot receive while transmitting.

**Failed Approaches:**
1. Simple send-and-wait: Commands often arrived while Pi was transmitting sensor data
2. ACK-based retry: Still unreliable due to timing

**Working Solution:** The PC now uses continuous transmission - sending the target throttle every 150ms until confirmed. This works like RC controllers.

---

**Ramp test skips commands:**

The ramp test sends many throttle values in sequence. With unreliable delivery, some values were skipped.

**Solution:** The continuous transmission protocol ensures each command is received before moving to the next. The PC waits for ACK confirmation that the motor reached the target state.

---

**systemd service runs but motor doesn't work:**

Check for these issues:
1. Wrong user in service file - verify with `whoami`
2. pigpiod not starting - the script auto-starts it, but may need sudo
3. Wrong working directory path

For more detailed troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Project Structure

```
TRITON/
├── src/
│   ├── test.py                    # Main Raspberry Pi: sensors + LoRa + motor control (unified)
│   ├── app.py                    # Flask web dashboard + motor control API + continuous TX
│   ├── lorareceivertest.py       # PC LoRa receiver and logger
│   ├── motor_control.py          # Motor control library (PWM for ESC)
│   ├── lorasendertest.py         # LoRa transmission testing
│   ├── web_server.py             # Alternative web server
│   ├── templates/
│   │   ├── dashboard.html        # Real-time dashboard template (with motor control UI)
│   │   └── index.html            # Landing page template
│   ├── logs/                     # CSV data logs
│   │   └── previous_data/        # Archived log files
│   └── legacy/                   # Obsolete/reference files
│       └── pi_motor_receiver.py  # Legacy standalone motor receiver (now in test.py)
├── config/                       # Configuration files
│   └── triton_config.json        # Dashboard and sensor configuration
├── README.md                     # This file
├── CLAUDE.md                     # Development instructions
├── TROUBLESHOOTING.md            # Detailed troubleshooting guide
├── Disabled_Features.md          # Documentation of hidden features
├── FEATURE_IMPLEMENTATION_WORKFLOW.md # Development workflow
└── LICENSE                       # Proprietary License
```

## Contributing

This project uses a proprietary license. All contributions require written approval from the copyright holder before they can be accepted.

If you wish to contribute:
1. Contact the project maintainer for written approval
2. Once approved, fork the repository
3. Create feature branch: `git checkout -b feature/amazing-feature`
4. Commit changes: `git commit -m 'Add amazing feature'`
5. Push to branch: `git push origin feature/amazing-feature`
6. Open Pull Request (requires prior written approval)

### Development Guidelines
- Follow the workflow in `FEATURE_IMPLEMENTATION_WORKFLOW.md`
- Use the project instructions in `CLAUDE.md`
- Test on both Raspberry Pi and PC platforms
- Update documentation for new features
- Maintain backward compatibility where possible

## License

This project is proprietary software. All rights are reserved by the copyright holders.

**You may NOT use, copy, modify, distribute, or create derivative works from this software without obtaining prior written approval from the copyright holder.**

See the [LICENSE](LICENSE) file for full terms and conditions.

To request permission, contact the project maintainer.

## Acknowledgments

- **Adafruit** for CircuitPython BME280 library
- **Raspberry Pi Foundation** for excellent hardware platform
- **Chart.js** for web dashboard visualization
- **Flask** development team for web framework
- **LoRa Alliance** for long-range communication standard

## Support

- **Issues**: [GitHub Issues](https://github.com/[username]/TRITON/issues)
- **Discussions**: [GitHub Discussions](https://github.com/[username]/TRITON/discussions)
- **Documentation**: See `TROUBLESHOOTING.md` for detailed help

---

**TRITON** - Navigating the depths of autonomous underwater exploration
