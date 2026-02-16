import json
from pathlib import Path
from flask import Flask, request, render_template_string, jsonify
from datetime import datetime
from pico.shared_html import get_html_template

app = Flask(__name__)

# File to store the latest data so all Gunicorn workers can access it
DATA_FILE = 'sensor_data.json'

DEFAULT_DATA = {
    "temp_c": "--", 
    "temp_f": "--", 
    "temp_k": "--", 
    "hum": "--", 
    "vsys_volts": "--",
    "status": "Waiting...", 
    "time": "No data yet"
}

def get_last_data():
    if Path(DATA_FILE).exists():
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_DATA

@app.route('/', methods=['GET'])
def dashboard():
    """
    Serves the beautifully formatted HTML dashboard using 
    the shared template file.
    """
    last_data = get_last_data()
    return render_template_string(get_html_template(last_data))

@app.route('/api', methods=['GET'])
def api_view():
    """
    Returns the last received sensor data as raw JSON.
    Useful for other scripts or integrations.
    """
    last_data = get_last_data()
    return jsonify(last_data), 200

@app.route('/data', methods=['POST'])
def receive_data():
    """
    Endpoint for the Pico to 'PUSH' its data.
    Expected JSON format: {"temp_c": 22, "temp_f": 71.6, ...}
    """
    incoming = request.json
    if not incoming:
        return jsonify({"status": "error", "message": "No JSON provided"}), 400
    
    # Update our state with the new data
    last_data = incoming
    
    # Add a laptop-side timestamp so we know exactly when it arrived
    last_data['time'] = datetime.now().strftime("%I:%M:%S %p")

    # Calculate Kelvin since it's not sent by Pico anymore
    if 'temp_c' in last_data:
        try:
            last_data['temp_k'] = round(float(last_data['temp_c']) + 273.15, 2)
        except (ValueError, TypeError):
            last_data['temp_k'] = "--"
    
    # Save to file so other workers see it
    with open(DATA_FILE, 'w') as f:
        json.dump(last_data, f)
    
    print(f"[{last_data['time']}] Update from Pico: {last_data.get('temp_f')}°F | {last_data.get('hum')}% Hum | {last_data.get('vsys_volts')}V")
    
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    # host='0.0.0.0' allows the Pico to find this server on your local network
    # port=5000 is the default Flask port
    print("--- Pico Receiver Server Started ---")
    print("Access the dashboard at: http://localhost:5000")
    print("Waiting for Pico PUSH data...")
    app.run(host='0.0.0.0', port=5000, debug=True)