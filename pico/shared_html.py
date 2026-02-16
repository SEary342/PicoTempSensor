def get_html_template(data):
    """
    Common UI for both Pico and Flask.
    Expects data dict with: temp_f, temp_c, temp_k, hum, time/last_update, refresh_ms
    """
    # Dynamic styling based on temperature
    try:
        temp = float(data.get("temp_f", 0))
        if temp < 60:
            status_color, icon_path = (
                "#3b82f6",
                '<path d="M12 2v20M4.93 4.93l14.14 14.14M2 12h20M4.93 19.07L19.07 4.93"></path>',
            )
        elif temp > 85:
            status_color, icon_path = (
                "#ef4444",
                '<circle cx="12" cy="12" r="4"></circle><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"></path>',
            )
        else:
            status_color, icon_path = (
                "#10b981",
                '<path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"></path>',
            )
    except Exception:
        status_color, icon_path = "#64748b", '<circle cx="12" cy="12" r="10"></circle>'

    refresh_ms = data.get("refresh_ms", 30000)

    # Use .get() with defaults to prevent crashes if a key is missing
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Env Monitor</title>
    <style>
        :root {{ --primary: #0f172a; --accent: {status_color}; --bg: #f8fafc; }}
        body {{ font-family: -apple-system, sans-serif; background: var(--bg); color: var(--primary); display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
        .card {{ background: white; padding: 2.5rem; border-radius: 2rem; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.1); width: 90%; max-width: 350px; text-align: center; border-top: 8px solid var(--accent); }}
        .icon {{ margin-bottom: 1rem; color: var(--accent); }}
        svg {{ width: 64px; height: 64px; fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }}
        .label {{ font-size: 0.85rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.15em; }}
        .reading {{ font-size: 5rem; font-weight: 900; margin: 0.5rem 0; color: var(--primary); }}
        .grid {{ display: flex; justify-content: space-around; margin: 2rem 0; padding: 1.5rem 0; border-top: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9; }}
        .stat-item {{ display: flex; flex-direction: column; }}
        .stat-label {{ font-size: 0.7rem; color: #94a3b8; font-weight: 800; }}
        .stat-val {{ font-size: 1.1rem; font-weight: 700; color: #475569; }}
        .tag {{ background: var(--bg); padding: 8px 15px; border-radius: 20px; font-size: 0.9rem; font-weight: 600; color: var(--accent); display: inline-block; }}
        .footer {{ margin-top: 2rem; font-size: 0.7rem; color: #cbd5e1; }}
    </style>
    <script>setTimeout(() => location.reload(), {refresh_ms});</script>
</head>
<body>
    <div class="card">
        <div class="icon"><svg viewBox="0 0 24 24">{icon_path}</svg></div>
        <div class="label">Conditions</div>
        <div class="reading">{data.get("temp_f", "--")}°</div>
        <div class="grid">
            <div class="stat-item"><span class="stat-label">CELSIUS</span><span class="stat-val">{data.get("temp_c", "--")}°C</span></div>
            <div class="stat-item"><span class="stat-label">HUMIDITY</span><span class="stat-val">{data.get("hum", "--")}%</span></div>
            <div class="stat-item"><span class="stat-label">VOLTAGE</span><span class="stat-val">{data.get("vsys_volts", "--")}V</span></div>
        </div>
        <div class="tag">{data.get("temp_k", "--")} Kelvin</div>
        <div class="footer">Updated: {data.get("time", data.get("runtime_s", "Live"))}</div>
    </div>
</body>
</html>"""
