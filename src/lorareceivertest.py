import serial

ser = serial.Serial('COM8', 9600, timeout=1)
print("🔍 Listening for full LoRa messages...")

buffer = ""

while True:
    if ser.in_waiting:
        try:
            line = ser.readline().decode(errors='ignore').strip()
            if line and line.count(",") >= 12:  # Expect 13 data values
                print("📥", line)
                with open("received_lora_data.csv", "a") as f:
                    f.write(line + "\n")
            else:
                print("⚠️ Incomplete or malformed line:", line)
        except Exception as e:
            print("[ERROR] Read failed:", e)
