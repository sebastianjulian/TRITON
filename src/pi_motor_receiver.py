#!/usr/bin/env python3
"""
TRITON Pi-Side LoRa Motor Command Receiver

This script runs on the Raspberry Pi and:
1. Receives motor commands via LoRa from the PC
2. Controls the brushless motor via ESC with continuous PWM
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
import threading
from queue import Queue, Empty

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
PWM_FREQUENCY = 50      # Standard servo frequency (50Hz = 20ms period)
PWM_MIN_US = 1000       # Full reverse/brake (1000 microseconds)
PWM_NEUTRAL_US = 1500   # Neutral/Stop (1500 microseconds)
PWM_MAX_US = 2000       # Full forward (2000 microseconds)

MAX_THROTTLE_PERCENT = 75  # Safety limit
PWM_REFRESH_RATE = 50      # How often to refresh PWM signal (Hz)


# ==================== Motor Controller ====================

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
                time.sleep(1)  # Give daemon time to fully initialize
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
            else:
                # Simulation mode - just print occasionally
                pass

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

        # Start PWM thread if not already running
        self.start_pwm_thread()

        # Wait for ESC to arm
        time.sleep(3)

        self.armed = True
        print("[MOTOR] ESC armed and ready!")

    def set_throttle(self, percent):
        """
        Set throttle as percentage (0-100).
        The PWM thread will continuously output this value.
        """
        if not self.armed:
            print("[MOTOR] Warning: ESC not armed")
            return False

        # Apply safety limit
        percent = max(0, min(percent, MAX_THROTTLE_PERCENT))

        # Convert percentage to pulse width (forward only: 1500-2000us)
        # 0% = 1500us, 100% = 2000us
        pulse_width = int(PWM_NEUTRAL_US + (percent / 100.0) * (PWM_MAX_US - PWM_NEUTRAL_US))

        with self.lock:
            self.current_pulse_width = pulse_width
            self.target_throttle = percent

        print(f"[MOTOR] Throttle set: {percent}% -> {pulse_width}us (continuous)")
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

        # Stop motor first
        with self.lock:
            self.current_pulse_width = PWM_NEUTRAL_US

        time.sleep(0.5)

        # Stop PWM thread
        self.stop_pwm_thread()

        # Turn off PWM output
        if PIGPIO_AVAILABLE and self.pi and self.pi.connected:
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


# ==================== Main ====================

def main():
    print("=" * 50)
    print("TRITON Pi Motor Command Receiver")
    print("Continuous PWM Mode")
    print("=" * 50)
    print(f"LoRa Port: {LORA_PORT}")
    print(f"ESC GPIO: {ESC_GPIO_PIN}")
    print(f"PWM Refresh Rate: {PWM_REFRESH_RATE}Hz")
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
        ser = serial.Serial(LORA_PORT, LORA_BAUD, timeout=0.1)
        print(f"[LORA] Connected to {LORA_PORT} at {LORA_BAUD} baud")
    except Exception as e:
        print(f"[ERROR] Failed to open serial port: {e}")
        return 1

    # Arm the ESC (this also starts the PWM thread)
    motor.arm()

    print("\n" + "=" * 50)
    print("[READY] Listening for commands...")
    print("Motor will spin CONTINUOUSLY at set throttle")
    print("Commands: THROTTLE:<0-100>, STOP, ESTOP")
    print("Press Ctrl+C to exit")
    print("=" * 50 + "\n")

    # Command queue for thread-safe serial reading
    command_queue = Queue()

    def serial_reader():
        """Separate thread for reading serial data."""
        while motor.running:
            try:
                if ser.in_waiting:
                    line = ser.readline().decode(errors='ignore').strip()
                    if line:
                        command_queue.put(line)
            except Exception as e:
                print(f"[SERIAL] Read error: {e}")
            time.sleep(0.02)

    # Start serial reader thread
    reader_thread = threading.Thread(target=serial_reader, daemon=True)
    reader_thread.start()

    try:
        while True:
            # Process commands from queue
            try:
                line = command_queue.get(timeout=0.1)
                print(f"[RX] {line}")

                # Parse command
                cmd_type, value = parse_command(line)

                if cmd_type is None:
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

                # Send acknowledgment
                if response:
                    ser.write((response + "\n").encode())
                    ser.flush()
                    print(f"[TX] {response}")

                # Print current status
                status = motor.get_status()
                print(f"[STATUS] Throttle: {status['throttle']}% | PWM: {status['pulse_width']}us")

            except Empty:
                pass
            except Exception as e:
                print(f"[ERROR] {e}")

    except KeyboardInterrupt:
        print("\n[INFO] Shutting down...")

    finally:
        motor.cleanup()
        ser.close()
        print("[INFO] Goodbye!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
