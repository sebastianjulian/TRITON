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


def find_throttle_range(pi):
    """
    Interactive test to find the actual working throttle range.
    Steps through pulse widths and asks user when motor responds.
    """
    print("\n" + "=" * 50)
    print("         THROTTLE RANGE FINDER")
    print("=" * 50)
    print("\nThis will help find your ESC's actual throttle range.")
    print("Watch the motor and tell me when it starts/stops spinning.")

    input("\nPress Enter to start...")

    # Start at neutral
    print("\nSetting NEUTRAL (1500 us)...")
    pi.set_servo_pulsewidth(ESC_GPIO_PIN, 1500)
    time.sleep(2)

    # Test forward range
    print("\n--- TESTING FORWARD RANGE ---")
    print("I'll increase throttle in steps of 25 us.")
    print("Tell me the pulse width where the motor STARTS spinning.\n")

    forward_start = None
    for pulse in range(1500, 2001, 25):
        print("Pulse: {} us".format(pulse), end="", flush=True)
        pi.set_servo_pulsewidth(ESC_GPIO_PIN, pulse)
        time.sleep(0.8)
        response = input(" - Motor spinning? (y/n/q to quit): ").strip().lower()
        if response == 'y' and forward_start is None:
            forward_start = pulse
            print("  -> Motor starts at {} us".format(pulse))
        elif response == 'q':
            break

    # Return to neutral
    print("\nReturning to NEUTRAL...")
    pi.set_servo_pulsewidth(ESC_GPIO_PIN, 1500)
    time.sleep(2)

    # Test reverse range (with double-tap for car ESCs)
    print("\n--- TESTING REVERSE RANGE ---")
    print("Car ESCs need 'double-tap' for reverse.")
    print("I'll do: brake -> neutral -> reverse\n")

    input("Press Enter to test reverse...")

    # Double-tap sequence: brake first
    print("Step 1: Sending BRAKE signal (1250 us)...")
    pi.set_servo_pulsewidth(ESC_GPIO_PIN, 1250)
    time.sleep(1)

    print("Step 2: Back to NEUTRAL (1500 us)...")
    pi.set_servo_pulsewidth(ESC_GPIO_PIN, 1500)
    time.sleep(0.5)

    print("Step 3: Now testing REVERSE...")
    reverse_start = None
    for pulse in range(1500, 999, -25):
        print("Pulse: {} us".format(pulse), end="", flush=True)
        pi.set_servo_pulsewidth(ESC_GPIO_PIN, pulse)
        time.sleep(0.8)
        response = input(" - Motor spinning backward? (y/n/q to quit): ").strip().lower()
        if response == 'y' and reverse_start is None:
            reverse_start = pulse
            print("  -> Reverse starts at {} us".format(pulse))
        elif response == 'q':
            break

    # Return to neutral
    print("\nReturning to NEUTRAL...")
    pi.set_servo_pulsewidth(ESC_GPIO_PIN, 1500)
    time.sleep(1)

    # Summary
    print("\n" + "=" * 50)
    print("         RANGE FINDER RESULTS")
    print("=" * 50)
    if forward_start:
        print("Forward starts at: {} us".format(forward_start))
    else:
        print("Forward start: Not detected")
    if reverse_start:
        print("Reverse starts at: {} us".format(reverse_start))
    else:
        print("Reverse start: Not detected")
    print("\nUpdate the MAX_FORWARD and MAX_REVERSE values in the")
    print("script if these differ from 2000/1000.")


def test_motor(pi):
    """Run a smooth motor test sequence with proper reverse handling."""
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

    # REVERSE with double-tap (required for car ESCs)
    print("\n--- REVERSE TEST (with double-tap) ---")

    # Step 1: Send brake signal first
    print("Step 1: Sending BRAKE signal (1300 us)...")
    pi.set_servo_pulsewidth(ESC_GPIO_PIN, 1300)
    time.sleep(1)

    # Step 2: Return to neutral briefly
    print("Step 2: Brief NEUTRAL (1500 us)...")
    pi.set_servo_pulsewidth(ESC_GPIO_PIN, NEUTRAL_PULSE)
    time.sleep(0.3)

    # Step 3: Now reverse will work
    print("Step 3: Engaging REVERSE...")

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


def manual_control(pi):
    """Manually set pulse width for testing."""
    print("\n" + "=" * 50)
    print("         MANUAL PULSE CONTROL")
    print("=" * 50)
    print("\nEnter pulse widths manually to test ESC response.")
    print("Valid range: 1000-2000 us (1500 = neutral)")
    print("Type 'q' to quit.\n")

    # Start at neutral
    pi.set_servo_pulsewidth(ESC_GPIO_PIN, 1500)
    print("Current: 1500 us (NEUTRAL)")

    while True:
        try:
            value = input("\nEnter pulse width (1000-2000) or 'q': ").strip()
            if value.lower() == 'q':
                break

            pulse = int(value)
            if 1000 <= pulse <= 2000:
                pi.set_servo_pulsewidth(ESC_GPIO_PIN, pulse)
                if pulse < 1500:
                    pct = (1500 - pulse) / 5
                    print("Set to {} us ({:.0f}% REVERSE)".format(pulse, pct))
                elif pulse > 1500:
                    pct = (pulse - 1500) / 5
                    print("Set to {} us ({:.0f}% FORWARD)".format(pulse, pct))
                else:
                    print("Set to {} us (NEUTRAL)".format(pulse))
            else:
                print("Invalid range. Use 1000-2000.")
        except ValueError:
            print("Invalid input. Enter a number or 'q'.")

    # Return to neutral
    print("\nReturning to NEUTRAL...")
    pi.set_servo_pulsewidth(ESC_GPIO_PIN, 1500)


def main_menu(pi):
    """Display main menu and handle user choice."""
    while True:
        print("\n" + "=" * 50)
        print("     ESC CALIBRATION & TEST UTILITY")
        print("     Hobbywing Quicrun WP 10BL 120 G2")
        print("=" * 50)
        print("\n  1. Calibrate ESC (do this first!)")
        print("  2. Run motor test (forward + reverse)")
        print("  3. Find throttle range (interactive)")
        print("  4. Manual pulse control")
        print("  5. Calibrate ESC, then run motor test")
        print("  6. Exit")

        choice = input("\nEnter your choice (1-6): ").strip()

        if choice == "1":
            calibrate_esc(pi)
        elif choice == "2":
            test_motor(pi)
        elif choice == "3":
            find_throttle_range(pi)
        elif choice == "4":
            manual_control(pi)
        elif choice == "5":
            calibrate_esc(pi)
            print("\nWaiting 3 seconds before motor test...")
            time.sleep(3)
            test_motor(pi)
        elif choice == "6":
            print("\nExiting...")
            break
        else:
            print("Invalid choice. Please enter 1-6.")


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
