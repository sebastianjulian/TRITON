#!/usr/bin/env python3
"""
TRITON Pi-Side LoRa Motor Command Receiver

This script runs on the Raspberry Pi and:
1. Receives motor commands via LoRa from the PC
2. Controls the brushless motor via ESC
3. Sends acknowledgments back to the PC

Command format received: CMD:<type>:<value>\n
Types: THROTTLE, STOP, ESTOP

Usage:
    python3 pi_motor_receiver.py
"""

import serial
import time
import sys
import subprocess
import os
import threading

# Try to import pigpio for motor control
try:
    import pigpio
    PIGPIO_AVAILABLE = True
except ImportError:
    print("[WARN] pigpio not installed. Motor control will be simulated.")
    PIGPIO_AVAILABLE = False


# ==================== Configuration ====================

LORA_PORT = '/dev/ttyUSB0'
LORA_BAUD = 9600

ESC_GPIO_PIN = 18
PWM_MIN = 1000      # Full reverse/brake
PWM_NEUTRAL = 1500  # Neutral/Stop
PWM_MAX = 2000      # Full forward

MAX_THROTTLE_PERCENT = 75  # Safety limit


# ==================== Motor Controller ====================

class MotorController:
    """Controls brushless motor via ESC using PWM signals."""

    def __init__(self, gpio_pin=ESC_GPIO_PIN):
        self.gpio_pin = gpio_pin
        self.pi = None
        self.armed = False
        self.current_throttle = 0

    def ensure_pigpiod_running(self):
        """Start pigpiod daemon if not already running."""
        try:
            result = subprocess.run(
                ["pgrep", "-x", "pigpiod"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
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
                time.sleep(0.5)
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

    def arm(self):
        """Arm the ESC by sending neutral signal."""
        print("[MOTOR] Arming ESC...")
        self.set_pulse_width(PWM_NEUTRAL)
        time.sleep(2)
        self.armed = True
        print("[MOTOR] ESC armed and ready")

    def set_pulse_width(self, pulse_width_us):
        """Set PWM pulse width in microseconds."""
        pulse_width_us = max(PWM_MIN, min(PWM_MAX, pulse_width_us))

        if PIGPIO_AVAILABLE and self.pi and self.pi.connected:
            self.pi.set_servo_pulsewidth(self.gpio_pin, pulse_width_us)
        else:
            print(f"[MOTOR-SIM] PWM: {pulse_width_us}us")

    def set_throttle(self, percent):
        """Set throttle as percentage (0-100)."""
        if not self.armed:
            print("[MOTOR] Warning: ESC not armed")
            return False

        # Apply safety limit
        if percent > MAX_THROTTLE_PERCENT:
            percent = MAX_THROTTLE_PERCENT
            print(f"[MOTOR] Throttle limited to {percent}%")

        # Convert percentage to pulse width (forward only: 1500-2000)
        pulse_width = PWM_NEUTRAL + (percent / 100.0) * (PWM_MAX - PWM_NEUTRAL)

        self.set_pulse_width(int(pulse_width))
        self.current_throttle = percent
        print(f"[MOTOR] Throttle: {percent}% -> Pulse: {int(pulse_width)}us")
        return True

    def stop(self):
        """Stop the motor (set to neutral)."""
        print("[MOTOR] Stopping motor...")
        self.set_pulse_width(PWM_NEUTRAL)
        self.current_throttle = 0
        return True

    def emergency_stop(self):
        """Emergency stop - immediately cuts motor power."""
        print("[MOTOR] EMERGENCY STOP!")
        self.set_pulse_width(PWM_NEUTRAL)
        self.current_throttle = 0
        return True

    def cleanup(self):
        """Clean up GPIO and stop motor."""
        print("[MOTOR] Cleaning up...")
        if PIGPIO_AVAILABLE and self.pi and self.pi.connected:
            self.set_pulse_width(PWM_NEUTRAL)
            time.sleep(0.5)
            self.pi.set_servo_pulsewidth(self.gpio_pin, 0)
            self.pi.stop()
        print("[MOTOR] Cleanup complete")


# ==================== Command Parser ====================

def parse_command(line):
    """
    Parse incoming command.
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
            value = 0

    return command_type, value


# ==================== Main Loop ====================

def main():
    print("=" * 50)
    print("TRITON Pi Motor Command Receiver")
    print("=" * 50)
    print(f"LoRa Port: {LORA_PORT}")
    print(f"ESC GPIO: {ESC_GPIO_PIN}")
    print(f"Max Throttle: {MAX_THROTTLE_PERCENT}%")
    print("=" * 50)

    # Initialize motor controller
    motor = MotorController()

    if not motor.connect():
        print("[ERROR] Failed to initialize motor controller")
        if not PIGPIO_AVAILABLE:
            print("[INFO] Continuing in simulation mode...")
        else:
            return 1

    # Initialize serial connection
    try:
        ser = serial.Serial(LORA_PORT, LORA_BAUD, timeout=1)
        print(f"[LORA] Connected to {LORA_PORT} at {LORA_BAUD} baud")
    except Exception as e:
        print(f"[ERROR] Failed to open serial port: {e}")
        return 1

    # Arm the ESC
    motor.arm()

    print("\n[READY] Listening for commands...")
    print("Commands: THROTTLE:<0-100>, STOP, ESTOP")
    print("Press Ctrl+C to exit\n")

    try:
        while True:
            if ser.in_waiting:
                try:
                    line = ser.readline().decode(errors='ignore').strip()

                    if not line:
                        continue

                    print(f"[RX] {line}")

                    # Parse command
                    cmd_type, value = parse_command(line)

                    if cmd_type is None:
                        # Not a command, might be sensor data or other
                        continue

                    # Execute command
                    success = False
                    response = ""

                    if cmd_type == "THROTTLE":
                        success = motor.set_throttle(value)
                        response = f"ACK:THROTTLE:{value}:{'OK' if success else 'FAIL'}"

                    elif cmd_type == "STOP":
                        success = motor.stop()
                        response = f"ACK:STOP:0:{'OK' if success else 'FAIL'}"

                    elif cmd_type == "ESTOP":
                        success = motor.emergency_stop()
                        response = f"ACK:ESTOP:0:{'OK' if success else 'FAIL'}"

                    else:
                        print(f"[WARN] Unknown command: {cmd_type}")
                        response = f"ACK:{cmd_type}:0:UNKNOWN"

                    # Send acknowledgment back via LoRa
                    if response:
                        ser.write((response + "\n").encode())
                        ser.flush()
                        print(f"[TX] {response}")

                except Exception as e:
                    print(f"[ERROR] Processing error: {e}")

            time.sleep(0.01)  # Small delay to prevent CPU hogging

    except KeyboardInterrupt:
        print("\n[INFO] Shutting down...")

    finally:
        motor.cleanup()
        ser.close()
        print("[INFO] Goodbye!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
