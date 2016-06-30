#!/usr/bin/env python
# coding: utf-8

__author__ = 'iceke'

import re
import os
import json
import wxbot

emoji_map = {}
fp = open("data/emoji.txt", 'r')
for line in fp.readlines():
    a = line.split(' ')
    if len(a) == 2:
        key = a[0][3:].lower()
        value = a[1][:-1].lower()
        emoji_map[key] = value

print 'emoji_map produce finished!'


def emoji_dealer(name):
    regex = re.compile('^(.*?)(?:<span class="emoji (.*?)"></span>(.*?))+$')
    match = re.findall(regex, name)
    #print match
    # print match[0]
    if len(match) > 0:
        #print match
        #flag = re.search('emoji([\da-z]{5})', match[0][0]+match[0][1]+match[0][2]).groups()[0]
        #print match[0][2]
        #return  ('\\U000%s'%flag).decode('unicode-escape').encode('utf8')
        #emoji_key = match[0][1][5:].replace('\'','').replace('u','')
        #print emoji_key
        #emoji_value = 'u\'\\u'+emoji_map[emoji_key]+'\''
        try:
            flag = re.search('emoji([\da-z]{5})', match[0][0]+match[0][1]+match[0][2]).groups()
        except:
            return name[0:3]
        #print flag
        name = match[0][0]+('\\U000%s'%flag).decode('unicode-escape')+match[0][2]
    return name


def check_file(fileDir):
    try:
        with open(fileDir):
            pass
        return True
    except:
        return False


def to_unicode(string, encoding='utf-8'):
        """
        将字符串转换为Unicode
        :param string: 待转换字符串
        :param encoding: 字符串解码方式
        :return: 转换后的Unicode字符串
        """
        if isinstance(string, str):
            return string.decode(encoding)
        elif isinstance(string, unicode):
            return string
        else:
            raise Exception('Unknown Type')

#print emoji_dealer("Ivory<span class=\"emoji emoji1f338\"></span>adsa")
#a= emoji_dealer("dads<span class=\"emoji emoji1f338\"></span>dad<span class=\"emoji emoji200\"></span>5sds")

#a = ('2005',)
#print '@'+"member"+('\\u2005').decode('unicode-escape')

