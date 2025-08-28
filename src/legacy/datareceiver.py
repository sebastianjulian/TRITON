'''
import serial

# Replace 'COMx' with the appropriate serial port your LoRa module is connected to
# ser = serial.Serial('COMx', 9600)  

# Replace 'output.txt' with the desired file name
output_file = open('output.txt', 'w')
for i in range (10):
    data = random.random()
    print(data)
try:
    while True:
        # Read a line from the serial port
        line = ser.readline().decode('utf-8').strip()

        # Check if the line is not empty
        if line:
            # Split the line into values using commas
            values = line.split(',')

            # Print the values to the console
            print("Received values:", values)

            # Save the values to the file
            output_file.write(','.join(values) + '\n')

except KeyboardInterrupt:
    # Close the serial port and the output file when interrupted by the user
    ser.close()
    output_file.close()
'''
import os
from datetime import datetime, timezone
LOGS_DIR = "logs"
nowUtc = datetime.now(timezone.utc)
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)
filename = os.path.abspath(f"{LOGS_DIR}/sensor_data_{nowUtc.strftime('%Y%m%d%H%M%S')}Z.csv")
file = open(filename, mode='w', encoding='utf-8')
file.write(f"Timestamp, t [s], Temperature [°C], Humidity [%], Relative Humidity [%], Pressure [hPa], Altitude [m], X-Gyro [°/s], Y-Gyro [°/s],Z-Gyro [°/s], X-Acceleration [g], Y-Acceleration [g], Z-Acceleration [g], X-Rotation [°], Y-Rotation [°], Z-Rotation [°]\n")
