import requests
from selenium import webdriver
from datetime import timedelta
import datetime
from dateutil.parser import parse
import csv
import numpy as np


def get_tickers():
    tickers = []
    with open('tickers.csv', newline='') as f:
        for row in csv.reader(f):
            tickers.append(row[0])
    return tickers

def get_driver():
    url = 'https://www.reddit.com/r/wallstreetbets/search/?q=flair%3A%22Daily%20Discussion%22&restrict_sr=1&sort=new'
    driver = webdriver.Chrome('/usr/bin/chromedriver')
    driver.get(url)
    return driver

def get_link():
    yesterday = datetime.date.today() - timedelta(days=1)
    driver = get_driver()
    links = driver.find_elements_by_xpath('//*[@class="_eYtD2XCVieq6emjKBH3m"]')

    for a in links:
        if a.text.startswith('Daily Discussion Thread'):
            date = "".join(a.text.split(' ')[-3:])
            parsed = parse(date)
            if parse(str(yesterday)) == parsed:
                link = a.find_element_by_xpath('../..').get_attribute('href')

        if a.text.startswith('Weekend'):
            weekend_date = a.text.split(' ')
            parsed_date = weekend_date[-3] + ' ' + weekend_date[-2].split('-')[1] + weekend_date[-1]
            parsed = parse(parsed_date)
            saturday = weekend_date[-3] + ' ' + str(int(weekend_date[-2].split('-')[1]
                .replace(',', '')) - 1) + ' ' + weekend_date[-1]

            if parse(str(yesterday)) == parsed:
                link = a.find_element_by_xpath('../..').get_attribute('href')

            elif parse(str(yesterday)) == parse(str(saturday)):
                link = a.find_element_by_xpath('../..').get_attribute('href')
    driver.close()
    return link

def get_raw_comment_list():
    link = get_link()
    stock_link = link.split('/')[-3]
    html = requests.get(f'https://api.pushshift.io/reddit/submission/comment_ids/{stock_link}')
    raw_comment_list = html.json()
    return raw_comment_list

def get_comments():
    raw_comment_list = get_raw_comment_list()
    orig_list = np.array(raw_comment_list['data'])
    comment_list = ",".join(orig_list[0:1000])
    html = requests.get(f'https://api.pushshift.io/reddit/comment/search?ids{comment_list}&fields=body&size=1000')
    newcomments = html.json()
    return newcomments

print(get_comments())
