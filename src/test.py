#!/usr/bin/env python3
"""
TRITON Main Script - Sensor Collection, LoRa Transmission & Motor Control

This script runs on the Raspberry Pi and handles:
1. Sensor data collection (BME280 + MPU6050)
2. Data logging to CSV files
3. LoRa transmission to PC
4. Motor command reception via LoRa
5. ESC/Motor control via pigpio

Usage:
    python3 test.py
"""

import os
import glob
import shutil
import time
import board
import busio
import serial
import subprocess
import threading
from datetime import datetime

import numpy as np
from adafruit_bme280 import basic as adafruit_bme280
from mpu6050 import mpu6050
import pytz

# Try to import pigpio for motor control
try:
    import pigpio
    PIGPIO_AVAILABLE = True
except ImportError:
    print("[WARN] pigpio not installed. Motor control will be simulated.")
    PIGPIO_AVAILABLE = False


# ==================== CONFIGURATION ====================

TZ = pytz.timezone("Europe/Berlin")
LOG_DIR = "logs"
ARCHIVE_DIR = os.path.join(LOG_DIR, "previous_data")

# LoRa Configuration
BAUD_RATE = 9600
LORA_PORT = '/dev/ttyUSB0'

# Motor/ESC Configuration
ESC_GPIO_PIN = 18
PWM_FREQUENCY = 50          # Standard servo frequency (50Hz = 20ms period)
PWM_MIN_US = 1000           # Full reverse/brake (1000 microseconds)
PWM_NEUTRAL_US = 1500       # Neutral/Stop (1500 microseconds)
PWM_MAX_US = 2000           # Full forward (2000 microseconds)
MAX_THROTTLE_PERCENT = 75   # Safety limit
PWM_REFRESH_RATE = 50       # How often to refresh PWM signal (Hz)

# Operating Modes
MODE_PASSIVE = "PASSIVE"    # Autonomous navigation on Pi
MODE_ACTIVE = "ACTIVE"      # Manual control from PC

# Sensor Labels
LABELS = [
    "Elapsed [s]",
    "Temp_BME280 [°C]", "Hum [%]", "Press [hPa]", "Alt [m]",
    "Acc x [m/s²]", "Acc y [m/s²]", "Acc z [m/s²]",
    "Gyro x [°/s]", "Gyro y [°/s]", "Gyro z [°/s]",
    "Temp_MPU [°C]"
]
DECIMALS = [3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]


# ==================== MOTOR CONTROLLER ====================

class MotorController:
    """Controls brushless motor via ESC using continuous PWM signals."""

    def __init__(self, gpio_pin=ESC_GPIO_PIN):
        self.gpio_pin = gpio_pin
        self.pi = None
        self.armed = False
        self.target_throttle = 0
        self.current_pulse_width = PWM_NEUTRAL_US
        self.running = False
        self.pwm_thread = None
        self.lock = threading.Lock()

    def ensure_pigpiod_running(self):
        """Start pigpiod daemon if not already running."""
        try:
            result = subprocess.run(
                ["pgrep", "-x", "pigpiod"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("[MOTOR] pigpiod already running")
                return True
        except FileNotFoundError:
            pass

        print("[MOTOR] Starting pigpiod daemon...")
        try:
            result = subprocess.run(
                ["sudo", "pigpiod"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                time.sleep(1)
                print("[MOTOR] pigpiod started successfully")
                return True
        except Exception as e:
            print(f"[MOTOR] Error starting pigpiod: {e}")
            return False
        return False

    def connect(self):
        """Connect to pigpio daemon."""
        if not PIGPIO_AVAILABLE:
            print("[MOTOR] Running in simulation mode (no pigpio)")
            return True

        self.ensure_pigpiod_running()

        self.pi = pigpio.pi()
        if not self.pi.connected:
            print("[MOTOR] Failed to connect to pigpio daemon")
            return False

        print(f"[MOTOR] Connected to pigpio, using GPIO {self.gpio_pin}")
        return True

    def _pwm_loop(self):
        """Background thread that continuously sends PWM signal."""
        interval = 1.0 / PWM_REFRESH_RATE
        print(f"[MOTOR] PWM refresh thread started ({PWM_REFRESH_RATE}Hz)")

        while self.running:
            with self.lock:
                pulse_width = self.current_pulse_width

            if PIGPIO_AVAILABLE and self.pi and self.pi.connected:
                try:
                    self.pi.set_servo_pulsewidth(self.gpio_pin, pulse_width)
                except Exception as e:
                    print(f"[MOTOR] PWM error: {e}")

            time.sleep(interval)

        print("[MOTOR] PWM refresh thread stopped")

    def start_pwm_thread(self):
        """Start the continuous PWM refresh thread."""
        if self.pwm_thread and self.pwm_thread.is_alive():
            return

        self.running = True
        self.pwm_thread = threading.Thread(target=self._pwm_loop, daemon=True)
        self.pwm_thread.start()

    def stop_pwm_thread(self):
        """Stop the PWM refresh thread."""
        self.running = False
        if self.pwm_thread:
            self.pwm_thread.join(timeout=1)

    def arm(self):
        """Arm the ESC by sending neutral signal."""
        print("[MOTOR] Arming ESC...")
        print("[MOTOR] Sending neutral signal for 3 seconds...")

        with self.lock:
            self.current_pulse_width = PWM_NEUTRAL_US

        self.start_pwm_thread()
        time.sleep(3)

        self.armed = True
        print("[MOTOR] ESC armed and ready!")

    def set_throttle(self, percent):
        """Set throttle as percentage (0-100)."""
        if not self.armed:
            print("[MOTOR] Warning: ESC not armed")
            return False

        percent = max(0, min(percent, MAX_THROTTLE_PERCENT))
        pulse_width = int(PWM_NEUTRAL_US + (percent / 100.0) * (PWM_MAX_US - PWM_NEUTRAL_US))

        with self.lock:
            self.current_pulse_width = pulse_width
            self.target_throttle = percent

        print(f"[MOTOR] Throttle set: {percent}% -> {pulse_width}us")
        return True

    def stop(self):
        """Stop the motor (set to neutral)."""
        print("[MOTOR] Stopping motor...")
        with self.lock:
            self.current_pulse_width = PWM_NEUTRAL_US
            self.target_throttle = 0
        return True

    def emergency_stop(self):
        """Emergency stop - immediately set to neutral."""
        print("[MOTOR] !!! EMERGENCY STOP !!!")
        with self.lock:
            self.current_pulse_width = PWM_NEUTRAL_US
            self.target_throttle = 0
        return True

    def get_status(self):
        """Get current motor status."""
        with self.lock:
            return {
                "throttle": self.target_throttle,
                "pulse_width": self.current_pulse_width,
                "armed": self.armed,
                "running": self.running
            }

    def cleanup(self):
        """Clean up GPIO and stop motor."""
        print("[MOTOR] Cleaning up...")

        with self.lock:
            self.current_pulse_width = PWM_NEUTRAL_US

        time.sleep(0.5)
        self.stop_pwm_thread()

        if PIGPIO_AVAILABLE and self.pi and self.pi.connected:
            self.pi.set_servo_pulsewidth(self.gpio_pin, 0)
            self.pi.stop()

        print("[MOTOR] Cleanup complete")


# ==================== COMMAND PARSER ====================

def parse_motor_command(line):
    """
    Parse incoming motor command.
    Format: CMD:<type>:<value>

    Returns: (command_type, value) or (None, None) if invalid
    """
    line = line.strip()

    if not line.startswith("CMD:"):
        return None, None

    parts = line.split(":")
    if len(parts) < 2:
        return None, None

    command_type = parts[1].upper()
    value = 0

    if len(parts) >= 3:
        try:
            value = int(parts[2])
        except ValueError:
            # For MODE command, value is a string
            value = parts[2].upper()

    return command_type, value


def process_command(motor, cmd_type, value, current_mode, estop_active):
    """
    Process a motor command and return the response.

    Returns: (response_string, new_mode, new_estop_active)
    """
    success = False
    response = ""
    new_mode = current_mode
    new_estop = estop_active

    # ESTOP handling - highest priority
    if cmd_type == "ESTOP":
        success = motor.emergency_stop()
        actual = motor.get_status()["throttle"]
        response = f"ACK:ESTOP:{actual}:{'OK' if success else 'FAIL'}"
        new_estop = True
        print("[ESTOP] !!! EMERGENCY STOP ACTIVATED !!!")

    # If ESTOP is active, only allow ESTOP clear (via new throttle command after confirmation)
    elif estop_active:
        # In ESTOP state, accept commands but motor stays stopped
        if cmd_type == "THROTTLE" and value == 0:
            # Allowing throttle 0 to confirm ESTOP state
            actual = motor.get_status()["throttle"]
            response = f"ACK:THROTTLE:{actual}:OK"
        else:
            print(f"[WARN] ESTOP active - ignoring {cmd_type} command")
            response = f"ACK:{cmd_type}:0:ESTOP_ACTIVE"

    elif cmd_type == "THROTTLE":
        success = motor.set_throttle(value)
        actual = motor.get_status()["throttle"]
        response = f"ACK:THROTTLE:{actual}:{'OK' if success else 'FAIL'}"

    elif cmd_type == "STOP":
        success = motor.stop()
        actual = motor.get_status()["throttle"]
        response = f"ACK:STOP:{actual}:{'OK' if success else 'FAIL'}"

    elif cmd_type == "MODE":
        mode_str = str(value).upper()
        if mode_str in [MODE_PASSIVE, MODE_ACTIVE]:
            new_mode = mode_str
            response = f"ACK:MODE:{new_mode}:OK"
            print(f"[MODE] Operating mode changed to: {new_mode}")
        else:
            response = f"ACK:MODE:{current_mode}:INVALID"
            print(f"[WARN] Invalid mode: {value}")

    else:
        print(f"[WARN] Unknown command: {cmd_type}")
        response = f"ACK:{cmd_type}:0:UNKNOWN"

    return response, new_mode, new_estop


# ==================== MAIN ====================

def main():
    print("=" * 60)
    print("TRITON - Sensor Collection & Motor Control")
    print("=" * 60)

    # ───── PREPARE DIRECTORIES ─────
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

    # Archive old logs
    for path in glob.glob(os.path.join(LOG_DIR, "sensor_data_*.csv")):
        shutil.move(path, ARCHIVE_DIR)

    # Create new log file
    timestamp = datetime.now(TZ).strftime("%Y%m%d_%H%M%S")
    logfile = os.path.join(LOG_DIR, f"sensor_data_{timestamp}.csv")

    # Write CSV header
    with open(logfile, "w") as f:
        f.write("Timestamp (MET)," + ",".join(LABELS) + "\n")

    print(f"[INFO] Logging to: {logfile}")

    # ───── INIT SENSORS ─────
    i2c = busio.I2C(board.SCL, board.SDA)

    try:
        bme = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
        print("[SENSOR] BME280 detected")
    except Exception as e:
        print(f"[SENSOR] BME280 init failed: {e}")
        bme = None

    try:
        mpu = mpu6050(0x68)
        print("[SENSOR] MPU6050 detected")
    except Exception as e:
        print(f"[SENSOR] MPU6050 init failed: {e}")
        mpu = None

    # ───── INIT LORA SERIAL ─────
    try:
        lora_serial = serial.Serial(LORA_PORT, BAUD_RATE, timeout=0.1)
        print(f"[LORA] Connected to {LORA_PORT} at {BAUD_RATE} baud")
    except Exception as e:
        print(f"[LORA] Module not connected: {e}")
        lora_serial = None

    # ───── INIT MOTOR CONTROLLER ─────
    motor = MotorController()
    motor_enabled = motor.connect()

    if motor_enabled:
        motor.arm()
        print("[MOTOR] Motor control enabled")
    else:
        print("[MOTOR] Motor control disabled (simulation mode)")

    # ───── INIT DATA CONTAINERS ─────
    data = [0] * len(LABELS)
    last_data = [None] * len(LABELS)
    min_data = [float('inf')] * len(LABELS)
    max_data = [float('-inf')] * len(LABELS)

    # ───── OPERATING STATE ─────
    current_mode = MODE_ACTIVE  # Start in active (manual control) mode
    estop_active = False        # Emergency stop state

    # ───── MAIN LOOP ─────
    start_time = time.perf_counter()
    last_log_time = start_time

    print("\n" + "=" * 60)
    print("[READY] Sensor logging and motor control active")
    print("Press Ctrl+C to exit")
    print("=" * 60 + "\n")

    try:
        while True:
            now = datetime.now(TZ)
            now_str = now.strftime("%Y-%m-%d %H:%M:%S")
            elapsed = time.perf_counter() - start_time
            data[0] = round(elapsed, DECIMALS[0])

            # ─────────────────────────────────────────
            # CHECK FOR INCOMING MOTOR COMMANDS
            # ─────────────────────────────────────────
            if lora_serial and lora_serial.in_waiting:
                try:
                    line = lora_serial.readline().decode(errors='ignore').strip()
                    if line:
                        print(f"[LORA-RX] {line}")

                        cmd_type, value = parse_motor_command(line)

                        if cmd_type is not None:
                            response, current_mode, estop_active = process_command(
                                motor, cmd_type, value, current_mode, estop_active
                            )

                            # Send acknowledgment
                            if response:
                                lora_serial.write((response + "\n").encode())
                                lora_serial.flush()
                                print(f"[LORA-TX] {response}")

                            # Print motor status
                            status = motor.get_status()
                            print(f"[MOTOR] Throttle: {status['throttle']}% | PWM: {status['pulse_width']}us | Mode: {current_mode}")

                except Exception as e:
                    print(f"[LORA-RX] Error: {e}")

            # ─────────────────────────────────────────
            # READ SENSORS
            # ─────────────────────────────────────────
            if bme:
                try:
                    data[1] = round(bme.temperature, DECIMALS[1])
                    data[2] = round(bme.humidity, DECIMALS[2])
                    data[3] = round(bme.pressure, DECIMALS[3])
                    data[4] = round(bme.altitude, DECIMALS[4])
                except:
                    data[1:5] = ["Error"] * 4

            if mpu:
                try:
                    acc = mpu.get_accel_data()
                    gyro = mpu.get_gyro_data()
                    data[5] = round(acc["x"], DECIMALS[5])
                    data[6] = round(acc["y"], DECIMALS[6])
                    data[7] = round(acc["z"], DECIMALS[7])
                    data[8] = round(gyro["x"], DECIMALS[8])
                    data[9] = round(gyro["y"], DECIMALS[9])
                    data[10] = round(gyro["z"], DECIMALS[10])
                    data[11] = round(mpu.get_temp(), DECIMALS[11])
                except:
                    data[5:12] = ["Error"] * 7

            # ─────────────────────────────────────────
            # LOG DATA (on change or every 1 second)
            # ─────────────────────────────────────────
            now_perf = time.perf_counter()
            changed = any(data[i] != last_data[i] for i in range(len(data)))

            if changed or (now_perf - last_log_time) >= 1.0:
                last_data = list(data)
                last_log_time = now_perf

                # Update min/max
                for i in range(1, len(data)):
                    try:
                        val = float(data[i])
                        min_data[i] = min(min_data[i], val)
                        max_data[i] = max(max_data[i], val)
                    except:
                        continue

                # Print to console
                line = f"{now_str:<22}" + ", ".join(f"{str(x):>8}" for x in data)
                print(line)

                # Write to file
                with open(logfile, "a") as f:
                    f.write(now_str + "," + ",".join(str(x) for x in data) + "\n")

                # Send sensor data over LoRa
                if lora_serial:
                    try:
                        lora_line = now_str + "," + ",".join(str(x) for x in data) + "\n"
                        lora_serial.write(lora_line.encode())
                        lora_serial.flush()

                        # IMPORTANT: Wait for transmission to complete, then listen for commands
                        # LoRa is half-duplex - can't receive while transmitting
                        time.sleep(0.1)  # Allow module to switch to receive mode

                        # Check for incoming commands after transmission
                        for _ in range(10):  # Check multiple times over 500ms
                            if lora_serial.in_waiting:
                                try:
                                    cmd_line = lora_serial.readline().decode(errors='ignore').strip()
                                    if cmd_line:
                                        print(f"[LORA-RX] {cmd_line}")
                                        cmd_type, value = parse_motor_command(cmd_line)
                                        if cmd_type is not None:
                                            response, current_mode, estop_active = process_command(
                                                motor, cmd_type, value, current_mode, estop_active
                                            )
                                            if response:
                                                lora_serial.write((response + "\n").encode())
                                                lora_serial.flush()
                                                print(f"[LORA-TX] {response}")
                                except Exception as e:
                                    print(f"[LORA-RX] Error: {e}")
                            time.sleep(0.05)

                    except Exception as e:
                        print(f"[LORA-TX] Send failed: {e}")

            time.sleep(0.05)  # 50ms loop for responsive motor control

    except KeyboardInterrupt:
        print("\n[INFO] Shutting down...")

    finally:
        # Cleanup motor
        if motor_enabled:
            motor.cleanup()

        # Close LoRa serial
        if lora_serial:
            lora_serial.close()

        # Write min/max to log
        with open(logfile, "a") as f:
            f.write("\nMIN," + ",".join(
                str(round(x, d)) if isinstance(x, float) and x != float('inf') else ""
                for x, d in zip(min_data, DECIMALS)
            ) + "\n")
            f.write("MAX," + ",".join(
                str(round(x, d)) if isinstance(x, float) and x != float('-inf') else ""
                for x, d in zip(max_data, DECIMALS)
            ) + "\n")

        print("[INFO] Min/Max values written to log")
        print("[INFO] Goodbye!")


if __name__ == "__main__":
    main()
