# pipeline.py
import os
import sys
import subprocess
import pandas as pd
from google.cloud import storage

# ----------------------------
# CONFIGURATION
# ----------------------------
BUCKET_NAME = "tomtom-traffic-data"
TRAFFIC_FILE = "tomtom_traffic.csv"

LOCAL_TRAFFIC = "traffic.csv"
LOCAL_WEATHER = "weather.csv"
MERGED_FILE = "merged.csv"
EXCEL_FILE = "pipeline_output.xlsx"

WEATHER_SCRIPT = "Tomorrow.py"

# ----------------------------
# STEP 1: DOWNLOAD TRAFFIC DATA FROM GCS
# ----------------------------
def download_traffic():
    print("Downloading traffic data from GCS...")
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(TRAFFIC_FILE)
    blob.download_to_filename(LOCAL_TRAFFIC)
    print(f"Traffic data saved to {LOCAL_TRAFFIC}")

# ----------------------------
# STEP 2: RUN WEATHER SCRIPT
# ----------------------------
def run_weather():
    print("Running weather script...")
    # result = subprocess.run(["python", WEATHER_SCRIPT], capture_output=True, text=True)
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
    WEATHER_SCRIPT = os.path.join(PROJECT_DIR, "Tomorrow.py")
    result = subprocess.run([sys.executable, WEATHER_SCRIPT], check=True)

    if result.returncode != 0:
        print("Weather script failed:")
        print(result.stderr)
        raise Exception("Weather script error")
    else:
        print(f"Weather data saved to {LOCAL_WEATHER}")

# ----------------------------
# STEP 3: MERGE DATASETS
# ----------------------------
def merge_data():
    print("Merging traffic and weather data...")

    # Load datasets
    df_traffic = pd.read_csv(LOCAL_TRAFFIC)
    df_weather = pd.read_csv(LOCAL_WEATHER)

    traffic_time_col = "timestamp"
    weather_time_col = "time"

    # Parse traffic timestamps (day/month/year)
    df_traffic[traffic_time_col] = pd.to_datetime(df_traffic[traffic_time_col], dayfirst=True)
    df_traffic[traffic_time_col] = df_traffic[traffic_time_col].dt.round("h")
    # df_traffic[traffic_time_col] = pd.to_datetime(df_traffic[traffic_time_col], dayfirst=True)

    # Parse weather timestamps (year-month-day)
    df_weather[weather_time_col] = pd.to_datetime(df_weather[weather_time_col], dayfirst=True)
    df_weather[weather_time_col] = df_weather[weather_time_col].dt.round("h")
    # df_weather[weather_time_col] = pd.to_datetime(df_weather[weather_time_col], dayfirst=True)


    # Merge on nearest hour with 1-hour tolerance
    df_merged = pd.merge_asof(
        df_traffic.sort_values(traffic_time_col),
        df_weather.sort_values(weather_time_col),
        left_on=traffic_time_col,
        right_on=weather_time_col,
        direction="nearest",
        tolerance=pd.Timedelta("1h")
    )

    # Save merged CSV
    df_merged.to_csv(MERGED_FILE, index=False)
    print(f"Merged dataset saved to {MERGED_FILE}")

    # Export Excel with 3 sheets
    with pd.ExcelWriter(EXCEL_FILE, engine='xlsxwriter') as writer:
        df_weather.to_excel(writer, sheet_name="Weather", index=False)
        df_traffic.to_excel(writer, sheet_name="Traffic", index=False)
        df_merged.to_excel(writer, sheet_name="Merged", index=False)
    print(f"Excel file with 3 sheets saved as {EXCEL_FILE}")

# ----------------------------
# MAIN
# ----------------------------
if __name__ == "__main__":
    download_traffic()
    run_weather()
    merge_data()
    print("Pipeline completed successfully.")
