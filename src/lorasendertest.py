# import serial
# import time

# # Öffne die serielle Verbindung
# ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
# time.sleep(2)

# # AT-Befehl senden
# ser.write(b'AT\r\n')

# # Antwort lesen
# response = ser.read(64)
# print("Antwort vom Modul):", response.decode (errors='ignore'))

# ser.close()
# #test

# import serial
# import time

# ser = serial.Serial('/dev/ttyUSB0', 9600)

# while True:
#     message = "Hello from Raspberry Pi\n"
#     ser.write(message.encode())
#     print("Sent:", message.strip())
#     time.sleep(5)


import serial
import time

# Adjust to your actual port if needed
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

while True:
    message = "Hello from Pi\n"
    ser.write(message.encode())
    print("Sent:", message.strip())

    # Read response from module (if any)
    time.sleep(0.5)
    while ser.in_waiting:
        response = ser.readline().decode(errors='ignore').strip()
        print("Response from module:", response)

    time.sleep(5)
