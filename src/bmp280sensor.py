#!/usr/bin/python3

isRealSensor = False

try:
    import board
    import busio
    import adafruit_bmp280
    isRealSensor = True
except Exception as e:
    print("[bmp280sensor] failed to load sensor libs -> generating random data instead")
    print(e)
    
import numpy as np
import random

bmp280 = None

def init ():
    
    global isRealSensor
    global bmp280
    
    if not isRealSensor: 
        return
    
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)
       
        # change this to match the location's pressure (hPa) at sea level
        # need to be configured for the real altitude. Check your next Weatherstation for the pressure
        #bme280.sea_level_pressure = 1013.25

        bmp280.mode = adafruit_bmp280.MODE_NORMAL
        
        print(f"[BMP280 sensor] FOUND")

    except Exception as e:
        print(f"[BMP280 sensor] {e}")
        isRealSensor = False

def getData (data, offset):
    
    if isRealSensor:
        
        data[offset + 0] = round(bmp280.temperature, 2)
        data[offset + 1] = round(bmp280.pressure, 2)
        data[offset + 2] = round(bmp280.altitude, 1)

    else:
        
        if random.random() > 0.9999:
            raise Exception("Simulated I/O error.")
        
        data[offset + 0] = round(random.uniform(-10, 40), 2)
        data[offset + 1] = round(random.uniform(950, 1050), 2)
        data[offset + 2] = round(random.uniform(1, 10000), 1)
        