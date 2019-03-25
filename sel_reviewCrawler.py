import time
import re
import requests

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless") # Runs Chrome in headless mode.
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
restuarantListUrl = BASE_URL + LOCATION + '/restaurants'

# Get the number of pages in the list
driver.get(restuarantListUrl)

def get_review(res_id, count):

    cookies = {
        # copy cookie from firefox
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.zomato.com/',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        'TE': 'Trailers',
    }

    data = {
      'entity_id': res_id,
      'profile_action': 'reviews-dd',
      'page': '0',
      'limit': count
    }

    response = requests.post('https://www.zomato.com/php/social_load_more.php', headers=headers, cookies=cookies, data=data)

    return response.json()

df = pd.read_csv('restaurants.csv', index_col=0)
print(df.info())

cols = ['userID', 'userName', 'userURL', 'rating', 'review', 'restuarantID', 'restuarantName']
# main = pd.DataFrame(columns=cols)
main = pd.read_csv('reviews.csv', index_col=0)

response = {}

for index in range(5,len(df)):

    print('Currently processing restuarant number ', index+1)
    try:
        response = get_review(df.loc[index, 'restaurantID'], df.loc[index, 'restaurantVoteCount'].split(' ')[0])
    except:
        response = {}
        continue
    try:
        javascript = str("document.write('" + response['html'].replace('\n', ' ').replace("'", '"') + "')")
        driver.execute_script(javascript)
    except:
        javascript = "document.body.innerHTML = ''"
        driver.execute_script(javascript)

    
    users = driver.find_elements_by_xpath('/html/body/div')
    
    print('No of Users: ', len(users))

    for user in users:
        try:
            userID = user.find_element_by_class_name('header').get_attribute('data-entity_id')
        except:
            userID = ''
        try:
            userURL = user.find_element_by_class_name('header').find_element_by_tag_name('a').get_attribute('href')
        except:
            userURL = ''
        try:
            userName = user.find_element_by_class_name('header').text
        except:
            userName = ''
        try:
            rating = user.find_element_by_class_name('ttupper').get_attribute('aria-label').split(' ')[1]
        except:
            rating = ''
        try:
            review = user.find_element_by_class_name('rev-text').text
        except:
            review = ''
        restuarantName = df.loc[index, 'restaurantName']
        restuarantID = df.loc[index, 'restaurantID']
        
        arow = [userID, userName, userURL, rating, review, restuarantID, restuarantName]
        temp_df = pd.DataFrame([arow], columns=cols)
        main = main.append(temp_df, ignore_index=True)
    
    javascript = "document.body.innerHTML = ''"
    driver.execute_script(javascript)

    main.to_csv('reviews.csv')
    print('Done!')

main.to_csv('reviews.csv')

time.sleep(3)

driver.quit()