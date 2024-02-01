'''
import board
import busio
import adafruit_bme280

i2c = busio.I2C(board.SCL, board.SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

print("Temperature: {:.2f} C".format(bme280.temperature))
print("Humidity: {:.2f} %".format(bme280.humidity))
print("Pressure: {:.2f} hPa".format(bme280.pressure))
'''
#!/usr/bin/python3
import board
import busio
import time


from adafruit_bme280 import basic as adafruit_bme280

i2c = busio.I2C(board.SCL, board.SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

# change this to match the location's pressure (hPa) at sea level
# need to be configured for the real altitude. Check your next Weatherstation for the pressure
#bme280.sea_level_pressure = 1013.25

bme280.mode = adafruit_bme280.MODE_NORMAL
time.sleep(1)

print("Temperature: %0.1f C" % bme280.temperature)
print("Humidity: %0.1f %%" % bme280.humidity)
print("relative Humidity: %0.1f %%" % bme280.relative_humidity)
print("absolute Pressure: %0.1f hPa" % bme280.pressure)
print("Altitude = %0.2f meters" % bme280.altitude)
