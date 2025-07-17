import time
import board
import busio
import numpy as np
from adafruit_bme280 import basic as adafruit_bme280
from mpu6050 import mpu6050

# Set up I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Set up BME280 sensor (address may be 0x76 or 0x77)
try:
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
    print("BME280 detected.")
except Exception as e:
    print("BME280 not found:", e)
    bme280 = None

# Set up MPU6050 sensor
try:
    mpu = mpu6050(0x68)
    print("MPU6050 detected.")
except Exception as e:
    print("MPU6050 not found:", e)
    mpu = None

# Define NumPy array: [temp, hum, pressure, alt, ax, ay, az, gx, gy, gz, mpu_temp]
data = np.zeros(11)

# Main loop
while True:
    print("\n--- Sensor Readings ---")

    if bme280:
        data[0] = bme280.temperature
        data[1] = bme280.humidity
        data[2] = bme280.pressure
        data[3] = bme280.altitude

    if mpu:
        accel = mpu.get_accel_data()
        gyro = mpu.get_gyro_data()
        data[4] = accel['x']
        data[5] = accel['y']
        data[6] = accel['z']
        data[7] = gyro['x']
        data[8] = gyro['y']
        data[9] = gyro['z']
        data[10] = mpu.get_temp()

    print(data)
    time.sleep(1)
