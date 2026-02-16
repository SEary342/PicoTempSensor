import dht
import machine
import network
import socket
import time
import json
import urequests

from shared_html import get_html_template


# --- Configuration Loader ---
def load_config():
    conf = {
        "MODE": "SERVER",
        "SSID": "",
        "PASSWORD": "",
        "SENSOR_PIN": 16,
        "REPORT_URL": "",
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
        pass
    print(f"Loaded config: {conf}")
    return conf


def get_reading(pin_num):
    """Fetches data from DHT11 and processes units."""
    try:
        sensor = dht.DHT11(machine.Pin(pin_num))
        sensor.measure()
        c = sensor.temperature()
        h = sensor.humidity()
        return {
            "status": "ok",
            "temp_c": round(c, 1),
            "temp_f": round(c * 9 / 5 + 32, 1),
            "temp_k": round(c + 273.15, 2),
            "hum": h,
            "runtime_s": time.ticks_ms() // 1000,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# --- Server / Routing Logic ---
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

            # Simple Router
            is_api = "GET /api" in req
            data = get_reading(pin)

            if is_api:
                content = json.dumps(data)
                mimetype = "application/json"
            else:
                content = get_html_template(data)
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


# --- Push Logic ---
def run_as_push(wlan, pin, url, sleep_mins):
    data = get_reading(pin)
    if wlan:
        try:
            r = urequests.post(url, json=data, timeout=5)
            r.close()
        except Exception:
            pass
        wlan.active(False)
    print(f"Sleeping for {sleep_mins} mins...")
    machine.deepsleep(sleep_mins * 60 * 1000)


def connect_wifi(ssid, pw):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, pw)
    for _ in range(15):
        if wlan.isconnected():
            return wlan
        time.sleep(1)
    return None


def main():
    config = load_config()
    wlan = connect_wifi(config["SSID"], config["PASSWORD"])

    if config["MODE"].upper() == "SERVER":
        if not wlan:
            time.sleep(10)
            machine.reset()
        run_as_server(wlan, config["SENSOR_PIN"])
    else:
        run_as_push(
            wlan, config["SENSOR_PIN"], config["REPORT_URL"], config["SLEEP_MINS"]
        )


if __name__ == "__main__":
    main()
