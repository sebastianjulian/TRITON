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
import time


bus = None
address = 0x68 # I2C address

scale0_gyro = 131.0  #scale factors of gyroscope
scale1_gyro = 65.5
scale2_gyro = 32.8
scale3_gyro = 16.4

scale0_accl = 16384.0  #scale factors of accelerometer
scale1_accl = 8192.0
scale2_accl = 4096.0
scale3_accl = 2048.0

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
        
        global bus
        
        if not isRealSensor: 
                return

        bus = smbus.SMBus(1)
        bus.write_byte_data(address, 0x6b, 0)  #initialize MPU

        scale0_gyro = 131.0  #scale factors of gyroscope
        scale1_gyro = 65.5
        scale2_gyro = 32.8
        scale3_gyro = 16.4

        scale0_accl = 16384.0  #scale factors of accelerometer
        scale1_accl = 8192.0
        scale2_accl = 4096.0
        scale3_accl = 2048.0

        print("MPU6050")
        print("------------------------------------------------")

def getData (data, offset):
        if isRealSensor:
                data[offset + 0] = read_word(0x43) / scale0_gyro
                data[offset + 1] = read_word(0x45) / scale0_gyro
                data[offset + 2] = read_word(0x47) / scale0_gyro
                data[offset + 3] = read_word(0x3b) / scale0_accl
                data[offset + 4] = read_word(0x3d) / scale0_accl
                data[offset + 5] = read_word(0x3f) / scale0_accl
                data[offset + 6] = get_temperature()
        else:
                if random.random() > 0.95:
                    raise Exception("Simulated I/O error.")
            
                data[offset + 0] = random.uniform(0,1) / scale0_gyro
                data[offset + 1] = random.uniform(0,1) / scale0_gyro
                data[offset + 2] = random.uniform(0,1) / scale0_gyro
                data[offset + 3] = random.uniform(0,20) / scale0_accl
                data[offset + 4] = random.uniform(0,20) / scale0_accl
                data[offset + 5] = random.uniform(0,20) / scale0_accl
                data[offset + 6] = random.uniform(-10,40)
    
    
   
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
