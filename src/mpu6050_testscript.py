from mpu6050 import mpu6050

sensor = mpu6050(0x77)  # Address may vary, run i2cdetect -y 1 to find the correct address

accel_data = sensor.get_accel_data()
gyro_data = sensor.get_gyro_data()

print("Accelerometer data: ", accel_data)
print("Gyroscope data: ", gyro_data)
