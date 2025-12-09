# # from flask import Flask, request, jsonify, render_template_string
# # import threading

# # app = Flask(__name__)
# # latest_data = {"timestamp": "No data received", "data": {}}
# # lock = threading.Lock()

# # # HTML template for the dashboard
# # HTML_TEMPLATE = """
# # <!DOCTYPE html>
# # <html>
# # <head>
# #     <title>CanSat Sensor Dashboard</title>
# #     <meta http-equiv="refresh" content="2">
# #     <style>
# #         body { font-family: Arial, sans-serif; background: #f4f4f4; padding: 2em; }
# #         h1 { color: #333; }
# #         table { border-collapse: collapse; width: 60%; }
# #         th, td { border: 1px solid #888; padding: 8px 12px; text-align: left; }
# #         th { background-color: #eee; }
# #     </style>
# # </head>
# # <body>
# #     <h1>CanSat Live Sensor Data</h1>
# #     <p><strong>Last Update:</strong> {{ timestamp }}</p>
# #     <table>
# #         <tr><th>Sensor</th><th>Value</th></tr>
# #         {% for key, value in data.items() %}
# #         <tr><td>{{ key }}</td><td>{{ value }}</td></tr>
# #         {% endfor %}
# #     </table>
# # </body>
# # </html>
# # """

# # @app.route("/", methods=["GET"])
# # def dashboard():
# #     with lock:
# #         return render_template_string(HTML_TEMPLATE, timestamp=latest_data["timestamp"], data=latest_data["data"])

# # @app.route("/update", methods=["POST"])
# # def update_data():
# #     global latest_data
# #     new_data = request.get_json()
# #     if new_data:
# #         with lock:
# #             latest_data = new_data
# #     return jsonify(status="ok")

# # if __name__ == "__main__":
# #     app.run(host="0.0.0.0", port=5000)


# from flask import Flask, request, jsonify, render_template
# from collections import defaultdict
# import time

# app = Flask(__name__)

# # Store all sensor data (x = elapsed, y = value)
# data_history = defaultdict(lambda: {"x": [], "y": []})
# MAX_POINTS = 300  # number of points shown per graph

# @app.route("/", methods=["GET"])
# def dashboard():
#     return render_template("dashboard.html")

# @app.route("/update", methods=["POST"])
# def update_data():
#     content = request.json
#     elapsed = float(content["data"]["Elapsed [s]"])
    
#     for key, value in content["data"].items():
#         if key == "Elapsed [s]":
#             continue
#         try:
#             y_val = float(value)
#         except:
#             continue  # skip non-numeric
#         d = data_history[key]
#         d["x"].append(elapsed)
#         d["y"].append(y_val)
#         if len(d["x"]) > MAX_POINTS:
#             d["x"] = d["x"][-MAX_POINTS:]
#             d["y"] = d["y"][-MAX_POINTS:]
#     return "OK"

# @app.route("/data", methods=["GET"])
# def get_data():
#     return jsonify(data_history)

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)


import os
import signal
import subprocess
import atexit
import platform
import random
import time
import json
import glob as glob_module

from flask import Flask, request, jsonify, render_template, send_from_directory
from datetime import datetime

# Configuration directory setup
CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config'))
CONFIG_FILE = os.path.join(CONFIG_DIR, 'triton_config.json')

# Default configuration values
DEFAULT_CONFIG = {
    "sea_level_pressure": 993.9,
    "transmission_thresholds": {
        "temp_bme280": 0.25,
        "humidity": 1.0,
        "pressure": 0.5,
        "altitude": 0.5,
        "acceleration": 0.25,
        "gyroscope": 5.0,
        "temp_mpu": 0.25
    },
    "update_frequency": 1.0,
    "history_length": 300
}

def load_config():
    """Load configuration from file or return defaults"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"[WARN] Could not load config: {e}")
    return DEFAULT_CONFIG.copy()

def save_config(config):
    """Save configuration to file"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

def get_profile_path(name):
    """Get the path for a configuration profile"""
    # Sanitize profile name
    safe_name = "".join(c for c in name if c.isalnum() or c in ('-', '_')).strip()
    if not safe_name:
        raise ValueError("Invalid profile name")
    return os.path.join(CONFIG_DIR, f'profile_{safe_name}.json')

def list_profiles():
    """List all saved configuration profiles"""
    profiles = []
    if os.path.exists(CONFIG_DIR):
        for f in os.listdir(CONFIG_DIR):
            if f.startswith('profile_') and f.endswith('.json'):
                name = f[8:-5]  # Remove 'profile_' prefix and '.json' suffix
                profiles.append(name)
    return profiles

def kill_port(port=5000):
    try:
        if platform.system() == "Windows":
            # Windows command to find processes using the port
            output = subprocess.check_output(f'netstat -ano | findstr :{port}', shell=True).decode().strip()
            if output:
                lines = output.splitlines()
                for line in lines:
                    if 'LISTENING' in line:
                        pid = line.split()[-1]
                        try:
                            subprocess.run(f'taskkill /F /PID {pid}', shell=True, check=True)
                            print(f"[INFO] Killed process on port {port} (PID: {pid})")
                        except subprocess.CalledProcessError as e:
                            print(f"[WARN] Couldn't kill PID {pid}: {e}")
        else:
            # Unix/Linux command
            output = subprocess.check_output(f"lsof -ti:{port}", shell=True).decode().split()
            for pid in output:
                try:
                    os.kill(int(pid), signal.SIGKILL)
                    print(f"[INFO] Killed process on port {port} (PID: {pid})")
                except Exception as e:
                    print(f"[WARN] Couldn't kill PID {pid}: {e}")
    except subprocess.CalledProcessError:
        # No process found using the port
        pass
    except Exception as e:
        print(f"[WARN] Port cleanup failed: {e}")

kill_port(5000)

app = Flask(__name__, template_folder='templates')

# Directory setup for downloads
LOG_DIR = os.path.abspath("logs")
ARCHIVE_DIR = os.path.join(LOG_DIR, "previous_data")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

latest_data = {"timestamp": "", "data": {}}
history = {"Elapsed [s]": []}  # For graphing
for key in [
    "Temp_BME280 [°C]", "Hum [%]", "Press [hPa]", "Alt [m]",
    "Acc x [m/s²]", "Acc y [m/s²]", "Acc z [m/s²]",
    "Gyro x [°/s]", "Gyro y [°/s]", "Gyro z [°/s]",
    "Temp_MPU [°C]"
]:
    history[key] = []

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template("dashboard.html")


@app.route("/update", methods=["POST"])
def update():
    global latest_data, history
    content = request.json
    latest_data = content

    elapsed = float(content["data"]["Elapsed [s]"])
    history["Elapsed [s]"].append(elapsed)

    for key in history:
        if key != "Elapsed [s]":
            try:
                history[key].append(float(content["data"][key]))
            except:
                history[key].append(None)

    return jsonify(status="ok")


@app.route("/data", methods=["GET"])
def get_data():
    return jsonify({
        "timestamp": latest_data["timestamp"],
        "history": history
    })

@app.route("/generate_random_data", methods=["POST"])
def generate_random_data():
    global latest_data, history
    
    # Get current elapsed time or start from 0
    current_elapsed = history["Elapsed [s]"][-1] if history["Elapsed [s]"] else 0
    new_elapsed = current_elapsed + random.uniform(1.0, 3.0)  # 1-3 second increment
    
    # Generate realistic sensor data
    random_data = {
        "Elapsed [s]": round(new_elapsed, 2),
        "Temp_BME280 [°C]": round(random.uniform(15.0, 35.0) + random.gauss(0, 0.5), 2),
        "Hum [%]": round(random.uniform(30.0, 80.0) + random.gauss(0, 2.0), 1),
        "Press [hPa]": round(random.uniform(980.0, 1020.0) + random.gauss(0, 1.0), 1),
        "Alt [m]": round(random.uniform(-50.0, 200.0) + random.gauss(0, 5.0), 1),
        "Acc x [m/s²]": round(random.gauss(0, 0.3), 3),
        "Acc y [m/s²]": round(random.gauss(0, 0.3), 3),
        "Acc z [m/s²]": round(random.uniform(9.5, 10.2) + random.gauss(0, 0.2), 3),  # Gravity + noise
        "Gyro x [°/s]": round(random.gauss(0, 10.0), 2),
        "Gyro y [°/s]": round(random.gauss(0, 10.0), 2),
        "Gyro z [°/s]": round(random.gauss(0, 10.0), 2),
        "Temp_MPU [°C]": round(random.uniform(20.0, 40.0) + random.gauss(0, 0.5), 2)
    }
    
    # Create properly formatted data structure
    generated_payload = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": random_data
    }
    
    # Update global data structures (same as /update endpoint)
    latest_data = generated_payload
    history["Elapsed [s]"].append(new_elapsed)
    
    for key in history:
        if key != "Elapsed [s]":
            try:
                history[key].append(float(random_data[key]))
            except:
                history[key].append(None)
    
    return jsonify({"status": "success", "message": "Random data generated"})

@app.route("/save_session_csv", methods=["POST"])
def save_session_csv():
    """Save current session data to a proper CSV file"""
    global history

    if not history.get("Elapsed [s]") or len(history["Elapsed [s]"]) == 0:
        return jsonify({"status": "error", "message": "No data to save"}), 400

    try:
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sensor_data_{timestamp}.csv"
        filepath = os.path.join(LOG_DIR, filename)

        # Move any existing files to archive
        import glob
        import shutil
        for file in glob.glob(os.path.join(LOG_DIR, "sensor_data_*.csv")):
            shutil.move(file, ARCHIVE_DIR)

        # Write CSV with proper comma-delimited format
        headers = ["MET [s]"] + [
            "Elapsed [s]", "Temp_BME280 [°C]", "Hum [%]", "Press [hPa]", "Alt [m]",
            "Acc x [m/s²]", "Acc y [m/s²]", "Acc z [m/s²]",
            "Gyro x [°/s]", "Gyro y [°/s]", "Gyro z [°/s]", "Temp_MPU [°C]"
        ]

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(",".join(headers) + "\n")

            num_rows = len(history.get("Elapsed [s]", []))
            for i in range(num_rows):
                row = []
                # MET timestamp (use elapsed time as MET)
                elapsed = history.get("Elapsed [s]", [0])[i] if i < len(history.get("Elapsed [s]", [])) else 0
                row.append(f"{elapsed:.3f}")

                # Add all other columns
                for key in headers[1:]:
                    values = history.get(key, [])
                    if i < len(values) and values[i] is not None:
                        row.append(f"{values[i]:.3f}" if isinstance(values[i], (int, float)) else str(values[i]))
                    else:
                        row.append("")

                f.write(",".join(row) + "\n")

        return jsonify({
            "status": "success",
            "message": f"Saved {num_rows} rows to {filename}",
            "filename": filename,
            "rows": num_rows
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/clear_test_data", methods=["POST"])
def clear_test_data():
    global latest_data, history
    
    # Clear all data
    latest_data = {"timestamp": "", "data": {}}
    history = {"Elapsed [s]": []}  # Reset to empty arrays
    for key in [
        "Temp_BME280 [°C]", "Hum [%]", "Press [hPa]", "Alt [m]",
        "Acc x [m/s²]", "Acc y [m/s²]", "Acc z [m/s²]",
        "Gyro x [°/s]", "Gyro y [°/s]", "Gyro z [°/s]",
        "Temp_MPU [°C]"
    ]:
        history[key] = []
    
    return jsonify({"status": "success", "message": "Test data cleared"})

@app.route('/download/latest')
def download_latest():
    files = sorted([f for f in os.listdir(LOG_DIR) if f.startswith("sensor_data_")], reverse=True)
    if files:
        return send_from_directory(LOG_DIR, files[0], as_attachment=True)
    return "No log files found", 404

@app.route('/download/list')
def list_logs():
    files = sorted([f for f in os.listdir(ARCHIVE_DIR) if f.endswith(".csv")])
    return jsonify(files)

@app.route('/download/archive/<filename>')
def download_archive(filename):
    path = os.path.join(ARCHIVE_DIR, filename)
    if os.path.isfile(path):
        return send_from_directory(ARCHIVE_DIR, filename, as_attachment=True)
    return "File not found", 404

@app.route('/api/missions/list', methods=['GET'])
def list_missions():
    """List all available mission CSV files from logs/ and logs/previous_data/"""
    missions = []

    # Get files from main logs directory
    try:
        for f in os.listdir(LOG_DIR):
            if f.endswith('.csv'):
                filepath = os.path.join(LOG_DIR, f)
                stat = os.stat(filepath)
                missions.append({
                    'filename': f,
                    'path': 'logs',
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
    except Exception as e:
        print(f"[WARN] Error reading logs directory: {e}")

    # Get files from archive directory
    try:
        for f in os.listdir(ARCHIVE_DIR):
            if f.endswith('.csv'):
                filepath = os.path.join(ARCHIVE_DIR, f)
                stat = os.stat(filepath)
                missions.append({
                    'filename': f,
                    'path': 'logs/previous_data',
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
    except Exception as e:
        print(f"[WARN] Error reading archive directory: {e}")

    # Sort by modified date (newest first)
    missions.sort(key=lambda x: x['modified'], reverse=True)

    return jsonify(missions)


@app.route('/api/missions/load/<path:filepath>', methods=['GET'])
def load_mission(filepath):
    """Load and parse a mission CSV file, returning data as JSON"""
    import csv
    import re

    # Security: only allow files from logs/ or logs/previous_data/
    if filepath.startswith('logs/previous_data/'):
        full_path = os.path.join(ARCHIVE_DIR, os.path.basename(filepath))
    elif filepath.startswith('logs/'):
        full_path = os.path.join(LOG_DIR, os.path.basename(filepath))
    else:
        return jsonify({'error': 'Invalid path'}), 400

    if not os.path.isfile(full_path):
        return jsonify({'error': 'File not found'}), 404

    try:
        data = {}
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        file_content = None

        for encoding in encodings:
            try:
                with open(full_path, 'r', encoding=encoding) as f:
                    file_content = f.read()
                break
            except UnicodeDecodeError:
                continue

        if file_content is None:
            return jsonify({'error': 'Could not decode file with any supported encoding'}), 500

        lines = file_content.strip().split('\n')
        if not lines:
            return jsonify({'error': 'Empty file'}), 400

        first_line = lines[0]

        # Detect format: comma-delimited, semicolon-delimited, or fixed-width
        is_semicolon_csv = ';' in first_line and first_line.count(';') >= 5
        is_comma_csv = ',' in first_line and first_line.count(',') >= 5

        if is_semicolon_csv:
            # Semicolon-delimited CSV (common in European Excel)
            import io
            reader = csv.DictReader(io.StringIO(file_content), delimiter=';')
            headers = reader.fieldnames

            for header in headers:
                data[header] = []

            for row in reader:
                for header in headers:
                    try:
                        value = float(row[header])
                    except (ValueError, TypeError):
                        value = row[header]
                    data[header].append(value)
        elif is_comma_csv:
            # Standard comma-delimited CSV
            import io
            reader = csv.DictReader(io.StringIO(file_content), delimiter=',')
            headers = reader.fieldnames

            for header in headers:
                data[header] = []

            for row in reader:
                for header in headers:
                    try:
                        value = float(row[header])
                    except (ValueError, TypeError):
                        value = row[header]
                    data[header].append(value)
        else:
            # Fixed-width format from legacy lorareceivertest.py
            # The header has known column names - use them to define expected structure
            expected_headers = [
                "Timestamp (MET)", "Elapsed [s]", "Temp_BME280 [°C]", "Hum [%]",
                "Press [hPa]", "Alt [m]", "Acc x [m/s²]", "Acc y [m/s²]",
                "Acc z [m/s²]", "Gyro x [°/s]", "Gyro y [°/s]", "Gyro z [°/s]",
                "Temp_MPU [°C]"
            ]

            # Check if this looks like our legacy format
            if "Timestamp (MET)" in first_line or "Elapsed [s]" in first_line:
                headers = expected_headers
            else:
                # Fallback to splitting by multiple spaces
                header_parts = re.split(r'\s{2,}', first_line.strip())
                headers = [h.strip() for h in header_parts if h.strip()]

            for header in headers:
                data[header] = []

            # Parse data rows - split by multiple whitespace
            for line in lines[1:]:
                if not line.strip():
                    continue
                # Skip MIN/MAX summary lines at the end
                if line.strip().startswith('MIN,') or line.strip().startswith('MAX,'):
                    continue

                # Split by multiple spaces (2+ spaces)
                values = re.split(r'\s{2,}', line.strip())
                values = [v.strip() for v in values if v.strip()]

                # Match values to headers
                for i, header in enumerate(headers):
                    if i < len(values):
                        try:
                            value = float(values[i])
                        except (ValueError, TypeError):
                            value = values[i]
                        data[header].append(value)

        # Get file info
        stat = os.stat(full_path)

        return jsonify({
            'filename': os.path.basename(full_path),
            'headers': headers,
            'data': data,
            'rowCount': len(data.get(headers[0], [])) if headers else 0,
            'fileSize': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        })

    except Exception as e:
        return jsonify({'error': f'Failed to parse CSV: {str(e)}'}), 500


@app.route('/open_logs_folder', methods=['POST'])
def open_logs_folder():
    try:
        # Get absolute path to logs directory for security
        logs_path = os.path.abspath(LOG_DIR)

        # Ensure logs directory exists
        if not os.path.exists(logs_path):
            return jsonify({"status": "error", "message": "Logs directory does not exist"}), 404

        # Open folder based on operating system
        system = platform.system()
        if system == "Windows":
            os.startfile(logs_path)
        elif system == "Darwin":  # macOS
            subprocess.run(["open", logs_path], check=True)
        elif system == "Linux":
            subprocess.run(["xdg-open", logs_path], check=True)
        else:
            return jsonify({"status": "error", "message": f"Unsupported operating system: {system}"}), 400

        return jsonify({"status": "success", "message": "Logs folder opened successfully"})

    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to open logs folder: {str(e)}"}), 500


# ==================== Configuration API Endpoints ====================

@app.route('/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    config = load_config()
    return jsonify(config)


@app.route('/config', methods=['POST'])
def update_config():
    """Update configuration"""
    try:
        new_config = request.json
        if not new_config:
            return jsonify({"error": "No configuration data provided"}), 400

        # Load current config and merge with new values
        current_config = load_config()

        # Update top-level values
        if 'sea_level_pressure' in new_config:
            current_config['sea_level_pressure'] = float(new_config['sea_level_pressure'])
        if 'update_frequency' in new_config:
            current_config['update_frequency'] = float(new_config['update_frequency'])
        if 'history_length' in new_config:
            current_config['history_length'] = int(new_config['history_length'])

        # Update transmission thresholds
        if 'transmission_thresholds' in new_config:
            for key, value in new_config['transmission_thresholds'].items():
                if key in current_config['transmission_thresholds']:
                    current_config['transmission_thresholds'][key] = float(value)

        save_config(current_config)
        return jsonify({"status": "success", "config": current_config})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/config/reset', methods=['POST'])
def reset_config():
    """Reset configuration to defaults"""
    try:
        save_config(DEFAULT_CONFIG.copy())
        return jsonify({"status": "success", "config": DEFAULT_CONFIG})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/config/profiles', methods=['GET'])
def get_profiles():
    """List all saved configuration profiles"""
    profiles = list_profiles()
    return jsonify({"profiles": profiles})


@app.route('/config/profiles/<name>', methods=['GET'])
def get_profile(name):
    """Load a specific configuration profile"""
    try:
        profile_path = get_profile_path(name)
        if not os.path.exists(profile_path):
            return jsonify({"error": f"Profile '{name}' not found"}), 404

        with open(profile_path, 'r', encoding='utf-8') as f:
            profile = json.load(f)
        return jsonify(profile)

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/config/profiles/<name>', methods=['POST'])
def save_profile(name):
    """Save current configuration as a named profile"""
    try:
        profile_path = get_profile_path(name)

        # Get current config or use provided config
        if request.json:
            config = request.json
        else:
            config = load_config()

        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)

        return jsonify({"status": "success", "message": f"Profile '{name}' saved"})

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/config/profiles/<name>', methods=['DELETE'])
def delete_profile(name):
    """Delete a configuration profile"""
    try:
        profile_path = get_profile_path(name)
        if not os.path.exists(profile_path):
            return jsonify({"error": f"Profile '{name}' not found"}), 404

        os.remove(profile_path)
        return jsonify({"status": "success", "message": f"Profile '{name}' deleted"})

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/config/profiles/<name>/apply', methods=['POST'])
def apply_profile(name):
    """Apply a profile as the current configuration"""
    try:
        profile_path = get_profile_path(name)
        if not os.path.exists(profile_path):
            return jsonify({"error": f"Profile '{name}' not found"}), 404

        with open(profile_path, 'r', encoding='utf-8') as f:
            profile = json.load(f)

        save_config(profile)
        return jsonify({"status": "success", "config": profile})

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def cleanup():
    try:
        if platform.system() == "Windows":
            # Windows cleanup
            result = subprocess.check_output('netstat -ano | findstr :5000', shell=True).decode().strip()
            if result:
                lines = result.splitlines()
                for line in lines:
                    if 'LISTENING' in line:
                        pid = line.split()[-1]
                        try:
                            subprocess.run(f'taskkill /F /PID {pid}', shell=True, check=True)
                            print(f"[INFO] Killed leftover process on port 5000 (PID {pid})")
                        except subprocess.CalledProcessError:
                            pass  # Process may have already ended
        else:
            # Unix/Linux cleanup
            result = subprocess.check_output(["lsof", "-t", "-i:5000"]).decode().strip()
            if result:
                for pid in result.splitlines():
                    os.kill(int(pid), signal.SIGKILL)
                    print(f"[INFO] Killed leftover process on port 5000 (PID {pid})")
    except Exception as e:
        print(f"[WARN] Cleanup failed or port already free: {e}")

cleanup()
atexit.register(cleanup)


if __name__ == "__main__":
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)  # Or use logging.CRITICAL to suppress all output

    try:
        app.run(debug=False, host="0.0.0.0", use_reloader=False)
    except KeyboardInterrupt:
        print("\nCaught Ctrl+C, shutting down...")
        cleanup()
