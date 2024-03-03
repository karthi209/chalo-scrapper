from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import requests
import os
import polyline
import time

# most variables listed here
source_location = "route_numbers.txt"
output_location = "failed_routes.txt"
website_url = "https://chalo.com/app/live-tracking"
chalo_json_geturl = "https://chalo.com/app/api/scheduler_v4/v4/chennai/routedetailslive?route_id="


# function to convert json used by chalo to standard geojson format
def convert_to_geojson(data, route_number):
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

# open the route_numbers.txt file and read its content
with open(source_location, "r") as file:
    route_numbers = file.readlines()

# iterate through the routes
for route_number in route_numbers:
    route_number = route_number.strip()  # remove leading/trailing whitespaces

    # start the chrome driver
    driver = webdriver.Chrome()

    # opens chalo website
    driver.get(website_url)

    # wait for Chennai to be visible
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(), 'Chennai')]")))

    # selecting Chennai as the focus city
    select_chn = driver.find_element(By.XPATH, "//div[contains(text(), 'Chennai')]")
    select_chn.click()

    # wait for Get Started button to be visible
    select_get_started = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//button[contains(text(), 'Get Started')]")))
    select_get_started.click()

    # wait for search inputs to be visible
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "searchInputs")))

    # this section finds the search bar and types the route number
    search_b = driver.find_element(By.CLASS_NAME, "searchInputs")
    select_searchbar = search_b.find_element(By.TAG_NAME, "input")
    select_searchbar.clear()  # Clear search bar
    select_searchbar.send_keys(route_number)  # Enter route number

    # wait for the list to be visible
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "MuiList-root")))

    # this section looks at the first result of the search

    # it then gets the route name that's in the first result
    # so, it was tricky here, there's two types of structures for normal and express trains
    # most routes covered by just getting elements from class "MuiList-root" and "route-name"
    first_result = driver.find_element(By.CLASS_NAME, "MuiList-root")
    check_route = first_result.find_element(By.CLASS_NAME, "route-name")
    route_in_chalo = check_route.text.strip()

    # few needs to use class "mark-text" to get the text
    check_route_express = first_result.find_element(By.CLASS_NAME, "mark-text")
    route_in_chalo_express = check_route_express.text.strip()

    # Check if the route number matches the first result or first result + " Deluxe" or the output from "mark-text" class
    if route_in_chalo == route_number or route_in_chalo == route_number + "  Deluxe" or route_in_chalo_express == route_number:
        first_result.click()

        time.sleep(3)

        # Wait for network requests to be available
        network_requests_script = "return window.performance.getEntries()"
        network_requests = WebDriverWait(driver, 10).until(lambda driver: driver.execute_script(network_requests_script))

        route_live_url = None

        # Find the request URL that matches "https://chalo.com/app/api/scheduler_v4/v4/chennai/routedetailslive?route_id="
        for request in network_requests:

            if request["name"].startswith(chalo_json_geturl):
                route_live_url = request["name"]
                break

        if route_live_url:

            response = requests.get(route_live_url)

            if response.status_code == 200:

                with open(f"routelive_{route_number}.json", "wb") as file:
                    file.write(response.content)

                # Read input data from the downloaded routelive JSON file
                with open(f"routelive_{route_number}.json", "r") as file:
                    json_data = json.load(file)['route']

                # Convert to GeoJSON format
                geojson_data = convert_to_geojson(json_data, route_number)

                # Output the GeoJSON data to a file
                with open(f"route_{route_number}.geojson", "w") as output_file:
                    json.dump(geojson_data, output_file)

                os.remove(f"routelive_{route_number}.json")

                print(f"Success! Route: {route_number}")

            else:

                print("Failed to download routelive file. Status code:", response.status_code)
        else:

            print("routelive file not found in network requests.")
    else:
        # For failed routes please check "failed_routes.txt" file
        print(f"Failure! Route: {route_number}")
        with open(output_location, "a") as file:
            file.write(route_number + "\n")

    driver.quit()  # close the browser after each iteration
