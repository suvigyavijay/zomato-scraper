from bs4 import BeautifulSoup
import requests

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

    return response.json()['html']

import pandas as pd

df = pd.read_csv('restaurants.csv', index_col=0)
print(df.info())

cols = 'userID, userName, userRating, restuarantID, restuarantName'

f = open("soup3k.csv", "wb")
f.write(cols.encode("utf-8"))
f.write('\n'.encode("utf-8"))


def process(index):
    print('Currently processing restuarant number ', index+1)
    
    try:
        response = get_review(df.loc[index, 'restaurantID'], df.loc[index, 'restaurantVoteCount'].split(' ')[0])
    except:
        response = ''


    soup = BeautifulSoup(response, 'html.parser')

    users = soup.find_all('div', class_='res-review-body')
    print('No of users for '+str(index+1)+': '+str(len(users)))

    if len(users)==0:
        print('Done ', (index+1))
        return

    for user in users:

        userID = user.find('div', class_='header').a['data-entity_id']
        userName = user.find('div', class_='header').a.text.strip()
        userRating = user.find('div', class_='ttupper')['aria-label'].split(' ')[1]

        restaurantName = df.loc[index, 'restaurantName']
        restaurantID = df.loc[index, 'restaurantID']

        arow = [userID, userName, userRating, restaurantID, restaurantName]
        lock.acquire()
        f.write((','.join(map(str, arow))).encode("utf-8"))
        f.write('\n'.encode("utf-8"))
        lock.release()

    print('Done ', (index+1))

import numpy as np
nrange = np.arange(len(df))

import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool

def init(l):
    global lock
    lock = l


# function to be mapped over
def calculateParallel(numbers, threads=2):
    l = multiprocessing.Lock()
    pool = ThreadPool(threads, initializer=init, initargs=(l,))
    pool.map(process, numbers)
    pool.close()
    pool.join()
    

calculateParallel(nrange, 32)

f.close()