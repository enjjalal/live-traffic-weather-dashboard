# Tomorrow.py
import requests
import pandas as pd
from datetime import datetime, timedelta

# Your Tomorrow.io API key
API_KEY = "M5uFTxChKuGAzvLsmNTkA7p0J7M9EFiO"
LOCATION = "London"

# Calculate UTC times for last 7 days ending at the current hour
end_time = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
start_time = end_time - timedelta(days=7)

start_iso = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
end_iso = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

url = f"https://api.tomorrow.io/v4/weather/history/recent?location={LOCATION}&apikey={API_KEY}&startTime={start_iso}&endTime={end_iso}"
r = requests.get(url)
data = r.json()

# Extract hourly weather data
rows = []
for hour in data.get("timelines", {}).get("hourly", []):
    rows.append({
        "time": hour["time"],
        "temperature": hour["values"].get("temperature"),
        "humidity": hour["values"].get("humidity"),
        "precipitation": hour["values"].get("precipitationProbability"),
        "windSpeed": hour["values"].get("windSpeed"),
        "cloudCover": hour["values"].get("cloudCover"),
        "iceAccumulation": hour["values"].get("iceAccumulation"),
        "pressureSurfaceLevel": hour["values"].get("pressureSurfaceLevel"),
        "rainAccumulation": hour["values"].get("rainAccumulation"),
        "rainIntensity": hour["values"].get("rainIntensity"),
        "visibility": hour["values"].get("visibility"),
        "weatherCode": hour["values"].get("weatherCode"),
        "windGust": hour["values"].get("windGust")
    })

# Save to CSV if data exists
if rows:
    df_weather = pd.DataFrame(rows)

    # Convert to datetime, remove timezone, round to nearest hour
    df_weather["time"] = pd.to_datetime(df_weather["time"], utc=True).dt.tz_convert(None)
    df_weather["time"] = df_weather["time"].dt.round("h")

    # Remove duplicate timestamps
    df_weather = df_weather.drop_duplicates(subset=["time"])

    # Save CSV
    df_weather.to_csv("weather.csv", index=False)
    print("Done, saved to weather.csv")
else:
    print("No weather data returned!")
