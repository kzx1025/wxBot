__author__ = 'iceke'


import re

def emoji_dealer(l):
    regex = re.compile('^(.*?)(?:<span class="emoji (.*?)"></span>(.*?))+$')
    for m in l: # because m is dict so can be used like this
        match = re.findall(regex, m['NickName'])
        if len(match) > 0: m['NickName'] = ''.join(match[0])
    return l
def check_file(fileDir):
    try:
        with open(fileDir): pass
        return True
    except:
        return False

#print u'\u5f20\u96c4'