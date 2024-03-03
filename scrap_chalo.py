from selenium import webdriver
import time
import json
from selenium.webdriver.common.by import By
import requests
import os
import polyline
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# function to convert json used by chalo to standard geojson format
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

    encoded_polyline = data["polyline"]

    # decode the polyline
    decoded_polyline = polyline.decode(encoded_polyline)

    # swap latitude and longitude pairs
    swapped_decoded_polyline = [(lon, lat) for lat, lon in decoded_polyline]

    # convert swapped decoded polyline to GeoJSON format
    geojson = {
        "type": "Feature",
        "properties": {
            "name": route_number
        },
        "geometry": {
            "type": "LineString",
            "coordinates": swapped_decoded_polyline
        }
    }

    features.append(geojson)

    feature_collection = {
        "type": "FeatureCollection",
        "features": features
    }

    return feature_collection

# route_numbers.txt should have all the route number - each route should be in separate line
# place the route_numbers.txt file in the same folder as this python script

# ------------------ Begin Script ------------------

# open the route_numbers.txt file and read it's content
with open("route_numbers.txt", "r") as file:
    route_numbers = file.readlines()

# iterate through the routes
for route_number in route_numbers:

    print(f"Start: Route {route_number}", end="")

    # start the chrome driver
    driver = webdriver.Chrome()

    # opens chalo website - please note the URL - this script is designed to navigate from "https://chalo.com/app/live-tracking" - might change in future
    driver.get("https://chalo.com/app/live-tracking")

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(), 'Chennai')]")))

    # selecting Chennai as the focus city (make sure to select your focus city)
    select_chn = driver.find_element(By.XPATH, "//div[contains(text(), 'Chennai')]")
    select_chn.click()

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//button[contains(text(), 'Get Started')]")))

    # Click the Get Started button (just some navigation stuff) - again will have to be modified if chalo decides to change it's UI or navigation schema
    select_get_started = driver.find_element(By.XPATH, "//button[contains(text(), 'Get Started')]")
    select_get_started.click()

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "MuiList-root")))

    # this section finds the search bar and types the route number
    search_b = driver.find_element(By.CLASS_NAME, "searchInputs")
    select_searchbar = search_b.find_element(By.TAG_NAME, "input")
    select_searchbar.clear()  # Clear search bar
    select_searchbar.send_keys(route_number.strip())  # Strip to remove leading/trailing whitespaces
    
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "searchInputs")))

    # this section looks at the first result of the search
    # it then gets the route name that's in the first result
    first_result = driver.find_element(By.CLASS_NAME, "MuiList-root")
    check_route = first_result.find_element(By.CLASS_NAME, "route-name")
    route_in_chalo = check_route.text

    # this section checks if the route number from our list matches with the first result
    # if it matches, then the script executes to the next step
    # if it doesn't match, then it logs the failed route into "failed_routes.txt" file and exits

    if route_in_chalo.strip() == route_number.strip() or route_in_chalo.strip() == route_number.strip() + "  Deluxe":

        first_result.click()

        time.sleep(5)

        network_requests = driver.execute_script("return window.performance.getEntries()")

        time.sleep(3)

        # Find the request URL that matches "https://chalo.com/app/api/scheduler_v4/v4/chennai/routedetailslive?route_id=" "
        route_live_url = None

        for request in network_requests:
            if request["name"].startswith("https://chalo.com/app/api/scheduler_v4/v4/chennai/routedetailslive?route_id="):
                route_live_url = request["name"]
                break

        if route_live_url:

            import requests

            response = requests.get(route_live_url)

            if response.status_code == 200:
                with open(f"routelive_{route_number.strip()}.json", "wb") as file:
                    file.write(response.content)

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

                print (f"Success! Route: {route_number}", end="")

            else:
                print("Failed to download routelive file. Status code:", response.status_code)
        else:
            print("routelive file not found in network requests.")
    else:

        # For failed routes please check "failed_routes.txt" file
        print (f"Failure! Route: {route_number}", end="")

        file_path = "failed_routes.txt"

        # Check if the file exists
        if os.path.exists(file_path):
            # Open the file in append mode and add content
            with open(file_path, "a") as file:
                file.write(route_number.strip() + "\n")
        else:
            # Open the file in write mode and create it
            with open(file_path, "w") as file:
                file.write(route_number.strip() + "\n")

    print(f"End: Route {route_number}", end="")



    
