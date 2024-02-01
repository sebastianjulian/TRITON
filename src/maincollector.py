# all imports
import asyncio
import os
import random
import smbus2
import bme280
import math
import smbus
import numpy as np
import board
import busio
import time
from adafruit_bme280 import basic as adafruit_bme280
import bme280sensor
import mpu6050sensor



# initializations
bme280sensor.bme280init()
mpu6050sensor.mpu6050init()



# main function: collects data and saves it
def main ():
    bme280sensor.bme280main()
    mpu6050sensor.mpu6050main()
    
main()
