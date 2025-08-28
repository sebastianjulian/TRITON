from MPU6050 import MPU6050, GyroRange, AccelerationRange

import numpy as np
import time

sensor = MPU6050(
    gyro_range = GyroRange.RANGE_2000,
    accel_range = AccelerationRange.RANGE_16
    )

data = np.zeros(13)
last = np.zeros(13)
deltas = np.array([1.0, 0.1, 0.5, 0.5, 0.1, 0.5, 1.0, 1.0, 1.0, 0.1, 0.1, 0.1, 0.5])
max = np.zeros(7)

t0 = time.perf_counter()
while True:
    
    sensor.get_data(data, offset = 6)
    
    data[0] = time.perf_counter() - t0
    
    diff = np.abs(data - last)
    
    if np.any(diff > deltas):
        line = ", ".join([f"{value:10.3f}" for value in data])
        print(line, end = '\r')
        last[:] = data
        
        
        