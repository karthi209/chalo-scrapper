from selenium import webdriver
from bs4 import BeautifulSoup
import time
import json
from selenium.webdriver.common.by import By
import requests
import os

# Function to convert data to GeoJSON format
def convert_to_geojson(data):
    features = []
    for stop in data["stopSequenceWithDetails"]:
        feature = {
            "type": "Feature",
            "properties": {
                "route_name": route_number,
                "stop_id": stop["stop_id"],
                "name": stop["stop_name"],
                "city": stop["city"]
            },
            "geometry": {
                "type": "Point",
                "coordinates": [stop["stop_lon"], stop["stop_lat"]]
            }
        }
        features.append(feature)

    feature_collection = {
        "type": "FeatureCollection",
        "features": features
    }

    return feature_collection

with open("route_numbers.txt", "r") as file:
    route_numbers = file.readlines()

for route_number in route_numbers:

    driver = webdriver.Chrome()

# Navigate to Chalo URL
    driver.get("https://chalo.com/app/live-tracking")

    time.sleep(3)

    # Select Chennai is the focus city
    select_chn = driver.find_element(By.XPATH, "//div[contains(text(), 'Chennai')]")
    select_chn.click()

    time.sleep(3)

    # Click the Get Started button
    select_get_started = driver.find_element(By.XPATH, "//button[contains(text(), 'Get Started')]")
    select_get_started.click()

    time.sleep(5)
    # Search using the Route Number
    search_b = driver.find_element(By.CLASS_NAME, "searchInputs")
    select_searchbar = search_b.find_element(By.TAG_NAME, "input")
    select_searchbar.clear()  # Clear search bar
    select_searchbar.send_keys(route_number.strip())  # Strip to remove leading/trailing whitespaces
    
    time.sleep(3)

    # Click the first result
    first_result = driver.find_element(By.CLASS_NAME, "MuiList-root")
    first_result.click()

    time.sleep(3)

    network_requests = driver.execute_script("return window.performance.getEntries()")

    time.sleep(3)

    # Find the URL of the file that starts with "routelive"
    route_live_url = None
    for request in network_requests:
        if request["name"].startswith("https://chalo.com/app/api/scheduler_v4/v4/chennai/routedetailslive?route_id="):
            route_live_url = request["name"]
            break

    if route_live_url:
        print("URL of routelive file:", route_live_url)

        # Now you can download the file using the obtained URL
        # For example, using requests library:
        import requests

        response = requests.get(route_live_url)
        if response.status_code == 200:
            with open(f"routelive_{route_number.strip()}.json", "wb") as file:
                file.write(response.content)
            print("routelive file downloaded successfully.")

            # Read input data from the downloaded routelive JSON file
            with open(f"routelive_{route_number.strip()}.json", "r") as file:
                json_data = json.load(file)['route']

            # Convert to GeoJSON format
            geojson_data = convert_to_geojson(json_data)

            # Output the GeoJSON data to a file
            with open(f"route_{route_number.strip()}.geojson", "w") as output_file:
                json.dump(geojson_data, output_file)
            print("GeoJSON file created successfully.")

            os.remove(f"routelive_{route_number.strip()}.json")

        else:
            print("Failed to download routelive file. Status code:", response.status_code)
    else:
        print("routelive file not found in network requests.")
