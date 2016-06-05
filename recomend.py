#!/usr/bin/env python
# coding: utf-8

__author__ = 'iceke'
from requests.exceptions import ConnectionError, ReadTimeout
import urllib2
import requests
import json
import random
from bs4 import BeautifulSoup

UNKONWN = 'unkonwn'
SUCCESS = '200'
SCANED = '201'
TIMEOUT = '408'


def to_unicode(string, encoding='utf-8'):
    if isinstance(string, str):
        return string.decode(encoding)
    elif isinstance(string, unicode):
        return string
    else:
        raise Exception('Unknown Type')


def recommend_movie():
    way = random.randint(0, 5)
    message = ''
    if way <= 5:
        start = random.randint(1, 150)
        index = random.randint(1, 100)
        url = "https://api.douban.com/v2/movie/top250?start=" + str(start) + "&count=100"
        r = requests.get(url)
        data = json.loads(r.text)
        movie = data['subjects'][index]
        message += u"电影名称:" + movie['title'] + ',' + u"电影拍摄于" + movie['year'] + ',' + u"电影评分为:" + \
                   str(movie['rating']['average']) + u"。由" + movie['casts'][0]['name'] + ',' + movie['casts'][1][
                       'name'] + \
                   u"等演员主演。" + u"豆瓣链接:" + movie['alt'] + u"。 若不喜欢，可以回复换一部"
        return message


def recommend_book(info):
    message = ''
    url = "https://api.douban.com/v2/book/search?q="+info
    r = requests.get(url)
    data = json.loads(r.text)
    #TODO


def recommend_smallmovie():
    url = "https://btso.pw/search/"
    r = requests.get(url,timeout=8)
    soup = BeautifulSoup(r.text, "html.parser")
    a_all = soup.find_all('a',class_='tag')
    fanhaos = []
    for a in a_all:
        fanhaos.append(a.get_text().split('.')[1])
        #print a
    index = random.randint(1, len(fanhaos))
    fanhao = fanhaos[index]
    print fanhao
    link = 'https://btso.pw/search/'+fanhao
    #print link
    r2 = requests.get(link,timeout=8)
    soup2 = BeautifulSoup(r2.text, "html.parser")

    magnet = []
    for a2 in soup2.find_all('a'):
        if 'hash' in a2.get('href'):
            magnet.append(a2.get('href'))
    if len(magnet) == 0:
        raise ValueError('magnet length is 0!')
    r3 = requests.get(magnet[0],timeout=8)
    soup3 = BeautifulSoup(r3.text, "html.parser")
    final_magnet = soup3.find('textarea').get_text().replace(';', '')
    message = u"不谢!番号是"+fanhao+u"。种子链接："+final_magnet
    print  message
    return message


