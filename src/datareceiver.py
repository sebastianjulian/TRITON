import serial as ser, serial
import os
import numpy as np
from datetime import timezone, datetime
import time
import random
import sys

'''
# try:
#     ser = serial.Serial('/dev/ttyUSB0', 9600)
# except Exception:
#     print("could not set connection")
startTime = datetime.now(timezone.utc)
t0_ns = time.monotonic_ns()
LOGS_DIR = "logs"
nowUtc = datetime.now(timezone.utc)
print(f"Data receiving started at {nowUtc}")

if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

filename = os.path.abspath(f"{LOGS_DIR}/sensor_data_{nowUtc.strftime('%Y%m%d%H%M%S')}Z.csv")
file = open(filename, mode='w', encoding='utf-8')
file.write(f"Timestamp, t [s], Temperature [°C], Humidity [%], Relative Humidity [%], Pressure [hPa], Altitude [m], X-Gyro [°/s], Y-Gyro [°/s],Z-Gyro [°/s], X-Acceleration [g], Y-Acceleration [g], Z-Acceleration [g], X-Rotation [°], Y-Rotation [°], Z-Rotation [°]\n")

print(f"logging to file {filename}")

print(f"start at {startTime.isoformat()}")

# data = np.zeros(13)
def random_data (offset):
    data = np.zeros(13)
    scale0_gyro = 131.0  #scale factors of gyroscope
    scale0_accl = 16384.0 
    data[offset + 0] = temperature = round(random.uniform(-10, 40), 2)
    data[offset + 1] = humidity = round(random.uniform(0, 100), 1)
    data[offset + 2] = relative_humidity = round(random.uniform(0, 100), 1)
    data[offset + 3] = pressure = round(random.uniform(950, 1050), 2)
    data[offset + 4] = altitude = round(random.uniform(1, 10000), 1)
    data[offset + 5] = gyroxout = random.uniform(0,1) / scale0_gyro
    data[offset + 6] = gyroyout = random.uniform(0,1) / scale0_gyro
    data[offset + 7] = gyrozout = random.uniform(0,1) / scale0_gyro
    data[offset + 8] = acclxout = random.uniform(0,20) / scale0_accl
    data[offset + 9] = acclyout = random.uniform(0,20) / scale0_accl
    data[offset + 10] = acclzout = random.uniform(0,20) / scale0_accl
    data[offset + 11] = temperature = random.uniform(-10,40)
    print(data)

def main ():
    while True:
        try:
            random_data(offset = 0)
            time.sleep(1)
        except Exception as e:
            print("Random data could not be generated")
            print(e)
        try:
            output_file_name = sys.argv[1]

            # Open the file in write mode to redirect stdout
            with open(file, 'w') as file:
            # Redirect stdout to both the console and the file
                sys.stdout = sys.__stdout__  # Reset stdout to default (console)
                #sys.stdout = Tee(sys.stdout, output_file) 
            # sys.stdout = sys.__stdout__  # Reset stdout to default (console)
            # sys.stdout = (sys.stdout, file)
            # print(sys.stdout)
            # # received_data = ser.readline().decode('utf8').strip()
            # # data = received_data.split(',')
            # # file.write(f"{data}\n")
        except Exception as e:
            print("Something went wrong")
            print(e)
        
if __name__ == "__main__":
    main()  
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
