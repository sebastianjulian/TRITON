import bme280sensor
#import bmp280sensor
import numpy as np
import os
import sys
import time
import threading

import time
import logging
import json
import signal
import sys
import os
import board
from busio import I2C
import serial

from datetime import datetime, timezone
from MPU6050 import MPU6050, GyroRange, AccelerationRange


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
        
data = np.zeros(12)
        
is_lora_send_thread_running = False

print("BEFORE LORA INIT")
LORA_SERIAL_DEVICE = '/dev/serial0'
LORA_SERIAL_BAUD_RATE = 9600
lora = serial.Serial(LORA_SERIAL_DEVICE, baudrate=LORA_SERIAL_BAUD_RATE, timeout=3.0)
print("AFTER LORA INIT")


def lora_send ():
    
    try:
        global data
        global is_lora_send_thread_running
        is_lora_send_thread_running = True
        
        ### TODO replace this test code with actual lora send code
        print(f"[LORA SEND TEST] START")
        for i in range(5):
            time.sleep(1.0)
            # print(f"[LORA SEND TEST] {i}")
        print(f"[LORA SEND TEST] STOP")
        ### TODO END
            
    except Exception as e:
        print("[ERROR] lora_send failed")
        print(e)
        
    finally:
        is_lora_send_thread_running = False
        
        
def main():
    # VARIABLES, LOG-FILES, ...
    verbose = False
    if "-v" in sys.argv:
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
    file.write(f"Timestamp, t [s], Temperature [°C], Humidity [%], Pressure [hPa], Altitude [m], X-Gyro [°/s], Y-Gyro [°/s],Z-Gyro [°/s], X-Acceleration [g], Y-Acceleration [g], Z-Acceleration [g], Temperature [°C]\n")
    if verbose:
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
    global data
    last = np.zeros(12)
    deltas = np.array([1.0, 0.1, 0.5, 0.1, 0.5, 1.0, 1.0, 1.0, 0.1, 0.1, 0.1, 0.1])
    
    minAlt = sys.float_info.max
    maxAlt = -sys.float_info.max
    
    if verbose:
        print(f"Deltas: {deltas}")
    
    # 7) List for minimal difference between recorded values (from collected data) so that values are written into the file
    # Position : sensor : Variable : Einheit : Schwelle : Runden
    # [ 0]  :  -         :  t    :  s   :   -   : -   # time since start in seconds
    # [ 1]  :  bme280    :  temp :  °C  :   0.1 : 2
    # [ 2]  :  bme280    :  humi :  %   :   0.5 : 1
    # [ 3]  :  bme280    :  press   hPa :   0.1 : 2
    # [ 4]  :  bme280    :  alti    m   :   0.5 : 1
    # [ 5]  :  mpu6050   :  xgyr    °/s :   1   : 0
    # [ 6]  :  mpu6050   :  ygyr    °/s :   1   : 0
    # [ 7]  :  mpu6050   :  zgyr    °/s :   1   : 0
    # [ 8]  :  mpu6050   :  xacc    g   :   0.1 : 2
    # [ 9]  :  mpu6050   :  yacc    g   :   0.1 : 2
    # [10]  :  mpu6050   :  zacc    g   :   0.1 : 2
    # [11]  :  mpu6050   :  temp    °   :   0.1 : 2
    
    # 8) Iteration counter
    i = 0
    iPrev = i
    lastReport = 0.0
    nextSendTime = 0.5
    
    
    # NEVER ENDING LOOP
    # Start of never ending loop
    while True:
        
        try:
            
            ##################################################################################
            # (1) read BME280 sensor
            try:
                # 10) Gets data from BME280 sensor and checks if the minimal difference is fulfilled -> if yes, writes data into files
                bme280sensor.getData (data = data, offset = 1)   # start at 1, index 0 is timestamp
                #bmp280sensor.getData (data = data, offset = 1)
                                          
                # if data[0] > nextSendTime:
                #     print("SENDING")
                #     file.write("SENDING")
                #     nextSendTime += 0.5
            
            except Exception as e:
                print("[ERROR] Failed to read BME280-sensor")
                print(e)
            
            ##################################################################################
            # (2) read MPU6050 sensor
            try:
                # 11) Gets data from MPU6050 sensor and checks if the minimal difference is fulfilled -> if yes, writes data into files
                mpu6050.get_data(data = data, offset = 5)
               
            except Exception as e:
                print("[ERROR] Failed to read MPU6050-sensor")
                print(e)
              
            ##################################################################################
            # (3) set current timestamp in seconds since start
            # (this makes plotting graphs simpler as compared to using date/time strings)
            data[0] = time.perf_counter() - t0
            
            ##################################################################################
            # (4) write data array to file
            try:
                line = f"{datetime.now(timezone.utc).isoformat()},{data[0]:8.3f},{data[1]:8.3f},{data[2]:8.3f},{data[3]:8.3f},{data[4]:8.3f},{data[5]:8.3f},{data[6]:8.3f},{data[7]:8.3f},{data[8]:8.3f},{data[9]:8.3f},{data[10]:8.3f},{data[11]:8.3f}"
                file.write(f"{line}\n")
                file.flush()
            except Exception as e:
                print("[ERROR] File write failed.")
                print(e)
                
            ##################################################################################
            # (5) print data to console
            if verbose:
                diff = data - last
                if np.any(diff > deltas):
                    last[:] = data
                    print(line, end='\r')
            
            ##################################################################################
            # (6) send data to ground station via LORA
            try:
                global is_lora_send_thread_running
                if not is_lora_send_thread_running:
                    t = threading.Thread(target=lora_send)
                    t.start()
                    if verbose:
                        print("[MAIN] started LORA send thread")
                
            except Exception as e:
                print("[ERROR] Lora send failed.")
                print(e)

            ##################################################################################

            try:
                print("BEFORE LORA SEND")
                lora.write('test'.encode('utf-8'))
                print("AFTER LORA SEND")
            except Exception as e:
                print("LORA SEND ERROR")
                print(e)
                print(e)
                print("test")

        
            


            ##################################################################################
                
            # with open(Config.SENSOR_DATA_FILE, 'a') as self.data_file:
            #     while self.running:
            #         data = self.read_sensor_data()
            #         self.write_data_to_file(data)
            #         self.write_data_to_lora(data)
                    
            ##################################################################################
            # (n) print separation altitude each time there is a new min/max altitude
            if verbose:
                if data[4] > maxAlt:
                    maxAlt = data[4]
                    sepAlt = maxAlt - minAlt
                    print(f"Altitude of separation: {sepAlt}")
                    
                if data[4] < minAlt:
                    minAlt = data[4]
                    sepAlt = maxAlt - minAlt
                    print(f"Altitude of separation: {sepAlt}")

        except Exception as e:

            print("[ERROR] Something else went wrong in the main function.")
            print(e)
            
        finally:
            
            try:
                i += 1
                dt = data[0] - lastReport
                if dt > 1.0: # .. 1 second
                    if verbose:
                        print(f"\n[MAIN] i = {i:10} | {((i - iPrev)/dt):10.1f} iterations/s")
                    lastReport = data[0]
                    iPrev = i
            except:
                pass

            
    # cleanup (which we NEVER reach)
    # print(f"Collected temperature and pressure data with timestamps saved to {filename}.")   
    # file.close()
    
        
        
    
    
# The following block ensures that the 'main()' function is only called
# if the script is executed as the main program, not if it is imported as a module.
if __name__ == "__main__":
    main()  

