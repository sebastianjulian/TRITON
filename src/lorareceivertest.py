import serial

# Replace COM3 with your actual port, if different
ser = serial.Serial('COM8', 9600, timeout=1)

print("Listening for LoRa messages...")
while True:
    if ser.in_waiting:
        data = ser.readline().decode(errors='ignore').strip()
        print("Received:", data)
