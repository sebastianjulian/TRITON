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
    t0_ns = time.monotonic_ns()
    LOGS_DIR = "logs"
     
    nowUtc = datetime.now(timezone.utc)
    print(f"started at {nowUtc}")
   
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)
    
    filename = os.path.abspath(f"{LOGS_DIR}/sensor_data_{nowUtc.strftime('%Y%m%d%H%M%S')}Z.csv")
    file = open(filename, mode='w', encoding='utf-8')
    file.write(f"Timestamp, t [s], Temperature [°C], Humidity [%], Relative Humidity [%], Pressure [hPa], Altitude [m], X-Gyro [°/s], Y-Gyro [°/s],Z-Gyro [°/s], X-Acceleration [g], Y-Acceleration [g], Z-Acceleration [g], X-Rotation [°], Y-Rotation [°], Z-Rotation [°]\n")
    
    print(f"logging to file {filename}")
  
    print(f"start at {startTime.isoformat()}")
    
    data = np.zeros(13)
    
    while True:
        
        try:
            
            try:
                bme280sensor.getData (data = data, offset = 1)
                
            except Exception as e:
                print("failed to read bme280 sensor")
                print(e)
        
            try:
                mpu6050sensor.getData(data = data, offset = 6)
            except Exception as e:
                print("failed to read mpu6050 sensor ")
                print(e)
            
            # set current timestamp in seconds since start
            # (this makes plotting graphs simpler as compared to using date/time strings)
            data[0] = (time.monotonic_ns() - t0_ns) / 1e9
            
            # write data array to file
            file.write(f"{datetime.now(timezone.utc).isoformat()},{data[0]},{data[1]},{data[2]},{data[3]},{data[4]},{data[5]},{data[6]},{data[7]},{data[8]},{data[9]},{data[10]},{data[11]},{data[12]}\n")
            file.flush()
            
            # write data array to console
            #print(data)
            
            #time.sleep(1)
            
        except Exception as e:
            print("something went wrong")
            print(e)
            
    # cleanup
    # print(f"Collected temperature and pressure data with timestamps saved to {filename}.")   
    # file.close()
    
        
        
    
    
# The following block ensures that the 'main()' function is only called
# if the script is executed as the main program, not if it is imported as a module.
if __name__ == "__main__":
    main()  