# # from flask import Flask, request, render_template, jsonify
# # import time
# # from collections import defaultdict, deque

# # app = Flask(__name__)
# # latest_data = {}
# # history = defaultdict(lambda: deque(maxlen=300))  # store last 300 values per field

# # @app.route('/')
# # def dashboard():
# #     return render_template('dashboard.html')

# # @app.route('/update', methods=['POST'])
# # def update():
# #     global latest_data
# #     latest_data = request.json
# #     timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
# #     latest_data["timestamp"] = timestamp

# #     # Save to history for each field
# #     elapsed = latest_data["data"].get("Elapsed [s]")
# #     for key, value in latest_data["data"].items():
# #         try:
# #             val = float(value)
# #             history[key].append(val)
# #         except:
# #             continue
# #     history["Elapsed [s]"].append(float(elapsed))

# #     return jsonify({"status": "ok"})

# # @app.route('/data')
# # def get_data():
# #     return jsonify({"history": {k: list(v) for k, v in history.items()}})

# # if __name__ == '__main__':
# #     app.run(host='0.0.0.0', port=5000)

# from flask import Flask, request, render_template, jsonify, send_from_directory
# import time
# import os
# from collections import defaultdict, deque

# app = Flask(__name__)

# # ───── Directories ─────
# LOG_DIR = "logs"
# ARCHIVE_DIR = os.path.join(LOG_DIR, "previous_data")
# os.makedirs(LOG_DIR, exist_ok=True)
# os.makedirs(ARCHIVE_DIR, exist_ok=True)

# # ───── Data Store ─────
# latest_data = {}
# history = defaultdict(lambda: deque(maxlen=300))  # Store last 300 values per field

# # ───── Routes ─────

# @app.route('/')
# def dashboard():
#     return render_template('dashboard.html')

# @app.route('/update', methods=['POST'])
# def update():
#     global latest_data
#     latest_data = request.json
#     timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
#     latest_data["timestamp"] = timestamp

#     # Save to history
#     elapsed = latest_data["data"].get("Elapsed [s]")
#     for key, value in latest_data["data"].items():
#         try:
#             val = float(value)
#             history[key].append(val)
#         except:
#             continue
#     try:
#         history["Elapsed [s]"].append(float(elapsed))
#     except:
#         pass

#     return jsonify({"status": "ok"})

# @app.route('/data')
# def get_data():
#     return jsonify({"history": {k: list(v) for k, v in history.items()}})

# @app.route('/download/latest')
# def download_latest():
#     files = sorted([
#         f for f in os.listdir(LOG_DIR)
#         if f.startswith("sensor_data_") and f.endswith(".csv")
#     ], reverse=True)
#     if files:
#         return send_from_directory(LOG_DIR, files[0], as_attachment=True)
#     return "No log files found", 404

# @app.route('/download/list')
# def list_archived_logs():
#     files = sorted([
#         f for f in os.listdir(ARCHIVE_DIR)
#         if f.startswith("sensor_data_") and f.endswith(".csv")
#     ])
#     return jsonify(files)

# @app.route('/download/archive/<filename>')
# def download_archived_log(filename):
#     safe_path = os.path.join(ARCHIVE_DIR, filename)
#     if os.path.isfile(safe_path):
#         return send_from_directory(ARCHIVE_DIR, filename, as_attachment=True)
#     return "File not found", 404

# # ───── App Entry Point ─────
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)


from flask import Flask, request, render_template, jsonify, send_from_directory
import time
import os
from collections import defaultdict, deque

app = Flask(__name__)

LOG_DIR = "logs"
ARCHIVE_DIR = os.path.join(LOG_DIR, "previous_data")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

latest_data = {}
history = defaultdict(lambda: deque(maxlen=300))
stats = {"min": {}, "max": {}, "avg": {}}
sums = defaultdict(float)
counts = defaultdict(int)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/update', methods=['POST'])
def update():
    global latest_data
    payload = request.json
    latest_data = payload
    data = payload.get("data", {})
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    latest_data["timestamp"] = timestamp

    for key, val in data.items():
        try:
            fval = float(val)
            history[key].append(fval)
            sums[key] += fval
            counts[key] += 1

            if key not in stats["min"] or fval < stats["min"][key]:
                stats["min"][key] = fval
            if key not in stats["max"] or fval > stats["max"][key]:
                stats["max"][key] = fval
            stats["avg"][key] = sums[key] / counts[key]
        except:
            continue

    try:
        elapsed = float(data.get("Elapsed [s]", 0))
        history["Elapsed [s]"].append(elapsed)
    except:
        pass

    return jsonify({"status": "ok"})

@app.route('/data')
def get_data():
    return jsonify({
        "history": {k: list(v) for k, v in history.items()},
        "stats": stats
    })

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
