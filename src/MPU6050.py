import math
import numpy as np
import random
import struct
import time

from datetime import datetime, timezone
from enum import Enum

class GyroRange(Enum):
    """Gyro sensor range in plus/minus degrees per second [°/s].
    """
    RANGE_250  = 0b00000000 #    ±  250 °/s
    RANGE_500  = 0b00001000 #    ±  500 °/s
    RANGE_1000 = 0b00010000 #    ± 1000 °/s
    RANGE_2000 = 0b00011000 #    ± 2000 °/s
   
class AccelerationRange(Enum):
    """Acceleration sensor range in plus/minus g.
    """
    RANGE_2    = 0b00000000  #    ±  2 g
    RANGE_4    = 0b00001000  #    ±  4 g
    RANGE_8    = 0b00010000  #    ±  8 g
    RANGE_16   = 0b00011000  #    ± 16 g
    
class MPU6050:
    
    _IS_SMBUS_IMPORTED_INITIALIZED = False
    _IS_SMBUS_IMPORTED             = False
    
    REGISTER_GYRO_CONFIG        = 0x1b
    REGISTER_ACCEL_CONFIG       = 0x1c
    REGISTER_PWR_MGMT_1         = 0x6b
    REGISTER_SIGNAL_PATH_RESET  = 0x68
    
    def __init__(
        self,
        smbus = 1,
        i2c_address = 0x68,
        gyro_range = GyroRange.RANGE_250,
        accel_range = AccelerationRange.RANGE_2
        ):
        
        if not MPU6050._IS_SMBUS_IMPORTED_INITIALIZED:
            
            try:
                import smbus
                MPU6050._IS_SMBUS_IMPORTED = True
            except Exception as e:
                print("[MPU6050] failed to import smbus -> generating random data instead")
                print(e)
        
            MPU6050._IS_SMBUS_IMPORTED_INITIALIZED = True
        
        self.i2c_address = i2c_address
        
        try:
            self.bus = smbus.SMBus(1) if MPU6050._IS_SMBUS_IMPORTED else None
        except Exception as e:
            self.bus = None
            print(e)
        
        if self.bus is not None:
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
            self.bus.write_byte_data(self.i2c_address, MPU6050.REGISTER_PWR_MGMT_1, 0b10000000)
            # 2. Wait 100ms
            time.sleep(0.100) 
            # 3. Set GYRO_RESET = ACCEL_RESET = TEMP_RESET = 1 (register SIGNAL_PATH_RESET)
            self.bus.write_byte_data(self.i2c_address, MPU6050.REGISTER_SIGNAL_PATH_RESET, 0b00000111)
            # 4. Wait 100ms
            time.sleep(0.100) 
        
            # switch off SLEEP
            self.bus.write_byte_data(self.i2c_address, MPU6050.REGISTER_PWR_MGMT_1,   0b00000000)
            
            self.bus.write_byte_data(self.i2c_address, MPU6050.REGISTER_GYRO_CONFIG,  gyro_range.value)
            self.bus.write_byte_data(self.i2c_address, MPU6050.REGISTER_ACCEL_CONFIG, accel_range.value)
        
            actual_gyro_range = GyroRange(self.bus.read_byte_data(self.i2c_address, MPU6050.REGISTER_GYRO_CONFIG))
            actual_accel_range = AccelerationRange(self.bus.read_byte_data(self.i2c_address, MPU6050.REGISTER_ACCEL_CONFIG))
            
            print(f"REGISTER_PWR_MGMT_1   -> {self.bus.read_byte_data(self.i2c_address, MPU6050.REGISTER_PWR_MGMT_1)}")
            print(f"REGISTER_GYRO_CONFIG  -> {actual_gyro_range}")
            print(f"REGISTER_ACCEL_CONFIG -> {actual_accel_range}")
            
            print(f"[MPU6050 sensor] FOUND")

            match actual_gyro_range:
                case GyroRange.RANGE_250       : self.scale_gyro  =  250.0 / 32767.0
                case GyroRange.RANGE_500       : self.scale_gyro  =  500.0 / 32767.0
                case GyroRange.RANGE_1000      : self.scale_gyro  = 1000.0 / 32767.0
                case GyroRange.RANGE_2000      : self.scale_gyro  = 2000.0 / 32767.0
                
            match actual_accel_range:
                case AccelerationRange.RANGE_2 : self.scale_accel =    2.0 / 32767.0
                case AccelerationRange.RANGE_4 : self.scale_accel =    4.0 / 32767.0
                case AccelerationRange.RANGE_8 : self.scale_accel =    8.0 / 32767.0
                case AccelerationRange.RANGE_16: self.scale_accel =   16.0 / 32767.0
                
        else:
            
            print("bus is none")

    def get_data(self, data, offset):
        """Read sensor values and write into data (there are 7 values).
        """
        if self.bus is not None:
            # Perform a burst read starting from ACCEL_XOUT_H through GYRO_ZOUT_L
            # This reads the accelerometer data (6 bytes), temperature data (2 bytes),
            # and gyroscope data (6 bytes) for a total of 14 bytes
            buffer = self.bus.read_i2c_block_data(0x68, 0x3B, 14)
            
            # Unpack the 14 bytes using struct
            accel_x, accel_y, accel_z, temp, gyro_x, gyro_y, gyro_z = struct.unpack(">hhhhhhh", bytes(buffer))
        
            data[offset + 0] = gyro_x  * self.scale_gyro
            data[offset + 1] = gyro_y  * self.scale_gyro
            data[offset + 2] = gyro_z  * self.scale_gyro
            data[offset + 3] = accel_x * self.scale_accel
            data[offset + 4] = accel_y * self.scale_accel
            data[offset + 5] = accel_z * self.scale_accel
            data[offset + 6] = (temp / 340.0) + 36.53
        
        else:
            if random.random() > 0.9999:
                raise Exception("Simulated I/O error.")
        
            data[offset + 0] = gyro_x = random.uniform(0,1)   #* self.scale_gyro
            data[offset + 1] = gyro_y = random.uniform(0,1)   #* self.scale_gyro
            data[offset + 2] = gyro_z = random.uniform(0,1)   #* self.scale_gyro
            data[offset + 3] = accel_x = random.uniform(0,20) #* self.scale_accel
            data[offset + 4] = accel_y = random.uniform(0,20) #* self.scale_accel
            data[offset + 5] = accel_z = random.uniform(0,20) #* self.scale_accel
            data[offset + 6] = temp = random.uniform(-10,40)
            
            # data[offset + 0] = gyro_x = random.uniform(0,0) 
            # data[offset + 1] = gyro_y = random.uniform(0,0) 
            # data[offset + 2] = gyro_z = random.uniform(0,0) 
            # data[offset + 3] = accel_x = random.uniform(0,0)
            # data[offset + 4] = accel_y = random.uniform(0,0)
            # data[offset + 5] = accel_z = random.uniform(0,0)
            # data[offset + 6] = temp = random.uniform(-1,0)




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

#         rotX = get_x_rotation(accl_xout_scaled, accl_yout_scaled, accl_zout_scaled)
#         rotY = get_y_rotation(accl_xout_scaled, accl_yout_scaled, accl_zout_scaled)
#         rotZ = get_z_rotation(accl_xout_scaled, accl_yout_scaled, accl_zout_scaled)

