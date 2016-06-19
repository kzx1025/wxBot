#!/usr/bin/env python
# coding: utf-8

__author__ = 'iceke'


import re
import os

def emoji_dealer(name):
    return name
    regex = re.compile('^(.*?)(?:<span class="emoji (.*?)"></span>(.*?))+$')
    match = re.findall(regex, name)
    #print match[0]
    if len(match) > 0: name = ''.join(match[0])
    return name
def check_file(fileDir):
    try:
        with open(fileDir): pass
        return True
    except:
        return False

#print os.listdir("data/emoji/")
#rint emoji_dealer("Ivory<span class=\"emoji emoji1f338\"></span>")
#<img class="emoji emoji1f625"  src="https://wx.qq.com/zh_CN/htmledition/v2/images/spacer.gif">
