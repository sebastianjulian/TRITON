import time
import logging
import json
import signal
import sys
import serial
import os
import board
from busio import I2C
import adafruit_bme680 as bme680

class Config:
    LOG_FILE = os.getenv('SENSOR_SERVICE_LOG_FILE', '/var/log/sensor_service.log')
    SENSOR_READ_INTERVAL = float(os.getenv('SENSOR_READ_INTERVAL', '1.0'))
    SENSOR_DATA_FILE = os.getenv('SENSOR_DATA_FILE', '/var/log/sensor_data.txt')
    PRESSURE_AT_SEALEVEL = float(os.getenv('PRESSURE_AT_SEALEVEL', '1013.25'))
    TEMPERATURE_OFFSET = int(os.getenv('TEMPERATURE_OFFSET', '0'))
    LORA_SERIAL_DEVICE = os.getenv('LORA_SERIAL_DEVICE', '/dev/serial0')
    LORA_SERIAL_BAUD_RATE = int(os.getenv('LORA_SERIAL_BAUD_RATE', '9600'))

logging.basicConfig(filename=Config.LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class SensorService:
    def __init__(self):
        self.sensor = self.initialize_bme680()
        self.lora = self.initialize_lora()
        self.running = True
        self.data_file = None
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, sig, frame):
        logging.info('Sensor service is stopping')
        self.running = False

    def run(self):
        with open(Config.SENSOR_DATA_FILE, 'a') as self.data_file:
            while self.running:
                data = self.read_sensor_data()
                self.write_data_to_file(data)
                self.write_data_to_lora(data)
                if data:
                    logging.info(f"Read sensor data: {data}")
                time.sleep(Config.SENSOR_READ_INTERVAL)

    def initialize_bme680(self):
        try:
            i2c = I2C(board.SCL, board.SDA)
            sensor = bme680.Adafruit_BME680_I2C(i2c, debug=False)
            sensor.sea_level_pressure = Config.PRESSURE_AT_SEALEVEL
        except IOError as e:
            logging.error(f"Failed to initialize BME680 sensor: {e}")
            sys.exit(1)
        return sensor

    def initialize_lora(self, serial_port=Config.LORA_SERIAL_DEVICE, baud_rate=Config.LORA_SERIAL_BAUD_RATE):
        try:
            lora = serial.Serial(serial_port, baudrate=baud_rate, timeout=3.0)
            logging.info("LoRa module initialized")
            return lora
        except Exception as e:
            logging.error(f"Failed to initialize LoRa module: {e}")
            raise

    def read_sensor_data(self):
        try:
            if self.sensor:
                data = {
                    'temperature': self.sensor.temperature,
                    'humidity': self.sensor.humidity,
                    'pressure': self.sensor.pressure,
                    'gas': self.sensor.gas,
                    'altitude': self.sensor.altitude
                }
                if not -40 <= data['temperature'] <= 85:
                    raise ValueError(f"Temperature out of range: {data['temperature']}")
                logging.info(f"Sensor data read successfully: {data}")
                return data
        except Exception as e:
            logging.error(f"Error reading sensor data: {e}")
        return {}

    def write_data_to_lora(self, data):
        try:
            self.lora.write(json.dumps(data).encode())
            logging.info(f"Sent data: {data}")
        except Exception as e:
            logging.error(f"Failed to send data: {e}")

    def write_data_to_file(self, data, filename=Config.SENSOR_DATA_FILE):
        try:
            with open(filename, "a") as self.data_file:
                if data:
                    self.data_file.write(json.dumps(data) + "\n")
                    self.data_file.flush()
        except Exception as e:
            logging.error(f"Error writing data to file: {e}")

if __name__ == "__main__":
    service = SensorService()
    try:
        service.run()
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        logging.info("Sensor reading ended")
