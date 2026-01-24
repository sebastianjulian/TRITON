import pigpio
import time

# --- Configuration ---
ESC_GPIO_PIN = 18

# Pulse widths for ESC control
NEUTRAL_PULSE = 1500      # 0% throttle (stopped)
MAX_FORWARD = 2000        # 100% Forward
MAX_REVERSE = 1000        # 100% Reverse

# Smoother ramp settings (slower, smaller steps)
RAMP_DELAY = 0.03         # Time between steps (longer = smoother)
RAMP_STEP_SIZE = 5        # Smaller steps for smoother acceleration

# Hold times (longer to let motor stabilize)
HOLD_TIME = 3             # Seconds to hold at each throttle level


def connect_pigpio():
    """Connect to pigpio daemon."""
    pi = pigpio.pi()
    if not pi.connected:
        print("Could not connect to pigpio daemon. Is it running?")
        print("Try: sudo pigpiod")
        exit()
    pi.set_mode(ESC_GPIO_PIN, pigpio.OUTPUT)
    return pi


def calibrate_esc(pi):
    """
    Calibrate the ESC by teaching it the throttle range.
    This must be done with the ESC powered OFF initially.
    """
    print("\n" + "=" * 50)
    print("         ESC CALIBRATION MODE")
    print("=" * 50)
    print("\nThis will calibrate your Hobbywing Quicrun ESC.")
    print("\nSTEP 1: Disconnect the battery from the ESC")
    input("        Press Enter when battery is disconnected...")

    # Send max throttle BEFORE powering ESC
    print("\nSending MAX throttle signal ({} us)...".format(MAX_FORWARD))
    pi.set_servo_pulsewidth(ESC_GPIO_PIN, MAX_FORWARD)
    time.sleep(1)

    print("\nSTEP 2: Connect the battery to the ESC NOW")
    print("        Listen for the ESC startup tones...")
    input("        Press Enter after you hear the beeps...")

    # Send neutral to set the low point
    print("\nSending NEUTRAL signal ({} us)...".format(NEUTRAL_PULSE))
    pi.set_servo_pulsewidth(ESC_GPIO_PIN, NEUTRAL_PULSE)
    time.sleep(2)

    print("\nSTEP 3: You should hear confirmation beeps")
    print("        (Usually a musical tone or series of beeps)")
    time.sleep(1)

    print("\n" + "=" * 50)
    print("         CALIBRATION COMPLETE")
    print("=" * 50)
    print("\nYour ESC now knows:")
    print("  - Full throttle = {} us".format(MAX_FORWARD))
    print("  - Neutral       = {} us".format(NEUTRAL_PULSE))
    print("  - Full reverse  = {} us".format(MAX_REVERSE))


def ramp_to(pi, start_pulse, end_pulse, description):
    """Smoothly ramp from one pulse width to another."""
    print(description)

    if start_pulse < end_pulse:
        step = RAMP_STEP_SIZE
    else:
        step = -RAMP_STEP_SIZE

    current = start_pulse
    while (step > 0 and current <= end_pulse) or (step < 0 and current >= end_pulse):
        pi.set_servo_pulsewidth(ESC_GPIO_PIN, current)
        time.sleep(RAMP_DELAY)
        current += step

    # Ensure we end exactly at target
    pi.set_servo_pulsewidth(ESC_GPIO_PIN, end_pulse)


def test_motor(pi):
    """Run a smooth motor test sequence."""
    print("\n" + "=" * 50)
    print("         MOTOR TEST SEQUENCE")
    print("=" * 50)
    print("\n--- SAFETY WARNING ---")
    print("Make sure propellers are REMOVED!")
    print("Press Ctrl+C at any time to stop.")
    print("-" * 25)

    input("\nPress Enter to start the motor test...")

    # Ensure we start at neutral
    print("\nSetting NEUTRAL ({} us)...".format(NEUTRAL_PULSE))
    pi.set_servo_pulsewidth(ESC_GPIO_PIN, NEUTRAL_PULSE)
    time.sleep(2)

    # Test 1: Ramp to 50% forward
    ramp_to(pi, NEUTRAL_PULSE, 1750, "\nRamping to 50% FORWARD (1750 us)...")
    print("Holding at 50% forward for {} seconds...".format(HOLD_TIME))
    time.sleep(HOLD_TIME)

    # Test 2: Ramp to 100% forward
    ramp_to(pi, 1750, MAX_FORWARD, "\nRamping to 100% FORWARD ({} us)...".format(MAX_FORWARD))
    print("Holding at 100% forward for {} seconds...".format(HOLD_TIME))
    time.sleep(HOLD_TIME)

    # Test 3: Ramp back to neutral
    ramp_to(pi, MAX_FORWARD, NEUTRAL_PULSE, "\nRamping back to NEUTRAL...")
    print("Holding at neutral for {} seconds...".format(HOLD_TIME))
    time.sleep(HOLD_TIME)

    # Test 4: Ramp to 50% reverse
    ramp_to(pi, NEUTRAL_PULSE, 1250, "\nRamping to 50% REVERSE (1250 us)...")
    print("Holding at 50% reverse for {} seconds...".format(HOLD_TIME))
    time.sleep(HOLD_TIME)

    # Test 5: Ramp to 100% reverse
    ramp_to(pi, 1250, MAX_REVERSE, "\nRamping to 100% REVERSE ({} us)...".format(MAX_REVERSE))
    print("Holding at 100% reverse for {} seconds...".format(HOLD_TIME))
    time.sleep(HOLD_TIME)

    # Test 6: Return to neutral
    ramp_to(pi, MAX_REVERSE, NEUTRAL_PULSE, "\nRamping back to NEUTRAL...")
    print("Test complete!")


def main_menu(pi):
    """Display main menu and handle user choice."""
    while True:
        print("\n" + "=" * 50)
        print("     ESC CALIBRATION & TEST UTILITY")
        print("     Hobbywing Quicrun WP 10BL 120 G2")
        print("=" * 50)
        print("\n  1. Calibrate ESC (do this first if never calibrated)")
        print("  2. Run motor test")
        print("  3. Calibrate ESC, then run motor test")
        print("  4. Exit")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            calibrate_esc(pi)
        elif choice == "2":
            test_motor(pi)
        elif choice == "3":
            calibrate_esc(pi)
            print("\nWaiting 3 seconds before motor test...")
            time.sleep(3)
            test_motor(pi)
        elif choice == "4":
            print("\nExiting...")
            break
        else:
            print("Invalid choice. Please enter 1-4.")


if __name__ == "__main__":
    pi = connect_pigpio()

    try:
        main_menu(pi)

    except KeyboardInterrupt:
        print("\n\nCtrl+C detected. Stopping motor...")

    finally:
        # Safety: always return to neutral and clean up
        print("\nSafety shutdown: Setting motor to NEUTRAL...")
        pi.set_servo_pulsewidth(ESC_GPIO_PIN, NEUTRAL_PULSE)
        time.sleep(1)

        # Stop PWM signal
        pi.set_servo_pulsewidth(ESC_GPIO_PIN, 0)

        # Disconnect
        pi.stop()
        print("GPIO cleanup complete. Goodbye!")
