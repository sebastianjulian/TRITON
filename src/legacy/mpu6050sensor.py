#!/usr/bin/python
isRealSensor = False

try:
    import smbus
    isRealSensor = True
except:
    print("[mpu6050sensor] failed to load sensor libs -> generating random data instead")
        
import math
import numpy as np
import random
import struct
import time
from datetime import datetime, timezone


bus = None
address = 0x68 # I2C address

REGISTER_GYRO_CONFIG        = 0x1b
REGISTER_ACCEL_CONFIG       = 0x1c
REGISTER_PWR_MGMT_1         = 0x6b
REGISTER_SIGNAL_PATH_RESET  = 0x68

GYRO_CONFIG_250  = 0b00000000 #    ±  250 °/s
GYRO_CONFIG_500  = 0b00001000 #    ±  500 °/s
GYRO_CONFIG_1000 = 0b00010000 #    ± 1000 °/s
GYRO_CONFIG_2000 = 0b00011000 #    ± 2000 °/s

ACCEL_CONFIG_2   = 0b00000000 #    ±  2 g
ACCEL_CONFIG_4   = 0b00001000 #    ±  4 g
ACCEL_CONFIG_8   = 0b00010000 #    ±  8 g
ACCEL_CONFIG_16  = 0b00011000 #    ± 16 g

scale0_gyro =  250.0 / 32768  #scale factors of gyroscope
scale1_gyro =  500.0 / 32768
scale2_gyro = 1000.0 / 32768
scale3_gyro = 2000.0 / 32768

scale0_accl =    2.0 / 32768  #scale factors of accelerometer
scale1_accl =    4.0 / 32768
scale2_accl =    8.0 / 32768
scale3_accl =   16.0 / 32768

def read_word(reg):  #reading values from register
    high = bus.read_byte_data(address, reg)
    low = bus.read_byte_data(address, reg+1)
    value = (high << 8) + low

    if (value >= 0x8000):
        return -((65535 - value) + 1)
    else:
        return value

def get_distance(a,b):
    return math.sqrt((a*a)+(b*b))

def get_y_rotation(x,y,z):
    radians = math.atan2(x, get_distance(y,z))
    return -math.degrees(radians)

def get_x_rotation(x,y,z):
    radians = math.atan2(y, get_distance(x,z))
    return math.degrees(radians)

def get_z_rotation(x,y,z):
    radians = math.atan2(z, get_distance(x,y))
    return math.degrees(radians)

def get_temperature():
    temp = read_word(0x41)
    return (temp / 340) + 36.53

def init ():
        
    global isRealSensor
    global bus

    if not isRealSensor: 
        return

    try:
        bus = smbus.SMBus(1)
        
        # see https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Register-Map1.pdf
        # page 41
        #   Note:
        #     When using SPI interface, user should use DEVICE_RESET (register 107) as well as
        #     SIGNAL_PATH_RESET (register 104) to ensure the reset is performed properly. The sequence
        #     used should be:
        #     1. Set DEVICE_RESET = 1 (register PWR_MGMT_1)
        #     2. Wait 100ms
        #     3. Set GYRO_RESET = ACCEL_RESET = TEMP_RESET = 1 (register SIGNAL_PATH_RESET)
        #     4. Wait 100ms
        
        # 1. Set DEVICE_RESET = 1 (register PWR_MGMT_1)
        bus.write_byte_data(address, REGISTER_PWR_MGMT_1, 0b10000000)
        # 2. Wait 100ms
        time.sleep(0.100) 
        # 3. Set GYRO_RESET = ACCEL_RESET = TEMP_RESET = 1 (register SIGNAL_PATH_RESET)
        bus.write_byte_data(address, REGISTER_SIGNAL_PATH_RESET, 0b00000111)
        # 4. Wait 100ms
        time.sleep(0.100) 
        #bus.write_byte_data(address, 0x6b, 0)  #initialize MPU
       
        # switch off SLEEP
        bus.write_byte_data(address, REGISTER_PWR_MGMT_1,   0b00000000)
        bus.write_byte_data(address, REGISTER_GYRO_CONFIG,  GYRO_CONFIG_250)
        bus.write_byte_data(address, REGISTER_ACCEL_CONFIG, ACCEL_CONFIG_2)
       
        print(f"REGISTER_PWR_MGMT_1   -> {bus.read_byte_data(address, REGISTER_PWR_MGMT_1)}")
        print(f"REGISTER_GYRO_CONFIG  -> {bus.read_byte_data(address, REGISTER_GYRO_CONFIG)}")
        print(f"REGISTER_ACCEL_CONFIG -> {bus.read_byte_data(address, REGISTER_ACCEL_CONFIG)}")
        
        scale0_gyro = 131.0  #scale factors of gyroscope
        scale1_gyro = 65.5
        scale2_gyro = 32.8
        scale3_gyro = 16.4

        scale0_accl = 16384.0  #scale factors of accelerometer
        scale1_accl = 8192.0
        scale2_accl = 4096.0
        scale3_accl = 2048.0

        print(f"[MPU6050 sensor] FOUND")

    except Exception as e:
        print(f"[MPU6050 sensor] {e}")
        isRealSensor = False

def getData (data, offset):
    
    if isRealSensor:
        # Perform a burst read starting from ACCEL_XOUT_H through GYRO_ZOUT_L
        # This reads the accelerometer data (6 bytes), temperature data (2 bytes),
        # and gyroscope data (6 bytes) for a total of 14 bytes
        buffer = bus.read_i2c_block_data(0x68, 0x3B, 14)
        
        # Unpack the 14 bytes using struct
        accel_x, accel_y, accel_z, temp, gyro_x, gyro_y, gyro_z = struct.unpack(">hhhhhhh", bytes(buffer))
    
        data[offset + 0] = round(gyro_x  * scale0_gyro, 0)
        data[offset + 1] = round(gyro_y  * scale0_gyro, 0)
        data[offset + 2] = round(gyro_z  * scale0_gyro, 0)
        data[offset + 3] = round(accel_x * scale0_accl, 2)
        data[offset + 4] = round(accel_y * scale0_accl, 2)
        data[offset + 5] = round(accel_z * scale0_accl, 2)
        data[offset + 6] = round((temp / 340) + 36.53, 2)
        
        # data[offset + 0] = gyroxout = round(read_word(0x43) / scale0_gyro, 0)
        # data[offset + 1] = gyroyout = round(read_word(0x45) / scale0_gyro, 0)
        # data[offset + 2] = gyrozout = round(read_word(0x47) / scale0_gyro, 0)
        # data[offset + 3] = acclxout = round(read_word(0x3b) / scale0_accl, 2)
        # data[offset + 4] = acclyout = round(read_word(0x3d) / scale0_accl, 2)
        # data[offset + 5] = acclzout = round(read_word(0x3f) / scale0_accl, 2)
        # data[offset + 6] = temperature = round(get_temperature(), 2)
        
    
    else:
        if random.random() > 0.9999:
            raise Exception("Simulated I/O error.")
    
        data[offset + 0] = gyroxout = random.uniform(0,1) / scale0_gyro
        data[offset + 1] = gyroyout = random.uniform(0,1) / scale0_gyro
        data[offset + 2] = gyrozout = random.uniform(0,1) / scale0_gyro
        data[offset + 3] = acclxout = random.uniform(0,20) / scale0_accl
        data[offset + 4] = acclyout = random.uniform(0,20) / scale0_accl
        data[offset + 5] = acclzout = random.uniform(0,20) / scale0_accl
        data[offset + 6] = temperature = random.uniform(-10,40)
    
   
#         while True:
  
#         temperature = get_temperature()

#         #print("measured temperature: %.2f \xb0C" % get_temperature())

#         #print()

#         gyro_xout = read_word(0x43)  #reading gyroscope values
#         gyro_yout = read_word(0x45)
#         gyro_zout = read_word(0x47)

#         gyro_xout_scaled = gyro_xout / scale0_gyro  #scaled gyroscope values
#         gyro_yout_scaled = gyro_yout / scale0_gyro
#         gyro_zout_scaled = gyro_zout / scale0_gyro

#         #print("Gyroscope with scale factor " + str(scale0_gyro) + ":")
#         #print("x-axis: %.4f arcsec" % gyro_xout_scaled)
#         #print("y-axis: %.4f arcsec" % gyro_yout_scaled)
#         #print("z-axis: %.4f arcsec" % gyro_zout_scaled)

#         #print()

#         accl_xout = read_word(0x3b)  #reading accelerometer values
#         accl_yout = read_word(0x3d)
#         accl_zout = read_word(0x3f)

#         accl_xout_scaled = accl_xout / scale0_accl  #scaled accelerometer values
#         accl_yout_scaled = accl_yout / scale0_accl
#         accl_zout_scaled = accl_zout / scale0_accl

#         #print("Acceleration with scale factor " + str(scale0_accl) + ":")
#         #print("x-axis: %.4f g" % accl_xout_scaled)
#         #print("y-axis: %.4f g" % accl_yout_scaled)
#         #print("z-axis: %.4f g" % accl_zout_scaled)

#         #print()

#         rotX = get_x_rotation(accl_xout_scaled, accl_yout_scaled, accl_zout_scaled)
#         rotY = get_y_rotation(accl_xout_scaled, accl_yout_scaled, accl_zout_scaled)
#         rotZ = get_z_rotation(accl_xout_scaled, accl_yout_scaled, accl_zout_scaled)

#         #print("Rotation:")
#         #print("x-axis: %.4f \xb0" % get_x_rotation(accl_xout_scaled, accl_yout_scaled, accl_zout_scaled))
#         #print("y-axis: %.4f \xb0" % get_y_rotation(accl_xout_scaled, accl_yout_scaled, accl_zout_scaled))
#         #print("z-axis: %.4f \xb0" % get_z_rotation(accl_xout_scaled, accl_yout_scaled, accl_zout_scaled))
#         #print("------------------------------------------------")

#         print(f"gyro {gyro_xout_scaled:10.0f} {gyro_yout_scaled:10.0f} {gyro_zout_scaled:10.0f} | acceleration {accl_xout_scaled:10.2f} {accl_yout_scaled:10.2f} {accl_zout_scaled:10.2f} | rot {rotX:5.0f} {rotY:5.0f} {rotZ:5.0f} | {temperature:10.1f} °C", end='\r')

#         #time.sleep(0.05)


# '''
