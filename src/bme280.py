#!/usr/bin/python3
import board
import busio
import time
import numpy as np
from adafruit_bme280 import basic as adafruit_bme280

i2c = busio.I2C(board.SCL, board.SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

# change this to match the location's pressure (hPa) at sea level
# need to be configured for the real altitude. Check your next Weatherstation for the pressure
#bme280.sea_level_pressure = 1013.25

bme280.mode = adafruit_bme280.MODE_NORMAL
time.sleep(1)

data = np.zeros(5)
t0 = time.monotonic_ns()

while True:
    temp = bme280.temperature
    hum  = bme280.humidity
    rhum = bme280.relative_humidity
    prs  = bme280.pressure
    alt  = bme280.altitude

    isChanged = False
    if (abs(temp - data[0]) > 0.1): isChanged = True 
    if (abs(hum  - data[1]) > 0.5): isChanged = True
    if (abs(rhum - data[2]) > 0.5): isChanged = True
    if (abs(prs  - data[3]) > 0.2): isChanged = True
    #print("Temperature: %0.1f C" % temp)
    #print("Humidity: %0.1f %%" % hum)
    #print("relative Humidity: %0.1f %%" % rhum)
    #print("absolute Pressure: %0.1f hPa" % prs)
    #print("Altitude = %0.2f meters" % alt)

    if isChanged:
        t = (time.monotonic_ns()-t0)/1000000000.0
        print(f"[{t:10.6f}] {temp:10.1f} °C {hum:10.1f} % {rhum:10.1f} % {prs:10.1f} hPa {alt:10.2f} m")

        data[0] = temp
        data[1] = hum
        data[2] = rhum
        data[3] = prs
        data[4] = alt

    #time.sleep(0.5)
