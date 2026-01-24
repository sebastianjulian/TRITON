#!/usr/bin/env python3
"""
Brushless Motor Control for TRITON
Controls Apisqueen brushless motor via Hobbywing Quicrun WP10BL120 ESC

Hardware Setup:
- ESC signal wire (white/yellow) -> GPIO 18 (PWM0)
- ESC ground wire (black/brown) -> Pi GND
- ESC power from 3S LiPo (connected directly to ESC)

PWM Configuration:
- Frequency: 50Hz (standard RC servo/ESC)
- Pulse width: 1000µs (full reverse) - 1500µs (neutral) - 2000µs (full forward)
"""

import pigpio
import time
import sys
import subprocess
import os

# Configuration
ESC_GPIO_PIN = 18  # GPIO 18 supports hardware PWM (PWM0)

# PWM pulse widths in microseconds
PWM_MIN = 1000      # Full reverse (or brake depending on ESC mode)
PWM_NEUTRAL = 1500  # Neutral/Stop
PWM_MAX = 2000      # Full forward

# Safety limits (percentage of max throttle)
MAX_THROTTLE_PERCENT = 50  # Limit max speed for safety during testing


def ensure_pigpiod_running():
    """Start pigpiod daemon if not already running."""
    # Check if pigpiod is running
    try:
        result = subprocess.run(
            ["pgrep", "-x", "pigpiod"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("pigpiod already running")
            return True
    except FileNotFoundError:
        pass  # pgrep not available, try to start anyway

    # Try to start pigpiod
    print("Starting pigpiod daemon...")
    try:
        result = subprocess.run(
            ["sudo", "pigpiod"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            time.sleep(0.5)  # Give daemon time to initialize
            print("pigpiod started successfully")
            return True
        else:
            print(f"Failed to start pigpiod: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error starting pigpiod: {e}")
        return False


class MotorController:
    """Controls brushless motor via ESC using PWM signals."""

    def __init__(self, gpio_pin=ESC_GPIO_PIN):
        self.gpio_pin = gpio_pin
        self.pi = None
        self.armed = False

    def connect(self):
        """Connect to pigpio daemon, starting it if necessary."""
        ensure_pigpiod_running()

        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError(
                "Failed to connect to pigpio daemon. "
                "Try running manually: sudo pigpiod"
            )
        print(f"Connected to pigpio daemon")
        print(f"Using GPIO pin {self.gpio_pin} for ESC control")

    def arm(self):
        """
        Arm the ESC by sending neutral signal.
        ESC must receive neutral signal before it will respond to throttle.
        """
        print("Arming ESC...")
        print("Sending neutral signal (1500µs)...")
        self.set_pulse_width(PWM_NEUTRAL)
        time.sleep(2)  # Wait for ESC to recognize neutral
        self.armed = True
        print("ESC armed and ready")

    def set_pulse_width(self, pulse_width_us):
        """Set PWM pulse width in microseconds."""
        # Clamp to valid range
        pulse_width_us = max(PWM_MIN, min(PWM_MAX, pulse_width_us))
        self.pi.set_servo_pulsewidth(self.gpio_pin, pulse_width_us)

    def set_throttle(self, percent):
        """
        Set throttle as percentage.

        Args:
            percent: -100 (full reverse) to +100 (full forward), 0 = neutral
        """
        if not self.armed:
            print("Warning: ESC not armed. Call arm() first.")
            return

        # Apply safety limit
        if abs(percent) > MAX_THROTTLE_PERCENT:
            percent = MAX_THROTTLE_PERCENT if percent > 0 else -MAX_THROTTLE_PERCENT
            print(f"Throttle limited to {percent}% for safety")

        # Convert percentage to pulse width
        # 0% = 1500µs, +100% = 2000µs, -100% = 1000µs
        if percent >= 0:
            pulse_width = PWM_NEUTRAL + (percent / 100.0) * (PWM_MAX - PWM_NEUTRAL)
        else:
            pulse_width = PWM_NEUTRAL + (percent / 100.0) * (PWM_NEUTRAL - PWM_MIN)

        self.set_pulse_width(int(pulse_width))
        print(f"Throttle: {percent}% -> Pulse: {int(pulse_width)}µs")

    def stop(self):
        """Stop the motor (set to neutral)."""
        print("Stopping motor...")
        self.set_pulse_width(PWM_NEUTRAL)

    def cleanup(self):
        """Clean up GPIO and stop motor."""
        print("\nCleaning up...")
        if self.pi and self.pi.connected:
            self.set_pulse_width(PWM_NEUTRAL)
            time.sleep(0.5)
            self.pi.set_servo_pulsewidth(self.gpio_pin, 0)  # Turn off PWM
            self.pi.stop()
        print("Cleanup complete")


def interactive_control():
    """Interactive motor control for testing."""
    controller = MotorController()

    try:
        controller.connect()

        print("\n" + "="*50)
        print("MOTOR CONTROL - Interactive Mode")
        print("="*50)
        print(f"Max throttle limited to {MAX_THROTTLE_PERCENT}% for safety")
        print("\nCommands:")
        print("  [number]  - Set throttle (-100 to 100)")
        print("  s         - Stop (neutral)")
        print("  a         - Arm ESC")
        print("  t         - Test sequence")
        print("  q         - Quit")
        print("="*50 + "\n")

        controller.arm()

        while True:
            try:
                cmd = input("\nThrottle > ").strip().lower()

                if cmd == 'q':
                    break
                elif cmd == 's':
                    controller.stop()
                elif cmd == 'a':
                    controller.arm()
                elif cmd == 't':
                    # Test sequence: ramp up and down
                    print("Running test sequence...")
                    for throttle in [10, 20, 30, 20, 10, 0]:
                        controller.set_throttle(throttle)
                        time.sleep(1)
                    controller.stop()
                    print("Test sequence complete")
                else:
                    try:
                        throttle = float(cmd)
                        controller.set_throttle(throttle)
                    except ValueError:
                        print("Invalid command. Enter a number or s/a/t/q")

            except KeyboardInterrupt:
                break

    except Exception as e:
        print(f"Error: {e}")

    finally:
        controller.cleanup()


def simple_test():
    """Simple test: spin motor briefly then stop."""
    controller = MotorController()

    try:
        controller.connect()
        controller.arm()

        print("\nStarting motor at 20% throttle for 3 seconds...")
        controller.set_throttle(20)
        time.sleep(3)

        print("Stopping motor...")
        controller.stop()
        time.sleep(1)

    finally:
        controller.cleanup()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        simple_test()
    else:
        interactive_control()
