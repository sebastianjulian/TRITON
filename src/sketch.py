from MPU6050 import MPU6050, GyroRange, AccelerationRange

import numpy as np

sensor = MPU6050(
    gyro_range = GyroRange.RANGE_2000,
    accel_range = AccelerationRange.RANGE_16
    )

data = np.zeros(7)
max = np.zeros(7)

while True:
    
    sensor.get_data(data, offset = 0)
    
    max = np.maximum(data, max)
    
    line = ", ".join([f"{value:10.3f}" for value in max])
    print(line, end = '\r')