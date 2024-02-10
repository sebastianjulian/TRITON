import asyncio
import bme280sensor
from datetime import datetime, timezone
import math
from MPU6050 import MPU6050, GyroRange, AccelerationRange
import mpu6050sensor
import numpy as np
import os
import random
import time
#import bmp280sensor





# MAIN FUNCTION:

    # VARIABLES, LOG-FILES, ...
        # 1) Prints when data gathering begins
        # 2) Starts time(counter)
        # 3) Checks if directory exists -> if not, creates one
        # 4) Creates log file for collected data with timestamp, so that files are not overwritten
        
    # SENSOR INITIALIZATION 
        # 5) Initializes sensors
        # 6) creates data array (for recorded data), last array (for calculating minimal differences between recorded values), deltas array (for minial difference values)
        # 7) List for minimal difference between recorded values (from collected data) so that values are written into the file
        # 8) Iteration counter
        
    # NEVERENDING LOOP
        # 9) Start of neverending loop
        # 10) Gets data from BME280 sensor and checks if the minimal difference is fulfilled -> if yes, writes data into files
        # 11) Gets data from MPU6050 sensor and checks if the minimal difference is fulfilled -> if yes, writes data into files
        
def main():
    # VARIABLES, LOG-FILES, ...
    verbose = True

    # 1) Prints when data gathering begins
    startTime = datetime.now(timezone.utc)
    print(f"[MAIN] started at {startTime.isoformat()}")
    
    # 2) Starts time(counter)
    t0 = time.perf_counter()
    
    # 3) Checks if directory exists -> if not, creates one
    # 4) Creates log file for collected data with timestamp, so that files are not overwritten
    LOGS_DIR = "logs"
    nowUtc = datetime.now(timezone.utc)
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)
    filename = os.path.abspath(f"{LOGS_DIR}/sensor_data_{nowUtc.strftime('%Y%m%d%H%M%S')}Z.csv")
    file = open(filename, mode='w', encoding='utf-8')
    file.write(f"Timestamp, t [s], Temperature [°C], Humidity [%], Relative Humidity [%], Pressure [hPa], Altitude [m], X-Gyro [°/s], Y-Gyro [°/s],Z-Gyro [°/s], X-Acceleration [g], Y-Acceleration [g], Z-Acceleration [g], X-Rotation [°], Y-Rotation [°], Z-Rotation [°]\n")
    print(f"[MAIN] logging to file {filename}")
  
    
    
    # SENSOR INITIALIZATION 
    # 5) Initializes sensors
    bme280sensor.init()
    #bmp280sensor.init()
    #mpu6050sensor.init()
    mpu6050 = MPU6050(
        gyro_range = GyroRange.RANGE_2000,
        accel_range = AccelerationRange.RANGE_16
        )
    
    # 6) Creates data array (for recorded data), last array (for calculating minimal differences between recorded values), deltas array (for minial difference values)
    data = np.zeros(13)
    last = np.zeros(13)
    deltas = np.array([0.0, 0.1, 0.5, 0.5, 0.1, 0.5, 1.0, 1.0, 1.0, 0.1, 0.1, 0.1, 0.1])
    # deltas = np.array([0.5, 0.1, 0.5, 0.5, 0.1, 0.5, 1.0, 1.0, 1.0, 0.1, 0.1, 0.1, 0.1])
    # deltas += 10
    
    print(f"Deltas: {deltas}")
    
    # 7) List for minimal difference between recorded values (from collected data) so that values are written into the file
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
    
    # 8) Iteration counter
    i = 0
    iPrev = i
    lastReport = 0.0
    nextSendTime = 0.5
    
    # NEVERENDING LOOP
    # Start of neverending loop
    while True:
        
        try:
            
            try:
                # 10) Gets data from BME280 sensor and checks if the minimal difference is fulfilled -> if yes, writes data into files
                bme280sensor.getData (data = data, offset = 1)
                #bmp280sensor.getData (data = data, offset = 1)
                
                # diff = data - last
                # if np.any(diff > deltas):
                #     last[:] = data
                #     line = f"{datetime.now(timezone.utc).isoformat()},{data[0]:8.3f},{data[1]:8.3f},{data[2]:8.3f},{data[3]:8.3f},{data[4]:8.3f},{data[5]:8.3f},{data[6]:8.3f},{data[7]:8.3f},{data[8]:8.3f},{data[9]:8.3f},{data[10]:8.3f},{data[11]:8.3f},{data[12]:8.3f}"
                #     file.write(f"{line}\n")
                
                
                

                
                if data[0] > nextSendTime:
                    print("SENDING")
                    file.write("SENDING")
                    nextSendTime += 0.5
            
            except Exception as e:
                print("[MAIN] failed to read bme280 sensor")
                print(e)
            
            try:
                # 11) Gets data from MPU6050 sensor and checks if the minimal difference is fulfilled -> if yes, writes data into files
                mpu6050.get_data(data = data, offset = 6)
                # diff = data - last
                # if np.any(diff > deltas):
                #     last[:] = data
                #     line = f"{datetime.now(timezone.utc).isoformat()},{data[0]:8.3f},{data[1]:8.3f},{data[2]:8.3f},{data[3]:8.3f},{data[4]:8.3f},{data[5]:8.3f},{data[6]:8.3f},{data[7]:8.3f},{data[8]:8.3f},{data[9]:8.3f},{data[10]:8.3f},{data[11]:8.3f},{data[12]:8.3f}"
                #     file.write(f"{line}\n")
            except Exception as e:
                print("Something went wrong")
                print(e)
            # try: 
            #     passedTime = data[0] - last[0]
            #     if passedTime >= 0.5:
            #         # SEND DATA VIA LORA-MODULE
            #         print("SENDING")
            #         file.write("SENDING")
            #         pass
            # except Exception as e:
            #     print("Something went wrong with SENDING")
            #     print(e)
                
        
            # try:
            #     mpu6050sensor.getData(data = data, offset = 6)
            # except Exception as e:
            #     print("[MAIN] failed to read mpu6050 sensor ")
            #     print(e)
            
            # set current timestamp in seconds since start
            # (this makes plotting graphs simpler as compared to using date/time strings)
            data[0] = time.perf_counter() - t0
            
            # write data array to file
            # line = f"{datetime.now(timezone.utc).isoformat()},{data[0]:8.3f},{data[1]:8.3f},{data[2]:8.3f},{data[3]:8.3f},{data[4]:8.3f},{data[5]:8.3f},{data[6]:8.3f},{data[7]:8.3f},{data[8]:8.3f},{data[9]:8.3f},{data[10]:8.3f},{data[11]:8.3f},{data[12]:8.3f}"
            # file.write(f"{line}\n")
            #file.flush()
            
            # print data to console
            if verbose: print(line, end='\r')
            
            #time.sleep(1)
                        
        except Exception as e:

            print("something went wrong")
            print(e)
            

        finally:
            diff = data - last
            if np.any(diff > deltas):
                last[:] = data
                line = f"{datetime.now(timezone.utc).isoformat()},{data[0]:8.3f},{data[1]:8.3f},{data[2]:8.3f},{data[3]:8.3f},{data[4]:8.3f},{data[5]:8.3f},{data[6]:8.3f},{data[7]:8.3f},{data[8]:8.3f},{data[9]:8.3f},{data[10]:8.3f},{data[11]:8.3f},{data[12]:8.3f}"
                file.write(f"{line}\n")
                
                
                
            i += 1
            dt = data[0] - lastReport
            if dt > 1.0: # .. 1 second
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