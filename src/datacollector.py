import asyncio
import os
import random
#import smbus2
#import bme280

from datetime import datetime, timezone

async def generate_random_sensor_data():
    while True:
        await asyncio.sleep(random.uniform(0.5, 2.0))
        temperature = round(random.uniform(18, 28), 2)
        pressure = round(random.uniform(980, 1030), 2)
        yield temperature, pressure
        '''
        await data = bme.280.sample(bus, address, calibration_params)
        temperature = data.temperature
        pressure = data.pressure
        yield temperatur, pressure
        '''


#def save_to_txt_with_timestamp(data, filename):
#    with open(filename, 'w') as file:
#        file.write(f"Timestamp,Temperature [°C],Pressure [hPa]\n")
#        for timestamp, temperature, pressure in data:
#            # file.write(f"{timestamp} - Temperature: {temperature} °C, Pressure: {pressure} hPa\n")
#            file.write(f"{timestamp},{temperature},{pressure}\n")

async def main(file):
    
    async for temperature, pressure in generate_random_sensor_data():
            # Get current timestamp
            timestamp = datetime.now(timezone.utc).isoformat()

            # Add temperature and pressure data to the list
            #data.append((timestamp, temperature, pressure))
            file.write(f"{timestamp},{temperature},{pressure}\n")
            file.flush()
            
            #CODE FÜR ÜBERTRAGUNG MIT LORA-MODUL
            
            # Print the latest temperature and pressure
            print(f"Received data ({timestamp}): Temperature: {temperature} °C, Pressure: {pressure} hPa")


if __name__ == "__main__":

    LOGS_DIR = "logs"
     
    t0 = datetime.now(timezone.utc)
    print(f"started at {t0}")
   
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)
    
    filename = os.path.abspath(f"{LOGS_DIR}/sensor_data_{t0.strftime('%Y%m%d%H%M%S')}Z.csv")
    file = open(filename, mode='w', encoding='utf-8')
    file.write(f"Timestamp,Temperature [°C],Pressure [hPa]\n")
    
    print(f"logging to file {filename}")
    # sensor:_data = []
    try:
        
        asyncio.run(main(file))
        
    except KeyboardInterrupt:
        
        # Handle keyboard interrupt (Ctrl+C) to exit the loop
        print("\nProgram terminated by user.")
        
    finally:
        # Save the collected temperature and pressure data with timestamps to a unique text file before exiting
        
        #save_to_txt_with_timestamp(sensor_data, filename)
        print(f"Collected temperature and pressure data with timestamps saved to {filename}.")
        
        file.close()
        