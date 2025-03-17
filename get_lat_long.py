import pandas as pd
import requests
import time

# Load UK postcode dataset
postcode_df = pd.read_csv(r"support_data/ukpostcodes.csv")  # Ensure it has 'postcode', 'latitude', 'longitude'

# Clean and format postcode column
postcode_df["postcode"] = postcode_df["postcode"].str.replace(" ", "").str.upper()

# Cache to store previously fetched lat/lon values
geo_cache = {}

# Function to get latitude and longitude using Nominatim with caching
def get_lat_long(location):
    if location in geo_cache:  # Check if we already fetched it
        return geo_cache[location]
    
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": location,
        "format": "json",
        "limit": 1
    }
    headers = {"User-Agent": "GeoLookupApp/1.0"}
    
    try:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data:
            lat, lon = data[0]["lat"], data[0]["lon"]
            geo_cache[location] = (lat, lon)  # Store in cache
            time.sleep(1)  # Prevent rate limiting issues
            return lat, lon
        else:
            return None, None  # No result found
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {location}: {e}")
        return None, None

# Function to get lat/lon from local postcode CSV
def get_lat_long_offline(postcode):
    postcode = postcode.replace(" ", "").upper()
    match = postcode_df[postcode_df["postcode"] == postcode]
    if not match.empty:
        return match["latitude"].values[0], match["longitude"].values[0]
    return None, None

# Function to apply to a DataFrame with caching and offline lookup
def add_lat_long(df, location_column):
    def lookup_location(location):
        if any(char.isdigit() for char in location):  # If contains numbers, it's a postcode
            return get_lat_long_offline(location)
        else:  # Otherwise, it's a city
            return get_lat_long(location)
    
    df["latitude"], df["longitude"] = zip(*df[location_column].apply(lookup_location))
    return df

# Example usage:
# df = pd.DataFrame({"locationName": ["Manchester", "HG1 5HH", "London", "Birmingham", "OX1 3DP"]})
# df = add_lat_long(df, "locationName")
# print(df)