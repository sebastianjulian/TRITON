#!/usr/bin/python3

isRealSensor = False

try:
    import board
    import busio
    from adafruit_bme280 import basic as adafruit_bme280
    isRealSensor = True
except:
    print("[bme280sensor] failed to load sensor libs -> generating random data instead")
    
import numpy as np
import random
import time
from datetime import datetime, timezone

bme280 = None

def init ():
    
    global isRealSensor
    global bme280
    
    if not isRealSensor: 
        return
    
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

        # change this to match the location's pressure (hPa) at sea level
        # need to be configured for the real altitude. Check your next Weatherstation for the pressure
        bme280.sea_level_pressure = 993.9
        bme280.mode = adafruit_bme280.MODE_NORMAL
        
        print(f"[BME280 sensor] FOUND")

    except Exception as e:
        print(f"[BME280 sensor] {e}")
        isRealSensor = False

def getData (data, offset = 1):
    '''Writes 4 values (temperature, humidity, pressure, altitude) into data array,
       starting at index offset.'''
    
    if isRealSensor:
        
        data[offset + 0] = round(bme280.temperature, 2)
        data[offset + 1] = round(bme280.humidity, 1)
        data[offset + 2] = round(bme280.pressure, 2)
        data[offset + 3] = round(bme280.altitude, 1)

    else:
        
        # if random.random() > 0.9999:
        #     raise Exception("Simulated I/O error.")
        
        data[offset + 0] = round(random.uniform(-10, 40), 2)
        data[offset + 1] = round(random.uniform(0, 100), 1)
        data[offset + 2] = round(random.uniform(950, 1050), 2)
        data[offset + 3] = round(random.uniform(1, 10000), 1)
