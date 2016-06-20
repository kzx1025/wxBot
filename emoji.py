# coding=utf-8
__author__ = 'iceke'

import urllib2
from HTMLParser import HTMLParser


class MyHtmlParser(HTMLParser):
    # class attribute defined here
    def __init__(self):  # python class的构造方法
        HTMLParser.__init__(self)  # 必须调用基类的constructor
        # 实例属性
        self.record = False
        self.emojiUnicodes = dict()
        self.emojiSB = dict()
        self.uniSBMap = dict()
        self.isUni = False
        self.isSB = False
        self.numUni = 0
        self.numSB = 0

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            print attrs  # attrs 是 list
            for attr in attrs:  # attr 是 tuple
                print attr
                (name, value) = attr
                print name
                print value
        if tag != "td":
            self.record = False
            self.isUni = False
            self.isSB = False

    def handle_data(self, data):
        if data == "Unicode" or data == "SB Unicode":
            self.record = True
            if data == "Unicode":
                self.isUni = True
            if data == "SB Unicode":
                self.isSB = True
            return
        if self.record:  # bool 类型
            if data.find("\n") != -1:  # 忽略掉不知道哪里来的换行符
                return
            if self.isUni:
                dataList = data.split(" ")
                self.numUni += 1
                for code in dataList:
                    code = code[2:]
                    code = "000" + code
                    self.emojiUnicodes[self.numUni] = code
                    return
            if self.isSB:
                self.numSB += 1
                self.emojiSB[self.numSB] = data
                return

                # 生成网页上(key, value)为(Unicode, SBCode)的dict

    def processMap(self):
        for i in range(1, self.numUni + 1):  # 注意这里range()的用法, range(start, end), 只会遍历到最大的比end小的数,不会等于end
            self.uniSBMap[self.emojiUnicodes[i]] = self.emojiSB[i]


def processEmoji(url):
    print "destination url: ", url
    # 把目标网页的html先扒到本地
    htmlfile = urllib2.urlopen(url)
    data = htmlfile.read()

    # 用自己定义的htmlParser处理htmlfile
    parser = MyHtmlParser()
    parser.feed(data)
    parser.processMap()
    print parser.emojiUnicodes, "\nnumUni=", parser.numUni, "\n", parser.emojiSB, "\nnumSB=", parser.numSB, "\n ", parser.uniSBMap

    # 单独把emoji.txt中不存在的条目 写成一个map
    newMap = dict()
    for key in parser.emojiUnicodes:
        value = parser.emojiUnicodes[key]
        if value not in emojiMap:  # 这里访问的emojiMap是下面定义的全局的
            print (value, parser.uniSBMap[value])  # 可以这样来print出一个tuple
            newMap[value] = parser.uniSBMap[value]
    return newMap  # 返回生成的dict


# 把emoji.txt中内容读到 emojiMap中
fp = open("data/emoji.txt", 'a+')  # 追加和读模式打开./emoji.txt时，不存在就会自动创建
emojiMap = dict()
for line in fp:
    if line == "\n":  # 跳过空行
        continue
    line.strip()
    (name, value) = line.split()  # string的split()默认以" "作为分隔符
    emojiMap[name] = value
fp.close()

# 所有的要去抓取的urls，还是写死了
baseUrl = "http://punchdrunker.github.com/iOSEmoji/table_html/"
urlList = ["index.html", "flower.html", "bell.html", "vehicle.html", "number.html"]
codeDict = dict()  # 用来保存每个网页新的条目的总和
for url in urlList:
    url = baseUrl + url
    newMap = processEmoji(url)
    codeDict.update(newMap)  # dict的合并

# 把codeDict写到emoji.txt中
print codeDict
fp = open("data/emoji.txt", 'w')  # 以追加模式打开emoji.txt
fp.write("\n")
for key in codeDict:  # dict的遍历要像这样
    line = key + " " + codeDict[key] + "\n"
    fp.write(line)
fp.close()
