import csv
from datetime import datetime
import os
import pytz
import requests

API_KEY = os.environ.get("TOMTOM_API_KEY")
CSV_FILE = "plus_highway_traffic.csv"

LOCATIONS = [
    # Johor
    {"city": "Johor Bahru (Skudai)", "direction": "NB", "lat": 1.5364, "lon": 103.6562},
    {"city": "Johor Bahru (Skudai)", "direction": "SB", "lat": 1.5362, "lon": 103.6558},
    {"city": "Ayer Hitam", "direction": "NB", "lat": 1.9189, "lon": 103.1812},
    {"city": "Ayer Hitam", "direction": "SB", "lat": 1.9187, "lon": 103.1808},
    {"city": "Pagoh", "direction": "NB", "lat": 2.1485, "lon": 102.7712},
    {"city": "Pagoh", "direction": "SB", "lat": 2.1483, "lon": 102.7708},
    # Melaka & Negeri Sembilan
    {"city": "Melaka (Ayer Keroh)", "direction": "NB", "lat": 2.3138, "lon": 102.3194},
    {"city": "Melaka (Ayer Keroh)", "direction": "SB", "lat": 2.3136, "lon": 102.3190},
    {"city": "Seremban", "direction": "NB", "lat": 2.7105, "lon": 101.9168},
    {"city": "Seremban", "direction": "SB", "lat": 2.7103, "lon": 101.9164},
    {"city": "Nilai", "direction": "NB", "lat": 2.8152, "lon": 101.7965},
    {"city": "Nilai", "direction": "SB", "lat": 2.8150, "lon": 101.7961},
    # Klang Valley & Selangor
    {"city": "Kuala Lumpur (Sungai Besi)", "direction": "NB", "lat": 3.0478, "lon": 101.7061},
    {"city": "Kuala Lumpur (Sungai Besi)", "direction": "SB", "lat": 3.0476, "lon": 101.7057},
    {"city": "Rawang", "direction": "NB", "lat": 3.3214, "lon": 101.5542},
    {"city": "Rawang", "direction": "SB", "lat": 3.3212, "lon": 101.5538},
    # Perak
    {"city": "Tapah", "direction": "NB", "lat": 4.1956, "lon": 101.2618},
    {"city": "Tapah", "direction": "SB", "lat": 4.1954, "lon": 101.2614},
    {"city": "Ipoh", "direction": "NB", "lat": 4.6186, "lon": 101.1197},
    {"city": "Ipoh", "direction": "SB", "lat": 4.6184, "lon": 101.1193},
    # Penang & Kedah
    {"city": "Penang (Juru)", "direction": "NB", "lat": 5.3175, "lon": 100.4368},
    {"city": "Penang (Juru)", "direction": "SB", "lat": 5.3173, "lon": 100.4364},
    {"city": "Alor Setar", "direction": "NB", "lat": 6.1184, "lon": 100.3882},
    {"city": "Alor Setar", "direction": "SB", "lat": 6.1182, "lon": 100.3878},
]



def classify_traffic(current_speed, free_flow_speed, road_closure):
    if road_closure or free_flow_speed == 0:
        return "Standstill"
    ratio = current_speed / free_flow_speed
    if ratio > 0.85:
        return "Free"
    elif ratio > 0.60:
        return "Light"
    elif ratio > 0.30:
        return "Heavy"
    return "Standstill"

def main():
    kl_tz = pytz.timezone("Asia/Kuala_Lumpur")
    now = datetime.now(kl_tz)
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    day_of_week = now.strftime("%A")

    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "timestamp", "day_of_week", "city", "direction",
                "current_speed", "free_flow_speed", "speed_ratio", "traffic_level"
            ])

        for loc in LOCATIONS:
            base_url = "https://" + ".".join(["api", "tomtom", "com"])
            path = "/traffic/services/4/flowSegmentData/absolute/10/json"
            coords = f"?point={loc['lat']},{loc['lon']}&key={API_KEY}"
            url = base_url + path + coords
            res = requests.get(url, timeout=10).json()
            flow = res.get("flowSegmentData", {})

            curr = flow.get("currentSpeed", 0)
            free = flow.get("freeFlowSpeed", 0)
            closed = flow.get("roadClosure", False)
            ratio = round(curr / free, 3) if free > 0 else 0
            level = classify_traffic(curr, free, closed)

            writer.writerow([timestamp, day_of_week, loc["city"], loc["direction"], curr, free, ratio, level])
            print(f"{timestamp} | {loc['city']} ({loc['direction']}): {curr}/{free} km/h -> {level}")

if __name__ == "__main__":
    main()

