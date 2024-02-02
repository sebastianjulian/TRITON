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

    print(f"start at {startTime.isoformat()}")
    
    data = np.zeros(12)
    
    while True:
        
        try:
            bme280sensor.getData (data = data, offset = 0)
        except Exception as e:
            print("failed to read bme280 sensor")
            print(e)
    
        try:
            mpu6050sensor.getData(data = data, offset = 5)
        except Exception as e:
            print("failed to read mpu6050 sensor ")
            print(e)
    
        print(data)
        
        time.sleep(1)
        
        
    
    
# The following block ensures that the 'main()' function is only called
# if the script is executed as the main program, not if it is imported as a module.
if __name__ == "__main__":
    main()  