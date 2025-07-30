from flask import Flask, request, render_template, jsonify
import time
from collections import defaultdict, deque

app = Flask(__name__)
latest_data = {}
history = defaultdict(lambda: deque(maxlen=300))  # store last 300 values per field

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/update', methods=['POST'])
def update():
    global latest_data
    latest_data = request.json
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    latest_data["timestamp"] = timestamp

    # Save to history for each field
    elapsed = latest_data["data"].get("Elapsed [s]")
    for key, value in latest_data["data"].items():
        try:
            val = float(value)
            history[key].append(val)
        except:
            continue
    history["Elapsed [s]"].append(float(elapsed))

    return jsonify({"status": "ok"})

@app.route('/data')
def get_data():
    return jsonify({"history": {k: list(v) for k, v in history.items()}})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
