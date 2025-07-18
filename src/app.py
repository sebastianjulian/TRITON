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


from flask import Flask, request, jsonify, render_template
from datetime import datetime

app = Flask(__name__)
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



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
