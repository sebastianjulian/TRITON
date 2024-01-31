#!/usr/bin/python
import smbus
import math
import time

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

bus = smbus.SMBus(1)
address = 0x68 # I2C address
bus.write_byte_data(address, 0x6b, 0)  #initialize MPU

scale0_gyroscope = 131.0  #scale factors of gyroscope
scale1_gyroscope = 65.5
scale2_gyroscope = 32.8
scale3_gyroscope = 16.4

scale0_acceleration = 16384.0  #scale factors of accelerometer
scale1_acceleration = 8192.0
scale2_acceleration = 4096.0
scale3_acceleration = 2048.0

print("MPU6050")
print("------------------------------------------------")

while True:
  print("measured temperature: %.2f \xb0C" % get_temperature())
  
  print()
  
  gyroscope_xout = read_word(0x43)  #reading gyroscope values
  gyroscope_yout = read_word(0x45)
  gyroscope_zout = read_word(0x47)
 
  gyroscope_xout_scaled = gyroscope_xout / scale0_gyroscope  #scaled gyroscope values
  gyroscope_yout_scaled = gyroscope_yout / scale0_gyroscope
  gyroscope_zout_scaled = gyroscope_zout / scale0_gyroscope
	
  print("Gyroscope with scale factor " + str(scale0_gyroscope) + ":")
  print("x-axis: %.4f arcsec" % gyroscope_xout_scaled)
  print("y-axis: %.4f arcsec" % gyroscope_yout_scaled)
  print("z-axis: %.4f arcsec" % gyroscope_zout_scaled)
 
  print()
 
  acceleration_xout = read_word(0x3b)  #reading accelerometer values
  acceleration_yout = read_word(0x3d)
  acceleration_zout = read_word(0x3f)

  acceleration_xout_scaled = acceleration_xout / scale0_acceleration  #scaled accelerometer values
  acceleration_yout_scaled = acceleration_yout / scale0_acceleration
  acceleration_zout_scaled = acceleration_zout / scale0_acceleration
 
  print("Acceleration with scale factor " + str(scale0_acceleration) + ":")
  print("x-axis: %.4f g" % acceleration_xout_scaled)
  print("y-axis: %.4f g" % acceleration_yout_scaled)
  print("z-axis: %.4f g" % acceleration_zout_scaled)
 
  print()
 
  print("Rotation:")
  print("x-axis: %.4f \xb0" % get_x_rotation(acceleration_xout_scaled, acceleration_yout_scaled, acceleration_zout_scaled))
  print("y-axis: %.4f \xb0" % get_y_rotation(acceleration_xout_scaled, acceleration_yout_scaled, acceleration_zout_scaled))
  print("z-axis: %.4f \xb0" % get_z_rotation(acceleration_xout_scaled, acceleration_yout_scaled, acceleration_zout_scaled))
  print("------------------------------------------------")
  time.sleep(1) 