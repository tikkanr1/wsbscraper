import requests
from selenium import webdriver
from datetime import timedelta
import datetime
from dateutil.parser import parse
import csv
import numpy as np
from collections import Counter


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

def get_link(driver):
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
    stock_link = link.split('/')[-3]
    driver.close()
    return stock_link

def get_raw_comment_list(stock_link):
    html = requests.get(f'https://api.pushshift.io/reddit/submission/comment_ids/{stock_link}')
    raw_comment_list = html.json()
    return raw_comment_list

def get_comment_list(raw_comment_list):
    orig_list = np.array(raw_comment_list['data'])
    comment_list = ",".join(orig_list[0:1000])
    return comment_list

def get_comments(comment_list):
    html = requests.get(f'https://api.pushshift.io/reddit/comment/search?ids{comment_list}&fields=body&size=1000')
    new_comments = html.json()
    return new_comments

def get_stock_list(new_comments, tickers):
    stock_dict = Counter()
    for a in new_comments['data']:
        for ticker in tickers:
            if ticker in a['body']:
                stock_dict[ticker] += 1
    return stock_dict

def count(stock_dict, raw_comment_list):
    orig_list = np.array(raw_comment_list['data'])
    remove_me = slice(0, 1000)
    cleaned = np.delete(orig_list, remove_me)
    tickers = get_tickers()
    i = 0
    while i < len(cleaned):
        print(len(cleaned))
        cleaned = np.delete(cleaned, remove_me)
        new_comments_list = ",".join(cleaned[0:1000])
        new_comments = get_comments(new_comments_list)
        get_stock_list(new_comments, tickers)
    stock = dict(stock_dict)
    return stock

def write(stock):
    data = list(zip(sorted(stock.keys()), sorted(stock.values())))
    with open('stock.csv', 'w') as w:
        writer = csv.writer(w, lineterminator='\n')
        writer.writerow(['Stock', 'Number of Mentions'])
        for a in data:
            writer.writerow(a)

if __name__ == "__main__":
    driver = get_driver()
    stock_link = get_link(driver)
    raw_comment_list = get_raw_comment_list(stock_link)
    tickers = get_tickers()
    comment_list = get_comment_list(raw_comment_list)
    new_comments = get_comments(comment_list)
    stock_dict = get_stock_list(new_comments, tickers)
    stock = count(stock_dict, raw_comment_list)
    write(stock)

