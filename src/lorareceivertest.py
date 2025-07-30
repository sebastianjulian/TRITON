# # import os
# # import glob
# # import shutil
# # import serial
# # import time
# # from datetime import datetime

# # # ───── CONFIG ─────
# # LABELS = [
# #     "Elapsed [s]",
# #     "Temp_BME280 [°C]", "Hum [%]", "Press [hPa]", "Alt [m]",
# #     "Acc x [m/s²]", "Acc y [m/s²]", "Acc z [m/s²]",
# #     "Gyro x [°/s]", "Gyro y [°/s]", "Gyro z [°/s]",
# #     "Temp_MPU [°C]"
# # ]
# # DECIMALS = [3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
# # MIN_COLUMNS = len(LABELS) + 1

# # COM_PORT = 'COM8'     # Adjust if needed
# # BAUD_RATE = 9600
# # LOG_DIR = "logs"
# # ARCHIVE_DIR = os.path.join(LOG_DIR, "previous_data")

# # # ───── PREPARE LOGGING ─────
# # os.makedirs(ARCHIVE_DIR, exist_ok=True)
# # os.makedirs(LOG_DIR, exist_ok=True)

# # for file in glob.glob(os.path.join(LOG_DIR, "sensor_data_*.csv")):
# #     shutil.move(file, ARCHIVE_DIR)

# # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# # logfile = os.path.join(LOG_DIR, f"sensor_data_{timestamp}.csv")

# # with open(logfile, "w") as f:
# #     header = f"{'Timestamp (MET)':<22}" + "".join(
# #         f"{label:>{DECIMALS[i] + 14}}" for i, label in enumerate(LABELS)
# #     ) + "\n"
# #     f.write(header)

# # print(f"📂 Logging to: {logfile}")

# # # ───── INIT SERIAL ─────
# # try:
# #     ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
# #     print(f"🔌 Connected to {COM_PORT} at {BAUD_RATE} baud.")
# # except Exception as e:
# #     print("❌ Serial error:", e)
# #     exit(1)

# # # ───── INIT DATA CONTAINERS ─────
# # min_data = [float('inf')] * len(LABELS)
# # max_data = [float('-inf')] * len(LABELS)

# # print("📡 Listening for LoRa data...")

# # try:
# #     while True:
# #         if ser.in_waiting:
# #             line = ser.readline().decode(errors='ignore').strip()

# #             if not line or line.count(",") < MIN_COLUMNS - 1:
# #                 print("⚠️ Skipped incomplete line:", line)
# #                 continue

# #             print("📥", line)

# #             fields = line.split(",")
# #             try:
# #                 float_data = [float(f) for f in fields[1:]]  # Skip timestamp
# #                 for i, val in enumerate(float_data):
# #                     min_data[i] = min(min_data[i], val)
# #                     max_data[i] = max(max_data[i], val)
# #             except:
# #                 pass  # If parsing fails, skip min/max update

# #             # Align and log line
# #             with open(logfile, "a") as f:
# #                 f.write(f"{fields[0]:<22}")
# #                 for i in range(len(LABELS)):
# #                     try:
# #                         val = float(fields[i + 1])
# #                         f.write(f"{val:>{DECIMALS[i] + 14}.{DECIMALS[i]}f}")
# #                     except:
# #                         f.write(f"{fields[i + 1]:>{DECIMALS[i] + 14}}")
# #                 f.write("\n")

# # except KeyboardInterrupt:
# #     print("\n🛑 Gracefully stopped. Writing min/max summary...")

# #     with open(logfile, "a") as f:
# #         min_line = "MIN" + " " * 18
# #         max_line = "MAX" + " " * 18

# #         for i in range(len(LABELS)):
# #             try:
# #                 min_line += f"{min_data[i]:>{DECIMALS[i] + 14}.{DECIMALS[i]}f}"
# #                 max_line += f"{max_data[i]:>{DECIMALS[i] + 14}.{DECIMALS[i]}f}"
# #             except:
# #                 min_line += f"{'':>{DECIMALS[i] + 14}}"
# #                 max_line += f"{'':>{DECIMALS[i] + 14}}"

# #         f.write("\n" + min_line + "\n" + max_line + "\n")
# #     print("✅ Min/max summary written to log.")


# import os
# import glob
# import shutil
# import serial
# import time
# import requests
# from datetime import datetime

# # ───── CONFIG ─────
# LABELS = [
#     "Elapsed [s]",
#     "Temp_BME280 [°C]", "Hum [%]", "Press [hPa]", "Alt [m]",
#     "Acc x [m/s²]", "Acc y [m/s²]", "Acc z [m/s²]",
#     "Gyro x [°/s]", "Gyro y [°/s]", "Gyro z [°/s]",
#     "Temp_MPU [°C]"
# ]
# DECIMALS = [3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
# MIN_COLUMNS = len(LABELS) + 1

# COM_PORT = 'COM8'
# BAUD_RATE = 9600
# LOG_DIR = "logs"
# ARCHIVE_DIR = os.path.join(LOG_DIR, "previous_data")
# WEB_ENDPOINT = "http://localhost:5000/update"

# # ───── PREPARE LOGGING ─────
# os.makedirs(ARCHIVE_DIR, exist_ok=True)
# os.makedirs(LOG_DIR, exist_ok=True)

# for file in glob.glob(os.path.join(LOG_DIR, "sensor_data_*.csv")):
#     shutil.move(file, ARCHIVE_DIR)

# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# logfile = os.path.join(LOG_DIR, f"sensor_data_{timestamp}.csv")

# with open(logfile, "w") as f:
#     header = f"{'Timestamp (MET)':<22}" + "".join(
#         f"{label:>{DECIMALS[i] + 14}}" for i, label in enumerate(LABELS)
#     ) + "\n"
#     f.write(header)

# print(f"📂 Logging to: {logfile}")

# # ───── INIT SERIAL ─────
# try:
#     ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
#     print(f"🔌 Connected to {COM_PORT} at {BAUD_RATE} baud.")
# except Exception as e:
#     print("❌ Serial error:", e)
#     exit(1)

# # ───── INIT DATA CONTAINERS ─────
# min_data = [float('inf')] * len(LABELS)
# max_data = [float('-inf')] * len(LABELS)

# print("📡 Listening for LoRa data...")

# try:
#     while True:
#         if ser.in_waiting:
#             line = ser.readline().decode(errors='ignore').strip()

#             if not line or line.count(",") < MIN_COLUMNS - 1:
#                 print("⚠️ Skipped incomplete line:", line)
#                 continue

#             print("📥", line)

#             fields = line.split(",")
#             timestamp_str = fields[0]
#             values = fields[1:]

#             # ───── Update min/max ─────
#             try:
#                 for i in range(len(values)):
#                     val = float(values[i])
#                     min_data[i] = min(min_data[i], val)
#                     max_data[i] = max(max_data[i], val)
#             except:
#                 pass  # Ignore any parse failures

#             # ───── Write to file ─────
#             with open(logfile, "a") as f:
#                 f.write(f"{timestamp_str:<22}")
#                 for i in range(len(LABELS)):
#                     try:
#                         val = float(values[i])
#                         f.write(f"{val:>{DECIMALS[i] + 14}.{DECIMALS[i]}f}")
#                     except:
#                         f.write(f"{values[i]:>{DECIMALS[i] + 14}}")
#                 f.write("\n")

#             # ───── Send to dashboard ─────
#             try:
#                 payload = {
#                     "timestamp": timestamp_str,
#                     "data": {LABELS[i]: values[i] for i in range(len(LABELS))}
#                 }
#                 requests.post(WEB_ENDPOINT, json=payload, timeout=0.5)
#             except Exception as e:
#                 print("[WARN] Could not send to dashboard:", e)

# except KeyboardInterrupt:
#     print("\n🛑 Gracefully stopped. Writing min/max summary...")

#     with open(logfile, "a") as f:
#         min_line = "MIN" + " " * 18
#         max_line = "MAX" + " " * 18

#         for i in range(len(LABELS)):
#             try:
#                 min_line += f"{min_data[i]:>{DECIMALS[i] + 14}.{DECIMALS[i]}f}"
#                 max_line += f"{max_data[i]:>{DECIMALS[i] + 14}.{DECIMALS[i]}f}"
#             except:
#                 min_line += f"{'':>{DECIMALS[i] + 14}}"
#                 max_line += f"{'':>{DECIMALS[i] + 14}}"

#         f.write("\n" + min_line + "\n" + max_line + "\n")
#     print("✅ Min/max summary written to log.")


# import os
# import glob
# import shutil
# import serial
# import time
# import requests
# from datetime import datetime

# LABELS = [
#     "Elapsed [s]",
#     "Temp_BME280 [°C]", "Hum [%]", "Press [hPa]", "Alt [m]",
#     "Acc x [m/s²]", "Acc y [m/s²]", "Acc z [m/s²]",
#     "Gyro x [°/s]", "Gyro y [°/s]", "Gyro z [°/s]",
#     "Temp_MPU [°C]"
# ]
# DECIMALS = [3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
# MIN_COLUMNS = len(LABELS) + 1

# COM_PORT = 'COM8'
# BAUD_RATE = 9600
# LOG_DIR = "logs"
# ARCHIVE_DIR = os.path.join(LOG_DIR, "previous_data")
# WEB_ENDPOINT = "http://localhost:5000/update"

# os.makedirs(ARCHIVE_DIR, exist_ok=True)
# os.makedirs(LOG_DIR, exist_ok=True)

# for file in glob.glob(os.path.join(LOG_DIR, "sensor_data_*.csv")):
#     shutil.move(file, ARCHIVE_DIR)

# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# logfile = os.path.join(LOG_DIR, f"sensor_data_{timestamp}.csv")

# with open(logfile, "w") as f:
#     header = f"{'Timestamp (MET)':<22}" + "".join(
#         f"{label:>{DECIMALS[i] + 14}}" for i, label in enumerate(LABELS)
#     ) + "\n"
#     f.write(header)

# try:
#     ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
#     print(f"🔌 Connected to {COM_PORT} at {BAUD_RATE} baud.")
# except Exception as e:
#     print("❌ Serial error:", e)
#     exit(1)

# print("📡 Listening for LoRa data...")

# min_data = [float('inf')] * len(LABELS)
# max_data = [float('-inf')] * len(LABELS)
# sum_data = [0.0] * len(LABELS)
# count_data = 0

# try:
#     while True:
#         if ser.in_waiting:
#             line = ser.readline().decode(errors='ignore').strip()
#             if not line or line.count(",") < MIN_COLUMNS - 1:
#                 print("⚠️ Skipped incomplete line:", line)
#                 continue

#             print("📥", line)
#             fields = line.split(",")
#             timestamp_str = fields[0]
#             values = fields[1:]

#             try:
#                 for i in range(len(values)):
#                     val = float(values[i])
#                     min_data[i] = min(min_data[i], val)
#                     max_data[i] = max(max_data[i], val)
#                     sum_data[i] += val
#                 count_data += 1
#             except:
#                 continue

#             with open(logfile, "a") as f:
#                 f.write(f"{timestamp_str:<22}")
#                 for i in range(len(LABELS)):
#                     try:
#                         val = float(values[i])
#                         f.write(f"{val:>{DECIMALS[i] + 14}.{DECIMALS[i]}f}")
#                     except:
#                         f.write(f"{values[i]:>{DECIMALS[i] + 14}}")
#                 f.write("\n")

#             try:
#                 payload = {
#                     "timestamp": timestamp_str,
#                     "data": {LABELS[i]: values[i] for i in range(len(LABELS))},
#                     "stats": {
#                         "min": {LABELS[i]: min_data[i] for i in range(len(LABELS))},
#                         "max": {LABELS[i]: max_data[i] for i in range(len(LABELS))},
#                         "avg": {LABELS[i]: sum_data[i]/count_data for i in range(len(LABELS))}
#                     }
#                 }
#                 requests.post(WEB_ENDPOINT, json=payload, timeout=0.5)
#             except Exception as e:
#                 print("[WARN] Could not send to dashboard:", e)

# except KeyboardInterrupt:
#     print("\n🛑 Gracefully stopped.")



import os
import glob
import shutil
import serial
import time
import requests
from datetime import datetime

LABELS = [
    "Elapsed [s]",
    "Temp_BME280 [°C]", "Hum [%]", "Press [hPa]", "Alt [m]",
    "Acc x [m/s²]", "Acc y [m/s²]", "Acc z [m/s²]",
    "Gyro x [°/s]", "Gyro y [°/s]", "Gyro z [°/s]",
    "Temp_MPU [°C]"
]

THRESHOLDS = {
    "Temp_BME280 [°C]": 0.25,
    "Hum [%]": 1.0,
    "Press [hPa]": 0.5,
    "Alt [m]": 0.5,
    "Acc x [m/s²]": 0.25,
    "Acc y [m/s²]": 0.25,
    "Acc z [m/s²]": 0.25,
    "Gyro x [°/s]": 5.0,
    "Gyro y [°/s]": 5.0,
    "Gyro z [°/s]": 5.0,
    "Temp_MPU [°C]": 0.25
}

DECIMALS = [3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
MIN_COLUMNS = len(LABELS) + 1
COM_PORT = 'COM8'
BAUD_RATE = 9600
LOG_DIR = "logs"
ARCHIVE_DIR = os.path.join(LOG_DIR, "previous_data")
WEB_ENDPOINT = "http://localhost:5000/update"

os.makedirs(ARCHIVE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

for file in glob.glob(os.path.join(LOG_DIR, "sensor_data_*.csv")):
    shutil.move(file, ARCHIVE_DIR)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
logfile = os.path.join(LOG_DIR, f"sensor_data_{timestamp}.csv")

with open(logfile, "w") as f:
    header = f"{'Timestamp (MET)':<22}" + "".join(
        f"{label:>{DECIMALS[i] + 14}}" for i, label in enumerate(LABELS)
    ) + "\n"
    f.write(header)

try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    print(f"🔌 Connected to {COM_PORT} at {BAUD_RATE} baud.")
except Exception as e:
    print("❌ Serial error:", e)
    exit(1)

print("📱 Listening for LoRa data...")

min_data = [float('inf')] * len(LABELS)
max_data = [float('-inf')] * len(LABELS)
sum_data = [0.0] * len(LABELS)
count_data = 0
last_sent_values = {}

try:
    while True:
        if ser.in_waiting:
            line = ser.readline().decode(errors='ignore').strip()
            if not line or line.count(",") < MIN_COLUMNS - 1:
                print("⚠️ Skipped incomplete line:", line)
                continue

            print("📥", line)
            fields = line.split(",")
            timestamp_str = fields[0]
            values = fields[1:]

            try:
                for i in range(len(values)):
                    val = float(values[i])
                    min_data[i] = min(min_data[i], val)
                    max_data[i] = max(max_data[i], val)
                    sum_data[i] += val
                count_data += 1
            except:
                continue

            with open(logfile, "a") as f:
                f.write(f"{timestamp_str:<22}")
                for i in range(len(LABELS)):
                    try:
                        val = float(values[i])
                        f.write(f"{val:>{DECIMALS[i] + 14}.{DECIMALS[i]}f}")
                    except:
                        f.write(f"{values[i]:>{DECIMALS[i] + 14}}")
                f.write("\n")

            filtered_data = {}
            should_send = False

            for i, label in enumerate(LABELS):
                try:
                    new_val = float(values[i])
                    last_val = last_sent_values.get(label)

                    if last_val is None or abs(new_val - last_val) >= THRESHOLDS.get(label, 0):
                        filtered_data[label] = values[i]
                        last_sent_values[label] = new_val
                        should_send = True
                    else:
                        filtered_data[label] = last_val
                except:
                    filtered_data[label] = values[i]

            if should_send:
                try:
                    payload = {
                        "timestamp": timestamp_str,
                        "data": filtered_data,
                        "stats": {
                            "min": {LABELS[i]: min_data[i] for i in range(len(LABELS))},
                            "max": {LABELS[i]: max_data[i] for i in range(len(LABELS))},
                            "avg": {LABELS[i]: sum_data[i]/count_data for i in range(len(LABELS))}
                        }
                    }
                    requests.post(WEB_ENDPOINT, json=payload, timeout=0.5)
                except Exception as e:
                    print("[WARN] Could not send to dashboard:", e)

except KeyboardInterrupt:
    print("\n🛑 Gracefully stopped.")
    with open(logfile, "a") as f:
        f.write("\nMIN," + ",".join(str(round(x, d)) if isinstance(x, float) else "" for x, d in zip(min_data, DECIMALS)) + "\n")
        f.write("MAX," + ",".join(str(round(x, d)) if isinstance(x, float) else "" for x, d in zip(max_data, DECIMALS)) + "\n")
