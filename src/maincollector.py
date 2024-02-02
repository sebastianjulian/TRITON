import asyncio
import math
import numpy as np
import os
import random
import time

import bme280sensor
import mpu6050sensor

from datetime import datetime, timezone

# initializations
bme280sensor.init()
mpu6050sensor.init()
#mpu6050sensor.mpu6050init()

# main function: collects data and saves it
def main():
    
    startTime = datetime.now(timezone.utc)
    t0 = time.monotonic_ns()
    LOGS_DIR = "logs"
     
    t0 = datetime.now(timezone.utc)
    print(f"started at {t0}")
   
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)
    
    filename = os.path.abspath(f"{LOGS_DIR}/sensor_data_{t0.strftime('%Y%m%d%H%M%S')}Z.csv")
    file = open(filename, mode='w', encoding='utf-8')
    file.write(f"Timestamp, Temperature [°C], Humidity [%], Relative Humidity [%], Pressure [hPa], Altitude [m], X-Gyro [°/s], Y-Gyro [°/s],Z-Gyro [°/s], X-Acceleration [g], Y-Acceleration [g], Z-Acceleration [g], X-Rotation [°], Y-Rotation [°], Z-Rotation [°]\n")
    
    print(f"logging to file {filename}")
    # sensor:_data = []

    print(f"start at {startTime.isoformat()}")
    
    data = np.zeros(12)
    
    while True:
        
        try:
            #file = open(filename, mode='w', encoding='utf-8')
            bme280sensor.getData (data = data, offset = 0, file=file)
            
        except Exception as e:
            print("failed to read bme280 sensor")
            print(e)
    
        try:
            #file = open(filename, mode='w', encoding='utf-8')
            mpu6050sensor.getData(data = data, offset = 5, file=file)
        except Exception as e:
            print("failed to read mpu6050 sensor ")
            print(e)
        finally:
            print(f"Collected temperature and pressure data with timestamps saved to {filename}.")
        
            #file.close()
    
        
        print(data)
        
        
        time.sleep(1)
        
        
    
    
# The following block ensures that the 'main()' function is only called
# if the script is executed as the main program, not if it is imported as a module.
if __name__ == "__main__":
    main()  