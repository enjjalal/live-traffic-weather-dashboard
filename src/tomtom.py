# API_KEY= "39067c66-f96b-467f-82b1-ce5c3edbabb7"
API_KEY= "jiFZ2Aar4Fmlm5xrWfji3TJrwY2U9zoa"

# import requests
# import pandas as pd
# import datetime

# # London bounding box (approximate)
# # format: minLon,minLat,maxLon,maxLat
# bbox = "-0.489,51.28,0.236,51.686"  
# point="51.5074,-0.1278"

# # url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?bbox={bbox}&key={API_KEY}"
# # url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={point}&unit=KMPH&key={API_KEY}"
# url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point=51.5074,-0.1278&key={API_KEY}"


# r = requests.get(url)
# data = r.json()

# # Flatten JSON into DataFrame
# df = pd.json_normalize(data)

# # Add timestamp for tracking
# df["timestamp"] = datetime.datetime.utcnow()

# # Save
# df.to_csv("tomtom_traffic.csv", index=False)
# print("✅ Real-time traffic data saved to tomtom_traffic.csv")
# print("Columns extracted:", df.columns.tolist())



import requests
import pandas as pd
import datetime
import os



# 2. Set up the API endpoint
# This example uses a single point for London.
point = "51.5074,-0.1278" 
url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={point}&key={API_KEY}"

# 3. Make the API request
try:
    r = requests.get(url)
    r.raise_for_status()  # This will raise an HTTPError if the request was unsuccessful
    data = r.json()
except requests.exceptions.RequestException as e:
    print(f"❌ Error fetching data: {e}")
    exit()

# 4. Flatten the JSON data into a DataFrame
df = pd.json_normalize(data)

# 5. Add a timestamp
df["timestamp"] = datetime.datetime.utcnow()

# 6. Save the data
output_file = "tomtom_traffic.csv"

# Check if the file exists to decide whether to write headers
file_exists = os.path.isfile(output_file)

if file_exists:
    # If the file exists, append without writing the header
    df.to_csv(output_file, mode='a', header=False, index=False)
    print(f"✅ Appended new traffic data to {output_file}")
else:
    # If the file doesn't exist, create it and write the header
    df.to_csv(output_file, index=False)
    print(f"✅ Created {output_file} and saved initial traffic data")

print("Columns extracted:", df.columns.tolist())