"""
ESC Control Module for TRITON Submarine
Controls brushless motors via PWM signals to ESC (Electronic Speed Controller)

Hardware: APISQUEEN 2-4S 30A Brushless ESC / Quicrun WP10BL120
Connection: ESC signal wire -> GPIO pin, ESC ground -> RPi GND

Usage:
    sudo pigpiod  # Start pigpio daemon first
    python3 esc_control.py
"""

import pigpio
import time

# Configuration
ESC_PIN = 18  # GPIO pin connected to ESC signal wire

# PWM pulse widths (microseconds)
PWM_MIN = 1000   # Minimum throttle (motor off)
PWM_NEUTRAL = 1500  # Neutral position
PWM_MAX = 2000   # Maximum throttle

class ESCController:
    def __init__(self, pin=ESC_PIN):
        self.pin = pin
        self.pi = pigpio.pi()

        if not self.pi.connected:
            raise RuntimeError("Failed to connect to pigpio daemon. Run 'sudo pigpiod' first.")

        self.armed = False
        print(f"ESC Controller initialized on GPIO {self.pin}")

    def arm(self):
        """Arm the ESC by sending minimum throttle signal"""
        print("Arming ESC...")
        self.pi.set_servo_pulsewidth(self.pin, PWM_MIN)
        time.sleep(2)
        self.armed = True
        print("ESC armed and ready")

    def calibrate(self):
        """
        Calibrate ESC throttle range.
        Run this with ESC powered off, then power on ESC when prompted.
        """
        print("=== ESC Calibration Mode ===")
        print("1. Disconnect battery from ESC")
        print("2. Press Enter when ready...")
        input()

        print("Sending maximum throttle signal...")
        self.pi.set_servo_pulsewidth(self.pin, PWM_MAX)

        print("3. Connect battery to ESC now")
        print("4. Wait for calibration beeps, then press Enter...")
        input()

        print("Sending minimum throttle signal...")
        self.pi.set_servo_pulsewidth(self.pin, PWM_MIN)

        print("5. Wait for confirmation beeps...")
        time.sleep(3)

        print("Calibration complete!")
        self.armed = True

    def set_throttle(self, percent):
        """
        Set motor throttle.

        Args:
            percent: Throttle percentage (0-100)
        """
        if not self.armed:
            print("Warning: ESC not armed. Call arm() first.")
            self.arm()

        # Clamp value to valid range
        percent = max(0, min(100, percent))

        # Map 0-100% to PWM_MIN-PWM_MAX microseconds
        pulse = PWM_MIN + (percent * (PWM_MAX - PWM_MIN) / 100)
        pulse = int(pulse)

        self.pi.set_servo_pulsewidth(self.pin, pulse)
        print(f"Throttle: {percent}% (pulse: {pulse}μs)")

    def set_pulse(self, microseconds):
        """
        Set PWM pulse width directly.

        Args:
            microseconds: Pulse width in microseconds (1000-2000)
        """
        microseconds = max(PWM_MIN, min(PWM_MAX, microseconds))
        self.pi.set_servo_pulsewidth(self.pin, microseconds)
        print(f"Pulse width: {microseconds}μs")

    def stop(self):
        """Stop the motor (minimum throttle)"""
        self.pi.set_servo_pulsewidth(self.pin, PWM_MIN)
        print("Motor stopped")

    def brake(self):
        """Emergency stop - cuts PWM signal entirely"""
        self.pi.set_servo_pulsewidth(self.pin, 0)
        print("Emergency brake - PWM signal disabled")

    def cleanup(self):
        """Clean up GPIO and stop pigpio"""
        self.pi.set_servo_pulsewidth(self.pin, 0)
        self.pi.stop()
        print("ESC Controller cleaned up")


def test_esc():
    """Basic ESC test sequence"""
    print("=" * 50)
    print("TRITON ESC Control Test")
    print("=" * 50)
    print("\nWARNING: Remove propeller before testing!")
    print("Press Enter to continue or Ctrl+C to cancel...")

    try:
        input()
    except KeyboardInterrupt:
        print("\nTest cancelled.")
        return

    esc = ESCController()

    try:
        # Arm the ESC
        esc.arm()

        # Test sequence
        print("\n--- Test Sequence ---")

        print("\nTesting 10% throttle for 3 seconds...")
        esc.set_throttle(10)
        time.sleep(3)

        print("\nTesting 20% throttle for 3 seconds...")
        esc.set_throttle(20)
        time.sleep(3)

        print("\nTesting 30% throttle for 2 seconds...")
        esc.set_throttle(30)
        time.sleep(2)

        print("\nStopping motor...")
        esc.stop()
        time.sleep(1)

        print("\n--- Test Complete ---")

    except KeyboardInterrupt:
        print("\nTest interrupted!")
    finally:
        esc.stop()
        esc.cleanup()


def interactive_control():
    """Interactive ESC control mode"""
    print("=" * 50)
    print("TRITON Interactive ESC Control")
    print("=" * 50)
    print("\nCommands:")
    print("  0-100  : Set throttle percentage")
    print("  a      : Arm ESC")
    print("  c      : Calibrate ESC")
    print("  s      : Stop motor")
    print("  b      : Emergency brake")
    print("  q      : Quit")
    print("\nWARNING: Remove propeller before testing!")

    esc = ESCController()

    try:
        while True:
            cmd = input("\n> ").strip().lower()

            if cmd == 'q':
                break
            elif cmd == 'a':
                esc.arm()
            elif cmd == 'c':
                esc.calibrate()
            elif cmd == 's':
                esc.stop()
            elif cmd == 'b':
                esc.brake()
            elif cmd.isdigit():
                throttle = int(cmd)
                if 0 <= throttle <= 100:
                    esc.set_throttle(throttle)
                else:
                    print("Throttle must be 0-100")
            else:
                print("Unknown command. Use 0-100, a, c, s, b, or q")

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        esc.stop()
        esc.cleanup()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        interactive_control()
    else:
        test_esc()
