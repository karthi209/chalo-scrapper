from selenium import webdriver
from bs4 import BeautifulSoup
import time
import json
from selenium.webdriver.common.by import By


# Start Chrome
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

time.sleep(3)

# Search using the Route Number
search_b = driver.find_element(By.CLASS_NAME, "searchInputs")
select_searchbar = search_b.find_element(By.TAG_NAME, "input")
select_searchbar.send_keys("1")

time.sleep(3)

first_result = driver.find_element(By.CLASS_NAME, "MuiList-root")
first_result.click()

time.sleep(8)