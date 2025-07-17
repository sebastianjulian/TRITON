#import time
#import board
#import busio
#from adafruit_bme280 import basic as adafruit_bme280
#from mpu6050 import mpu6050
#
## I2C bus setup
#i2c = busio.I2C(board.SCL, board.SDA)
#
## BME280 setup (default I2C address is 0x76 or 0x77)
#try:
#    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
#    print("BME280 detected.")
#except Exception as e:
#    print("BME280 not found:", e)
#    bme280 = None
#
## MPU6050 setup
#try:
#    mpu = mpu6050(0x68)
#    print("MPU6050 detected.")
#except Exception as e:
#    print("MPU6050 not found:", e)
#    mpu = None
#
## Loop to read data
#while True:
#    print("\n--- Sensor Readings ---")
#
#    if bme280:
#        print(f"Temperature: {bme280.temperature:.2f} °C")
#        print(f"Humidity: {bme280.humidity:.2f} %")
#        print(f"Pressure: {bme280.pressure:.2f} hPa")
#
#    if mpu:
#        accel = mpu.get_accel_data()
#        gyro = mpu.get_gyro_data()
#        print(f"Accel  (m/s²): x={accel['x']:.2f}, y={accel['y']:.2f}, z={accel['z']:.2f}")
#        print(f"Gyro (°/s):    x={gyro['x']:.2f}, y={gyro['y']:.2f}, z={gyro['z']:.2f}")
#
#    time.sleep(1)
#

import time
import board
import busio
from adafruit_bme280 import basic as adafruit_bme280
from mpu6050 import mpu6050
from MPU6050 import MPU6050, GyroRange, AccelerationRange
from datetime import datetime, timezone
import bme280sensor
import numpy as np
import os
import sys
import threading
import logging
import json
import signal
from busio import I2C
import serial
import termios
import tty
import select
from threading import Timer


# I2C bus setup
i2c = busio.I2C(board.SCL, board.SDA)

data = np.zeros(12)

# BME280 setup (default I2C address is 0x76 or 0x77)
#try:
#    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
#    print("BME280 detected.")
#except Exception as e:
#    print("BME280 not found:", e)
#    bme280 = None
#
## MPU6050 setup
#try:
#    mpu = mpu6050(0x68)
#    print("MPU6050 detected.")
#except Exception as e:
#    print("MPU6050 not found:", e)
#    mpu = None
#
## Loop to read data
#while True:
#    print("\n--- Sensor Readings ---")
#
#    if bme280:
#        print(f"Temperature: {bme280.temperature:.2f} °C")
#        print(f"Humidity: {bme280.humidity:.2f} %")
#        print(f"Pressure: {bme280.pressure:.2f} hPa")
#
#    if mpu:
#        accel = mpu.get_accel_data()
#        gyro = mpu.get_gyro_data()
#        print(f"Accel  (m/s²): x={accel['x']:.2f}, y={accel['y']:.2f}, z={accel['z']:.2f}")
#        print(f"Gyro (°/s):    x={gyro['x']:.2f}, y={gyro['y']:.2f}, z={gyro['z']:.2f}")
#
#    time.sleep(1)


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
                message_payload = "Test123"  # Ensure this is defined or available
                data = bytes([255]) + bytes([255]) + bytes([16]) + bytes([255]) + bytes([255]) + bytes([16]) + message_payload.encode()
                node.send(data)
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