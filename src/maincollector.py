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
    
    verbose = False

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
    # Position : sensor : Variable : Einheit : Schwelle : Runden
    # [0]   :  -         :  t    :  s   :   -   : -   # time since start in seconds
    # [1]   :  bme280    :  temp :  °C  :   0.1 : 2
    # [2]   :  bme280    :  humi :  %   :   0.5 : 1
    # [3]   :  bme280    :  rehu :  %   :   0.5 : 1
    # [4]   :  bme280    :  press   hPa :   0.1 : 2
    # [5]   :  bme280    :  alti    m   :   0.5 : 1
    # [6]   :  mpu6050   :  xgyr    °/s :   1   : 0
    # [7]   :  mpu6050   :  ygyr    °/s :   1   : 0
    # [8]   :  mpu6050   :  zgyr    °/s :   1   : 0
    # [9]   :  mpu6050   :  xacc    g   :   0.1 : 2
    # [10]  :  mpu6050   :  yacc    g   :   0.1 : 2
    # [11]  :  mpu6050   :  zacc    g   :   0.1 : 2
    # [12]  :  mpu6050   :  temp    °   :   0.1 : 2
    
    i = 0
    iPrev = i
    lastReport = 0.0
    while True:
        
        try:
            
            if False: #i % 2 == 0:
                try:
                    bme280sensor.getData (data = data, offset = 1)
                    
                except Exception as e:
                    print("failed to read bme280 sensor")
                    print(e)
        
            else:
                try:
                    mpu6050sensor.getData(data = data, offset = 6)
                except Exception as e:
                    print("failed to read mpu6050 sensor ")
                    print(e)
            
            # set current timestamp in seconds since start
            # (this makes plotting graphs simpler as compared to using date/time strings)
            data[0] = round((time.monotonic_ns() - t0_ns) / 1e9, 3)
            
            # write data array to file
            line = f"{datetime.now(timezone.utc).isoformat()},{data[0]:8.3f},{data[1]:8.3f},{data[2]:8.3f},{data[3]:8.3f},{data[4]:8.3f},{data[5]:8.3f},{data[6]:8.3f},{data[7]:8.3f},{data[8]:8.3f},{data[9]:8.3f},{data[10]:8.3f},{data[11]:8.3f},{data[12]:8.3f}"
            file.write(f"{line}\n")
            #file.flush()
            
            # print data to console
            if verbose: print(line, end='\r')
            
            #time.sleep(1)
            
        except Exception as e:

            print("something went wrong")
            print(e)

        finally:

            i += 1
            dt = data[0] - lastReport
            if dt > 1.0:
                print(f"\n[MAIN] i = {i:10} | {((i - iPrev)/dt):10.1f} iterations/s")
                lastReport = data[0]
                iPrev = i

                #raise Exception("haha")

            
    # cleanup
    # print(f"Collected temperature and pressure data with timestamps saved to {filename}.")   
    # file.close()
    
        
        
    
    
# The following block ensures that the 'main()' function is only called
# if the script is executed as the main program, not if it is imported as a module.
if __name__ == "__main__":
    main()  