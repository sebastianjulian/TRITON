#TRY1
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





#TRY2
# import time
# import board
# import busio
# import numpy as np
# from datetime import datetime
# from adafruit_bme280 import basic as adafruit_bme280
# from mpu6050 import mpu6050

# # Set up I2C
# i2c = busio.I2C(board.SCL, board.SDA)

# # Try to initialize BME280
# try:
#     bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
#     print("BME280 detected.")
# except Exception as e:
#     print("BME280 not found:", e)
#     bme280 = None

# # Try to initialize MPU6050
# try:
#     mpu = mpu6050(0x68)
#     print("MPU6050 detected.")
# except Exception as e:
#     print("MPU6050 not found:", e)
#     mpu = None

# # Data array
# data = np.zeros(11)

# # CSV file setup
# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# filename = f"sensor_data_{timestamp}.csv"
# with open(filename, "w") as f:
#     f.write("timestamp,temp,humidity,pressure,altitude,ax,ay,az,gx,gy,gz,mpu_temp\n")

# # Loop
# while True:
#     now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     if bme280:
#         try:
#             data[0] = bme280.temperature
#             data[1] = bme280.humidity
#             data[2] = bme280.pressure
#             data[3] = bme280.altitude
#         except Exception as e:
#             print("[WARNING] BME280 read failed:", e)
#             data[0:4] = np.nan

#     if mpu:
#         try:
#             accel = mpu.get_accel_data()
#             gyro = mpu.get_gyro_data()
#             data[4] = accel['x']
#             data[5] = accel['y']
#             data[6] = accel['z']
#             data[7] = gyro['x']
#             data[8] = gyro['y']
#             data[9] = gyro['z']
#             data[10] = mpu.get_temp()
#         except Exception as e:
#             print("[WARNING] MPU6050 read failed:", e)
#             data[4:11] = np.nan

#     # Print to console
#     print(data)

#     # Write to file
#     with open(filename, "a") as f:
#         values = ",".join(f"{v:.2f}" if not np.isnan(v) else "NaN" for v in data)
#         f.write(f"{now},{values}\n")

#     time.sleep(1)






#TRY3
# import time
# import os
# import board
# import busio
# import numpy as np
# from datetime import datetime
# from adafruit_bme280 import basic as adafruit_bme280
# from mpu6050 import mpu6050

# # Create logs directory if it doesn't exist
# LOG_DIR = "logs"
# os.makedirs(LOG_DIR, exist_ok=True)

# # Create filename with timestamp
# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# filename = os.path.join(LOG_DIR, f"sensor_data_{timestamp}.csv")

# # Set up I2C
# i2c = busio.I2C(board.SCL, board.SDA)

# # Try to initialize BME280
# try:
#     bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
#     print("BME280 detected.")
# except Exception as e:
#     print("BME280 not found:", e)
#     bme280 = None

# # Try to initialize MPU6050
# try:
#     mpu = mpu6050(0x68)
#     print("MPU6050 detected.")
# except Exception as e:
#     print("MPU6050 not found:", e)
#     mpu = None

# # Data array: [temp, hum, pressure, alt, ax, ay, az, gx, gy, gz, mpu_temp]
# data = np.zeros(11)

# # Open file and write header
# with open(filename, "w") as f:
#     f.write(
#         "Timestamp,Temperature [°C],Humidity [%],Pressure [hPa],Altitude [m],"
#         "Accel X [m/s²],Accel Y [m/s²],Accel Z [m/s²],"
#         "Gyro X [°/s],Gyro Y [°/s],Gyro Z [°/s],MPU Temp [°C]\n"
#     )

# print(f"[INFO] Logging to {filename}")

# # Print table header
# print(
#     f"{'Time':<20} {'T [°C]':>8} {'H [%]':>8} {'P [hPa]':>10} {'Alt [m]':>8}"
#     f" {'Ax':>8} {'Ay':>8} {'Az':>8} {'Gx':>8} {'Gy':>8} {'Gz':>8} {'T_mpu':>8}"
# )

# # Main loop
# while True:
#     now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     if bme280:
#         try:
#             data[0] = bme280.temperature
#             data[1] = bme280.humidity
#             data[2] = bme280.pressure
#             data[3] = bme280.altitude
#         except Exception as e:
#             print("[WARNING] BME280 read failed:", e)
#             data[0:4] = np.nan

#     if mpu:
#         try:
#             accel = mpu.get_accel_data()
#             gyro = mpu.get_gyro_data()
#             data[4] = accel['x']
#             data[5] = accel['y']
#             data[6] = accel['z']
#             data[7] = gyro['x']
#             data[8] = gyro['y']
#             data[9] = gyro['z']
#             data[10] = mpu.get_temp()
#         except Exception as e:
#             print("[WARNING] MPU6050 read failed:", e)
#             data[4:11] = np.nan

#     # Print formatted output
#     print(
#         f"{now_str:<20} "
#         f"{data[0]:8.2f} {data[1]:8.2f} {data[2]:10.2f} {data[3]:8.2f} "
#         f"{data[4]:8.2f} {data[5]:8.2f} {data[6]:8.2f} "
#         f"{data[7]:8.2f} {data[8]:8.2f} {data[9]:8.2f} {data[10]:8.2f}"
#     )

#     # Write to file
#     with open(filename, "a") as f:
#         line = ",".join(f"{v:.2f}" if not np.isnan(v) else "NaN" for v in data)
#         f.write(f"{now_str},{line}\n")

#     time.sleep(1)




#TRY4
# import time
# import os
# import board
# import busio
# import numpy as np
# from datetime import datetime
# from adafruit_bme280 import basic as adafruit_bme280
# from mpu6050 import mpu6050

# import pytz  # make sure this is installed (pip install pytz)

# # Time zone setup: MET (Europe/Berlin handles DST automatically)
# tz = pytz.timezone("Europe/Berlin")

# # Create logs directory if it doesn't exist
# LOG_DIR = "logs"
# os.makedirs(LOG_DIR, exist_ok=True)

# # Create filename with timestamp
# timestamp = datetime.now(tz).strftime("%Y%m%d_%H%M%S")
# filename = os.path.join(LOG_DIR, f"sensor_data_{timestamp}.csv")

# # Set up I2C
# i2c = busio.I2C(board.SCL, board.SDA)

# # Try to initialize BME280
# try:
#     bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
#     print("BME280 detected.")
# except Exception as e:
#     print("BME280 not found:", e)
#     bme280 = None

# # Try to initialize MPU6050
# try:
#     mpu = mpu6050(0x68)
#     print("MPU6050 detected.")
# except Exception as e:
#     print("MPU6050 not found:", e)
#     mpu = None

# # Data array: [temp, hum, pressure, alt, ax, ay, az, gx, gy, gz, mpu_temp]
# data = np.zeros(11)

# # Open file and write header
# with open(filename, "w") as f:
#     f.write(
#         "Timestamp,Temperature [°C],Humidity [%],Pressure [hPa],Altitude [m],"
#         "Accel X [m/s²],Accel Y [m/s²],Accel Z [m/s²],"
#         "Gyro X [°/s],Gyro Y [°/s],Gyro Z [°/s],MPU Temp [°C]\n"
#     )

# print(f"[INFO] Logging to {filename}\n")

# # Console header
# print(f"{'Timestamp (MET)':<20} {'Temp[°C]':>10} {'Hum[%]':>10} {'Pres[hPa]':>10} {'Alt[m]':>10} "
#       f"{'Ax':>10} {'Ay':>10} {'Az':>10} {'Gx':>10} {'Gy':>10} {'Gz':>10} {'T_mpu[°C]':>12}")

# # Main loop
# while True:
#     now = datetime.now(tz)
#     now_str = now.strftime("%Y-%m-%d %H:%M:%S")

#     if bme280:
#         try:
#             data[0] = bme280.temperature
#             data[1] = bme280.humidity
#             data[2] = bme280.pressure
#             data[3] = bme280.altitude
#         except Exception as e:
#             print("[WARNING] BME280 read failed:", e)
#             data[0:4] = np.nan

#     if mpu:
#         try:
#             accel = mpu.get_accel_data()
#             gyro = mpu.get_gyro_data()
#             data[4] = accel['x']
#             data[5] = accel['y']
#             data[6] = accel['z']
#             data[7] = gyro['x']
#             data[8] = gyro['y']
#             data[9] = gyro['z']
#             data[10] = mpu.get_temp()
#         except Exception as e:
#             print("[WARNING] MPU6050 read failed:", e)
#             data[4:11] = np.nan

#     # Print aligned output
#     print(f"{now_str:<20}"
#           f"{data[0]:10.2f}{data[1]:10.2f}{data[2]:10.2f}{data[3]:10.2f}"
#           f"{data[4]:10.2f}{data[5]:10.2f}{data[6]:10.2f}"
#           f"{data[7]:10.2f}{data[8]:10.2f}{data[9]:10.2f}{data[10]:12.2f}")

#     # Write to CSV
#     with open(filename, "a") as f:
#         values = ",".join(f"{v:.2f}" if not np.isnan(v) else "NaN" for v in data)
#         f.write(f"{now_str},{values}\n")

#     time.sleep(1)




#TRY5


# import time
# import os
# import board
# import busio
# import numpy as np
# from datetime import datetime
# from adafruit_bme280 import basic as adafruit_bme280
# from mpu6050 import mpu6050
# import pytz

# # ─────────────────────────────────────────────
# # CONFIGURATION
# # ─────────────────────────────────────────────
# tz = pytz.timezone("Europe/Berlin")  # MET timezone

# LOG_DIR = "logs"
# os.makedirs(LOG_DIR, exist_ok=True)

# filename = os.path.join(
#     LOG_DIR,
#     f"sensor_data_{datetime.now(tz).strftime('%Y%m%d_%H%M%S')}.csv"
# )

# # Measurement thresholds (deltas) — when to log
# deltas = np.array([
#     0.1,  # BME280 temp °C
#     0.5,  # humidity %
#     0.1,  # pressure hPa
#     0.5,  # altitude m
#     0.1,  # accel x
#     0.1,  # accel y
#     0.1,  # accel z
#     1.0,  # gyro x
#     1.0,  # gyro y
#     1.0,  # gyro z
#     0.1   # mpu temp °C
# ])
# # deltas (Temp: auf 2, Hum: auf 1, Press: auf 1, Alt: auf 1, acc: auf 2, gyro: auf 2, Temp(mpu): auf 1)
# # ─────────────────────────────────────────────
# # INIT SENSORS
# # ─────────────────────────────────────────────
# i2c = busio.I2C(board.SCL, board.SDA)

# try:
#     bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
#     print("BME280 detected.")
# except Exception as e:
#     print("BME280 not found:", e)
#     bme280 = None

# try:
#     mpu = mpu6050(0x68)
#     print("MPU6050 detected.")
# except Exception as e:
#     print("MPU6050 not found:", e)
#     mpu = None

# # ─────────────────────────────────────────────
# # INIT DATA STRUCTURES
# # ─────────────────────────────────────────────
# data = np.zeros(11)
# last_data = np.full(11, np.nan)

# header_labels = [
#     "Temp[°C]", "Hum[%]", "Pres[hPa]", "Alt[m]",
#     "Ax[m/s²]", "Ay", "Az", "Gx[°/s]", "Gy", "Gz", "T_MPU[°C]"
# ]

# # ─────────────────────────────────────────────
# # WRITE HEADER TO CSV
# # ─────────────────────────────────────────────
# with open(filename, "w") as f:
#     f.write("Timestamp (MET)," + ",".join(header_labels) + "\n")

# # ─────────────────────────────────────────────
# # PRINT HEADER FOR CONSOLE
# # ─────────────────────────────────────────────
# print("\n" + "-" * 130)
# print(f"{'Timestamp (MET)':<22}" + "".join([f"{label:>12}" for label in header_labels]))
# print("-" * 130)

# # ─────────────────────────────────────────────
# # MAIN LOOP
# # ─────────────────────────────────────────────
# last_print_time = time.perf_counter()

# while True:
#     now = datetime.now(tz)
#     now_str = now.strftime("%Y-%m-%d %H:%M:%S")

#     try:
#         if bme280:
#             data[0] = bme280.temperature
#             data[1] = bme280.humidity
#             data[2] = bme280.pressure
#             data[3] = bme280.altitude
#         if mpu:
#             accel = mpu.get_accel_data()
#             gyro = mpu.get_gyro_data()
#             data[4] = accel["x"]
#             data[5] = accel["y"]
#             data[6] = accel["z"]
#             data[7] = gyro["x"]
#             data[8] = gyro["y"]
#             data[9] = gyro["z"]
#             data[10] = mpu.get_temp()
#     except Exception as e:
#         print("[ERROR] Sensor read failed:", e)
#         continue

#     diff = np.abs(data - last_data)
#     now_perf = time.perf_counter()

#     should_log = (
#         np.any(diff > deltas) or
#         now_perf - last_print_time >= 1.0
#     )

#     if should_log:
#         last_data[:] = data
#         last_print_time = now_perf

#         # ───── Console Output ─────
#         print(f"{now_str:<22}" + "".join([f"{val:12.2f}" for val in data]))

#         # ───── File Output ─────
#         with open(filename, "a") as f:
#             csv_line = ",".join(f"{val:.2f}" for val in data)
#             f.write(f"{now_str},{csv_line}\n")

#     time.sleep(0.1)



#TRY6
# import os
# import glob
# import shutil
# import time
# import board
# import busio
# import numpy as np
# from datetime import datetime
# from adafruit_bme280 import basic as adafruit_bme280
# from mpu6050 import mpu6050
# import pytz

# # ── CONFIG ───────────────────────────────────────────────────────────────
# TZ = pytz.timezone("Europe/Berlin")  # MET with DST
# LOG_DIR = "logs"
# ARCHIVE_DIR = os.path.join(LOG_DIR, "previous_data")

# # decimal-place thresholds for change detection
# decimals = np.array([
#     2,  # Temp [°C]
#     1,  # Hum [%]
#     1,  # Pres [hPa]
#     1,  # Alt [m]
#     2,  # Ax [m/s²]
#     2,  # Ay
#     2,  # Az
#     2,  # Gx [°/s]
#     2,  # Gy
#     2,  # Gz
#     1,  # T_MPU [°C]
# ], dtype=int)

# labels = [
#     "Temp[°C]", "Hum[%]", "Pres[hPa]", "Alt[m]",
#     "Ax[m/s²]", "Ay", "Az",
#     "Gx[°/s]", "Gy", "Gz",
#     "T_MPU[°C]"
# ]

# # ── ARCHIVE OLD LOGS ─────────────────────────────────────────────────────
# os.makedirs(ARCHIVE_DIR, exist_ok=True)
# for path in glob.glob(os.path.join(LOG_DIR, "sensor_data_*.csv")):
#     shutil.move(path, ARCHIVE_DIR)

# # ── NEW LOG FILE ─────────────────────────────────────────────────────────
# timestamp = datetime.now(TZ).strftime("%Y%m%d_%H%M%S")
# logfile = os.path.join(LOG_DIR, f"sensor_data_{timestamp}.csv")

# # write header
# with open(logfile, "w") as f:
#     f.write("Timestamp (MET)," + ",".join(labels) + "\n")

# # ── INIT SENSORS ─────────────────────────────────────────────────────────
# i2c = busio.I2C(board.SCL, board.SDA)
# try:
#     bme = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
#     print("BME280 detected.")
# except Exception as e:
#     print("BME280 init failed:", e)
#     bme = None

# try:
#     mpu = mpu6050(0x68)
#     print("MPU6050 detected.")
# except Exception as e:
#     print("MPU6050 init failed:", e)
#     mpu = None

# # ── DATA STORAGE ──────────────────────────────────────────────────────────
# data = np.zeros(len(labels))
# last_data = np.full(len(labels), np.nan)
# min_data = np.full(len(labels), np.inf)
# max_data = np.full(len(labels), -np.inf)

# # ── CONSOLE HEADER ────────────────────────────────────────────────────────
# print("\n" + "-"*130)
# fmt = "{:<20}" + "".join(["{:>12}" for _ in labels])
# print(fmt.format("Timestamp (MET)", *labels))
# print("-"*130)

# # ── MAIN LOOP ─────────────────────────────────────────────────────────────
# last_log_time = time.perf_counter()
# try:
#     while True:
#         now = datetime.now(TZ)
#         now_str = now.strftime("%Y-%m-%d %H:%M:%S")

#         # read sensors
#         if bme:
#             try:
#                 data[0] = bme.temperature
#                 data[1] = bme.humidity
#                 data[2] = bme.pressure
#                 data[3] = bme.altitude
#             except Exception as e:
#                 print("[WARN] BME read failed:", e)
#                 data[0:4] = np.nan

#         if mpu:
#             try:
#                 accel = mpu.get_accel_data()
#                 gyro  = mpu.get_gyro_data()
#                 data[4] = accel["x"]; data[5] = accel["y"]; data[6] = accel["z"]
#                 data[7] = gyro["x"];  data[8] = gyro["y"];  data[9] = gyro["z"]
#                 data[10] = mpu.get_temp()
#             except Exception as e:
#                 print("[WARN] MPU read failed:", e)
#                 data[4:11] = np.nan

#         # update min/max
#         min_data = np.minimum(min_data, data)
#         max_data = np.maximum(max_data, data)

#         # check deltas
#         changed = any(
#             round(data[i], decimals[i]) != round(last_data[i], decimals[i])
#             for i in range(len(data))
#         )
#         now_perf = time.perf_counter()
#         if changed or (now_perf - last_log_time) >= 1.0:
#             # log/update
#             last_data[:] = data
#             last_log_time = now_perf

#             # console
#             print(fmt.format(now_str, *data))

#             # file
#             with open(logfile, "a") as f:
#                 row = ",".join(f"{v:.2f}" if not np.isnan(v) else "NaN" for v in data)
#                 f.write(f"{now_str},{row}\n")

#         time.sleep(0.1)

# except KeyboardInterrupt:
#     # on exit, append min/max
#     with open(logfile, "a") as f:
#         f.write("MIN," + ",".join(f"{v:.2f}" for v in min_data) + "\n")
#         f.write("MAX," + ",".join(f"{v:.2f}" for v in max_data) + "\n")
#     print("\nGraceful exit, min/max written to file.")




#TRY7
import os
import glob
import shutil
import time
import board
import busio
import numpy as np
from datetime import datetime
from adafruit_bme280 import basic as adafruit_bme280
from mpu6050 import mpu6050
import pytz

# ─────────────── CONFIG ───────────────
TZ = pytz.timezone("Europe/Berlin")  # MET with DST
LOG_DIR = "logs"
ARCHIVE_DIR = os.path.join(LOG_DIR, "previous_data")

labels = [
    "Temp [°C]", "Hum [%]", "Pres [hPa]", "Alt [m]",
    "Ax [m/s²]", "Ay [m/s²]", "Az [m/s²]",
    "Gx [°/s]", "Gy [°/s]", "Gz [°/s]",
    "T_MPU [°C]"
]

decimals = np.array([
    2, 1, 1, 1,     # BME280
    2, 2, 2,        # Acceleration
    2, 2, 2,        # Gyroscope
    1              # MPU6050 Temp
], dtype=int)

# ────── Prepare log folders ──────
os.makedirs(ARCHIVE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Move old logs to archive
for path in glob.glob(os.path.join(LOG_DIR, "sensor_data_*.csv")):
    shutil.move(path, ARCHIVE_DIR)

# Create new log file
timestamp = datetime.now(TZ).strftime("%Y%m%d_%H%M%S")
logfile = os.path.join(LOG_DIR, f"sensor_data_{timestamp}.csv")

# Write CSV header
with open(logfile, "w") as f:
    header = f"{'Timestamp (MET)':<22}" + "".join([f"{label:>{decimals[i] + 12}}" for i, label in enumerate(labels)]) + "\n"
    f.write(header)

# ────── Sensor init ──────
i2c = busio.I2C(board.SCL, board.SDA)

try:
    bme = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
    print("✅ BME280 detected.")
except Exception as e:
    print("⚠️  BME280 init failed:", e)
    bme = None

try:
    mpu = mpu6050(0x68)
    print("✅ MPU6050 detected.")
except Exception as e:
    print("⚠️  MPU6050 init failed:", e)
    mpu = None

# ────── Data containers ──────
data = np.zeros(len(labels))
last_data = np.full(len(labels), np.nan)
min_data = np.full(len(labels), np.inf)
max_data = np.full(len(labels), -np.inf)

# Print header to console
print("\n" + "-" * (22 + (decimals + 12).sum()))
header_line = f"{'Timestamp (MET)':<22}" + "".join(f"{label:>{decimals[i] + 12}}" for i, label in enumerate(labels))
print(header_line)
print("-" * (22 + (decimals + 12).sum()))

# ────── Main loop ──────
last_log_time = time.perf_counter()

try:
    while True:
        now = datetime.now(TZ)
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")

        # ─ Read sensors ─
        if bme:
            try:
                data[0] = bme.temperature
                data[1] = bme.humidity
                data[2] = bme.pressure
                data[3] = bme.altitude
            except Exception as e:
                print("[WARN] BME read failed:", e)
                data[0:4] = np.nan

        if mpu:
            try:
                accel = mpu.get_accel_data()
                gyro = mpu.get_gyro_data()
                data[4] = accel["x"]
                data[5] = accel["y"]
                data[6] = accel["z"]
                data[7] = gyro["x"]
                data[8] = gyro["y"]
                data[9] = gyro["z"]
                data[10] = mpu.get_temp()
            except Exception as e:
                print("[WARN] MPU read failed:", e)
                data[4:] = np.nan

        # ─ Update min/max ─
        min_data = np.minimum(min_data, data)
        max_data = np.maximum(max_data, data)

        # ─ Check for changes ─
        changed = any(
            round(data[i], decimals[i]) != round(last_data[i], decimals[i])
            for i in range(len(data))
        )
        now_perf = time.perf_counter()

        if changed or (now_perf - last_log_time) >= 1.0:
            last_data[:] = data
            last_log_time = now_perf

            # ─ Console print ─
            print_line = f"{now_str:<22}"
            for i in range(len(data)):
                try:
                    val = float(data[i])
                    print_line += f"{val:>{decimals[i] + 12}.{decimals[i]}f}"
                except:
                    print_line += f"{'NaN':>{decimals[i] + 12}}"
            print(print_line)

            # ─ CSV file write ─
            with open(logfile, "a") as f:
                csv_line = f"{now_str:<22}"
                for i in range(len(data)):
                    try:
                        val = float(data[i])
                        csv_line += f"{val:>{decimals[i] + 12}.{decimals[i]}f}"
                    except:
                        csv_line += f"{'NaN':>{decimals[i] + 12}}"
                f.write(csv_line + "\n")

        time.sleep(0.1)

except KeyboardInterrupt:
    # ─ Log min/max data at end ─
    with open(logfile, "a") as f:
        f.write("\n")
        f.write("MIN" + " " * 18 + "".join(f"{min_data[i]:>{decimals[i] + 12}.{decimals[i]}f}" for i in range(len(data))) + "\n")
        f.write("MAX" + " " * 18 + "".join(f"{max_data[i]:>{decimals[i] + 12}.{decimals[i]}f}" for i in range(len(data))) + "\n")
    print("\n🛑 Gracefully stopped. Min/max written to file.")





# deltas (Temp: auf 2, Hum: auf 1, Press: auf 1, Alt: auf 1, acc: auf 2, gyro: auf 2, Temp(mpu): auf 1)
# timer
# integrals
# lora
# mission control website
