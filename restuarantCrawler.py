import time
import re

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

options = Options()
# options.add_argument("--headless") # Runs Chrome in headless mode.
options.add_argument('--no-sandbox') # Bypass OS security model
options.add_argument('--disable-gpu')  # applicable to windows os only
options.add_argument('start-maximized') # start maximized
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'    
options.add_argument('user-agent={0}'.format(user_agent))

# Init WebDriver
driver = webdriver.Chrome('chromedriver.exe', options=options)

# Global URLs
BASE_URL = 'https://www.zomato.com/'
LOCATION = 'mumbai'

# Generate List URL
restuarantListUrl = BASE_URL + LOCATION + '/restaurants?page='

# Get the number of pages in the list
driver.get(restuarantListUrl)
driver.save_screenshot("screenshot.png")
# driver.execute_script("return navigator.userAgent")
# WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="search-results-container"]/div[2]/div[1]/div[1]/div/b[2]')))
pageCount = int(driver.find_element_by_xpath('//*[@id="search-results-container"]/div[2]/div[1]/div[1]/div/b[2]').text)

print('No of Pages: ', pageCount)

# Create DataFrame
cols = ['restaurantID', 'restaurantName', 'restaurantURL', 'restaurantType', 'restaurantRating', 'restaurantVoteCount', 'restaurantLocation', 'restaurantImageURL', 'restaurantCuisines', 'restaurantCostForTwo', 'restaurantHours']
df = pd.read_csv('restaurants.csv', index_col=0)

# Iterate through pages
for page in range(611, pageCount):
    print('Processing page no: ', page+1)

    restuarantPageUrl = restuarantListUrl + str(page+1)
    driver.get(restuarantPageUrl)

    # WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, '//*[@id="cat-banner-ads"]/div[2]/div[2]/div[1]')))

    # Scape the data
    restaurantCards = driver.find_elements_by_xpath('//*[@id="orig-search-list"]/div')
    
    for restaurant in restaurantCards:
        ele = restaurant
        
        # Store details
        restaurantID = ele.find_element_by_class_name('js-search-result-li').get_attribute('data-res_id')
        restaurantName = ele.find_element_by_class_name('result-title').text
        restaurantURL = ele.find_element_by_class_name('result-title').get_attribute('href')
        try:
            restaurantType = ele.find_element_by_class_name('res-snippet-small-establishment').text
        except:
            restaurantType = ''
        try:
            restaurantRating = ele.find_element_by_class_name('rating-popup').text
        except:
            restaurantRating = ''
        try:
            restaurantVoteCount = ele.find_element_by_class_name('search_result_rating').find_element_by_xpath('span').text
        except:
            restaurantVoteCount = ''
        try:
            restaurantLocation = ele.find_element_by_class_name('search_result_subzone').text
        except:
            restaurantLocation = ''
        restaurantImageURL = ele.find_element_by_class_name('feat-img').value_of_css_property('background-image')
        restaurantImageURL = re.findall('\"(.*?)\"',restaurantImageURL)[0]
        try:
            restaurantCuisines = ele.find_element_by_xpath('div[1]/div/article/div[3]/div[1]/span[2]').text
        except:
            restaurantCuisines = ''
        try:
            restaurantCostForTwo = ele.find_element_by_xpath('div[1]/div/article/div[3]/div[2]/span[2]').text
        except:
            restaurantCostForTwo = ''
        try:
            restaurantHours = ele.find_element_by_xpath('div[1]/div/article/div[3]/div[3]/div[1]').text
        except:
            restaurantHours = ''

        row = [restaurantID, restaurantName, restaurantURL, restaurantType, restaurantRating, restaurantVoteCount, restaurantLocation, restaurantImageURL, restaurantCuisines, restaurantCostForTwo, restaurantHours]
        temp_df = pd.DataFrame([row], columns=cols)
        df = df.append(temp_df, ignore_index=True)

    if page%10==0:
        df.to_csv('restaurants.csv')

df.to_csv('restaurants.csv')

time.sleep(3)

driver.quit()