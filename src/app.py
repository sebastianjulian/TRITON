from flask import Flask, request, jsonify, render_template_string
import threading

app = Flask(__name__)
latest_data = {"timestamp": "No data received", "data": {}}
lock = threading.Lock()

# HTML template for the dashboard
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>CanSat Sensor Dashboard</title>
    <meta http-equiv="refresh" content="2">
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f4; padding: 2em; }
        h1 { color: #333; }
        table { border-collapse: collapse; width: 60%; }
        th, td { border: 1px solid #888; padding: 8px 12px; text-align: left; }
        th { background-color: #eee; }
    </style>
</head>
<body>
    <h1>CanSat Live Sensor Data</h1>
    <p><strong>Last Update:</strong> {{ timestamp }}</p>
    <table>
        <tr><th>Sensor</th><th>Value</th></tr>
        {% for key, value in data.items() %}
        <tr><td>{{ key }}</td><td>{{ value }}</td></tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def dashboard():
    with lock:
        return render_template_string(HTML_TEMPLATE, timestamp=latest_data["timestamp"], data=latest_data["data"])

@app.route("/update", methods=["POST"])
def update_data():
    global latest_data
    new_data = request.get_json()
    if new_data:
        with lock:
            latest_data = new_data
    return jsonify(status="ok")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


