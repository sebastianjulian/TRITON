# import time
# import board
# import busio
# import numpy as np
# from adafruit_bme280 import basic as adafruit_bme280
# from mpu6050 import mpu6050

# # Set up I2C bus
# i2c = busio.I2C(board.SCL, board.SDA)

# # Set up BME280 sensor (address may be 0x76 or 0x77)
# try:
#     bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
#     print("BME280 detected.")
# except Exception as e:
#     print("BME280 not found:", e)
#     bme280 = None

# # Set up MPU6050 sensor
# try:
#     mpu = mpu6050(0x68)
#     print("MPU6050 detected.")
# except Exception as e:
#     print("MPU6050 not found:", e)
#     mpu = None

# # Define NumPy array: [temp, hum, pressure, alt, ax, ay, az, gx, gy, gz, mpu_temp]
# data = np.zeros(11)

# # Main loop
# while True:
#     print("\n--- Sensor Readings ---")

#     if bme280:
#         data[0] = bme280.temperature
#         data[1] = bme280.humidity
#         data[2] = bme280.pressure
#         data[3] = bme280.altitude

#     if mpu:
#         accel = mpu.get_accel_data()
#         gyro = mpu.get_gyro_data()
#         data[4] = accel['x']
#         data[5] = accel['y']
#         data[6] = accel['z']
#         data[7] = gyro['x']
#         data[8] = gyro['y']
#         data[9] = gyro['z']
#         data[10] = mpu.get_temp()

#     print(data)
#     time.sleep(1)
import time
import board
import busio
import numpy as np
from datetime import datetime
from adafruit_bme280 import basic as adafruit_bme280
from mpu6050 import mpu6050

# Set up I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Try to initialize BME280
try:
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
    print("BME280 detected.")
except Exception as e:
    print("BME280 not found:", e)
    bme280 = None

# Try to initialize MPU6050
try:
    mpu = mpu6050(0x68)
    print("MPU6050 detected.")
except Exception as e:
    print("MPU6050 not found:", e)
    mpu = None

# Data array
data = np.zeros(11)

# CSV file setup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"sensor_data_{timestamp}.csv"
with open(filename, "w") as f:
    f.write("timestamp,temp,humidity,pressure,altitude,ax,ay,az,gx,gy,gz,mpu_temp\n")

# Loop
while True:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if bme280:
        try:
            data[0] = bme280.temperature
            data[1] = bme280.humidity
            data[2] = bme280.pressure
            data[3] = bme280.altitude
        except Exception as e:
            print("[WARNING] BME280 read failed:", e)
            data[0:4] = np.nan

    if mpu:
        try:
            accel = mpu.get_accel_data()
            gyro = mpu.get_gyro_data()
            data[4] = accel['x']
            data[5] = accel['y']
            data[6] = accel['z']
            data[7] = gyro['x']
            data[8] = gyro['y']
            data[9] = gyro['z']
            data[10] = mpu.get_temp()
        except Exception as e:
            print("[WARNING] MPU6050 read failed:", e)
            data[4:11] = np.nan

    # Print to console
    print(data)

    # Write to file
    with open(filename, "a") as f:
        values = ",".join(f"{v:.2f}" if not np.isnan(v) else "NaN" for v in data)
        f.wri
