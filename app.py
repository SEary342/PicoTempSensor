from flask import Flask, request, render_template_string, jsonify
from datetime import datetime
from pico.shared_html import get_html_template

app = Flask(__name__)

# Global storage for the latest data received from the Pico
# Initialized with placeholders
last_data = {
    "temp_c": "--", 
    "temp_f": "--", 
    "temp_k": "--", 
    "hum": "--", 
    "status": "Waiting...", 
    "time": "No data yet"
}

@app.route('/', methods=['GET'])
def dashboard():
    """
    Serves the beautifully formatted HTML dashboard using 
    the shared template file.
    """
    return render_template_string(get_html_template(last_data))

@app.route('/api', methods=['GET'])
def api_view():
    """
    Returns the last received sensor data as raw JSON.
    Useful for other scripts or integrations.
    """
    return jsonify(last_data), 200

@app.route('/data', methods=['POST'])
def receive_data():
    """
    Endpoint for the Pico to 'PUSH' its data.
    Expected JSON format: {"temp_c": 22, "temp_f": 71.6, ...}
    """
    global last_data
    
    incoming = request.json
    if not incoming:
        return jsonify({"status": "error", "message": "No JSON provided"}), 400
    
    # Update our global state with the new data
    last_data = incoming
    
    # Add a laptop-side timestamp so we know exactly when it arrived
    last_data['time'] = datetime.now().strftime("%I:%M:%S %p")
    
    print(f"[{last_data['time']}] Update from Pico: {last_data.get('temp_f')}°F | {last_data.get('hum')}% Hum")
    
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    # host='0.0.0.0' allows the Pico to find this server on your local network
    # port=5000 is the default Flask port
    print("--- Pico Receiver Server Started ---")
    print("Access the dashboard at: http://localhost:5000")
    print("Waiting for Pico PUSH data...")
    app.run(host='0.0.0.0', port=5000, debug=True)