import dht
import machine
import network
import socket
import time
import json
import urequests

# Import your custom HTML helper
from shared_html import get_html_template


# --- Configuration Loader ---
def load_config():
    conf = {
        "MODE": "PUSH",
        "SSID": "YOUR_WIFI_NAME",
        "PASSWORD": "YOUR_WIFI_PASSWORD",
        "SENSOR_PIN": 16,
        "REPORT_URL": "http://your-server-ip/api",
        "SLEEP_MINS": 5,
    }
    try:
        with open(".env", "r") as f:
            for line in f:
                if "=" in line:
                    k, v = [x.strip() for x in line.split("=", 1)]
                    if k in ["SENSOR_PIN", "SLEEP_MINS"]:
                        conf[k] = int(v)
                    else:
                        conf[k] = v
    except Exception:
        print("Using default config (ensure .env exists for custom settings)")
    return conf


# --- Power & Battery Sensing ---
def is_usb_powered():
    """Detects if VBUS (USB) power is present to avoid the deepsleep reset glitch."""
    try:
        return machine.Pin("WL_GPIO2", machine.Pin.IN).value() == 1
    except Exception:
        return False


def get_vsys_voltage():
    """Reads the voltage on the VSYS pin for AA battery monitoring."""
    try:
        # Pin 29 on Pico W monitors VSYS
        vsys_adc = machine.ADC(29)
        raw = vsys_adc.read_u16()
        # Formula: (Reading / 65535) * 3.3V Reference * 3 (Voltage Divider)
        voltage = (raw * 3.3 * 3) / 65535
        return round(voltage, 2)
    except Exception:
        return 0.0


def get_reading(pin_num):
    """Fetches data from DHT11 and includes battery level."""
    try:
        sensor = dht.DHT11(machine.Pin(pin_num))
        sensor.measure()
        c = sensor.temperature()
        h = sensor.humidity()
        return {
            "status": "ok",
            "temp_c": round(c, 1),
            "temp_f": round(c * 9 / 5 + 32, 1),
            "hum": h,
            "vsys_volts": get_vsys_voltage(),
            "runtime_s": time.ticks_ms() // 1000,
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "vsys_volts": get_vsys_voltage()}


# --- Networking ---
def connect_wifi(ssid, pw):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print(f"Connecting to {ssid}...")
        wlan.connect(ssid, pw)
        for _ in range(15):
            if wlan.isconnected():
                print(f"Connected! IP: {wlan.ifconfig()[0]}")
                return wlan
            time.sleep(1)
    return wlan if wlan.isconnected() else None


# --- Mode: Server ---
def run_as_server(wlan, pin):
    ip = wlan.ifconfig()[0]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", 80))
    s.listen(5)
    print(f"Web Server running on http://{ip}")

    while True:
        cl = None
        try:
            cl, _ = s.accept()
            req = cl.recv(1024).decode("utf-8")
            data = get_reading(pin)

            # Route Handling
            if "GET /api" in req:
                content = json.dumps(data)
                mimetype = "application/json"
            else:
                content = get_html_template(data)  # Uses your shared_html.py
                mimetype = "text/html"

            response = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: {mimetype}\r\n"
                f"Content-Length: {len(content)}\r\n"
                f"Connection: close\r\n\r\n"
                f"{content}"
            )
            cl.send(response)
        except Exception as e:
            print(f"Server Error: {e}")
        finally:
            if cl:
                cl.close()


# --- Mode: Push ---
def run_as_push(wlan, config):
    pin = config["SENSOR_PIN"]
    url = config["REPORT_URL"]
    sleep_mins = config["SLEEP_MINS"]

    usb_mode = is_usb_powered()

    while True:
        # 1. Check if wlan is None or disconnected, and try to reconnect
        if wlan is None or not wlan.isconnected():
            wlan = connect_wifi(config["SSID"], config["PASSWORD"])

        # 2. Get data
        data = get_reading(pin)

        # 3. Only attempt push if wlan is NOT None
        if wlan and wlan.isconnected():
            print(f"Pushing: {data['temp_f']}F | {data['vsys_volts']}V")
            try:
                r = urequests.post(url, json=data, timeout=5)
                r.close()
            except Exception:
                print("Failed to reach server")
        else:
            print("Skipping push: No Wi-Fi connection")

        # 4. Smart Sleep
        if usb_mode:
            print(f"Waiting {sleep_mins}m (USB Loop)...")
            # Safety check for Pylance/Runtime
            if wlan:
                wlan.active(False)

            time.sleep(sleep_mins * 60)

            if wlan:
                wlan.active(True)
        else:
            print(f"Deep Sleeping {sleep_mins}m...")
            if wlan:
                wlan.active(False)
            time.sleep(1)
            machine.deepsleep(sleep_mins * 60 * 1000)


# --- Main Entry ---
def main():
    config = load_config()
    wlan = connect_wifi(config["SSID"], config["PASSWORD"])

    # If wlan is None, we still proceed to run_as_push
    # because that function now handles reconnection attempts.
    if config["MODE"].upper() == "SERVER":
        if wlan:
            run_as_server(wlan, config["SENSOR_PIN"])
        else:
            print("Server mode requires Wi-Fi. Resetting in 10s...")
            time.sleep(10)
            machine.reset()
    else:
        run_as_push(wlan, config)


if __name__ == "__main__":
    main()
