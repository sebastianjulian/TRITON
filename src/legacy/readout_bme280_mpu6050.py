import time
import board
import busio
from adafruit_bme280 import basic as adafruit_bme280
from mpu6050 import mpu6050
import numpy as np


# I2C bus setup
i2c = busio.I2C(board.SCL, board.SDA)

# BME280 setup (default I2C address is 0x76 or 0x77)
try:
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
    print("BME280 detected.")
except Exception as e:
    print("BME280 not found:", e)
    bme280 = None

# MPU6050 setup
try:
    mpu = mpu6050(0x68)
    print("MPU6050 detected.")
except Exception as e:
    print("MPU6050 not found:", e)
    mpu = None

# Loop to read data

data = np.zeros(9)

#(Temperature [°C], Humidity [%], Pressure [hPa], X-Acceleration [g], Y-Acceleration [g], Z-Acceleration [g], X-Gyro [°/s], Y-Gyro [°/s],Z-Gyro [°/s],)
deltas = np.array([0.1, 0.5, 0.1, 0.1, 0.1, 0.1, 1.0, 1.0, 1.0])   




while True:
    print("\n--- Sensor Readings ---")

    if bme280:
        print(f"Temperature: {bme280.temperature:.2f} °C")
        print(f"Humidity: {bme280.humidity:.2f} %")
        print(f"Pressure: {bme280.pressure:.2f} hPa")
        data[offset = 0] = bme280.temperature:.2f
        data[offset = 1] = bme280.humidity:.2f
        data[offset = 2] = bme280.pressure:.2f
        

    if mpu:
        accel = mpu.get_accel_data()
        gyro = mpu.get_gyro_data()
        print(f"Accel  (m/s²): x={accel['x']:.2f}, y={accel['y']:.2f}, z={accel['z']:.2f}")
        print(f"Gyro (°/s):    x={gyro['x']:.2f}, y={gyro['y']:.2f}, z={gyro['z']:.2f}")
        data[offset = 3] = accel['x']:.2f
        data[offset = 4] = accel['y']:.2f
        data[offset = 5] = accel['z']:.2f
        data[offset = 6] = gyro['x']:.2f
        data[offset = 7] = gyro['y']:.2f
        data[offset = 8] = gyro['z']:.2f

    print(data)



    time.sleep(1)
  
  
  
  
  #data[offset + 5] = accel_z * self.scale_accel
  #data[offset + 2] = round(bme280.pressure, 2)