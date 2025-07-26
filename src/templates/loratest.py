import serial
import time

# Öffne die serielle Verbindung
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)

# AT-Befehl senden
ser.write(b'AT\r\n')

# Antwort lesen
response = ser.read(64)
print("Antwort vom Modul):", response.decode (errors='ignore'))

ser.close()