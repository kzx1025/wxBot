#!/usr/bin/env python
# coding: utf-8

from wxbot import *
import ConfigParser
import json
import recomend
import myredispool


class TulingWXBot(WXBot):
    def __init__(self):
        WXBot.__init__(self)

        self.tuling_key = ""
        self.robot_switch = True
        self.redis = myredispool.RedisCache()

        try:
            cf = ConfigParser.ConfigParser()
            cf.read('conf.ini')
            self.tuling_key = cf.get('main', 'key')
        except Exception:
            pass
        print 'tuling_key:', self.tuling_key

    def tuling_auto_reply(self, uid, msg):
        if self.tuling_key:
            url = "http://www.tuling123.com/openapi/api"
            user_id = uid.replace('@', '')[:30]
            body = {'key': self.tuling_key, 'info': msg.encode('utf8'), 'userid': user_id}
            r = requests.post(url, data=body)
            respond = json.loads(r.text)
            result = ''
            if respond['code'] == 100000:
                result = respond['text'].replace('<br>', '  ')
            elif respond['code'] == 200000:
                result = respond['url']
            elif respond['code'] == 302000:
                for k in respond['list']:
                    result = result + u"【" + k['source'] + u"】 " +\
                        k['article'] + "\t" + k['detailurl'] + "\n"
            else:
                result = respond['text'].replace('<br>', '  ')

            print '    ROBOT:', result
            return result
        else:
            return u"知道啦"

    def auto_switch(self, msg):
        msg_data = msg['content']['data']
        stop_cmd = [u'退下', u'走开', u'关闭', u'关掉', u'休息', u'滚开']
        start_cmd = [u'出来', u'启动', u'工作']
        if self.robot_switch:
            for i in stop_cmd:
                if i == msg_data:
                    self.robot_switch = False
                    self.send_msg_by_uid(u'[Robot]' + u'机器人已关闭！', msg['to_user_id'])
        else:
            for i in start_cmd:
                if i == msg_data:
                    self.robot_switch = True
                    self.send_msg_by_uid(u'[Robot]' + u'机器人已开启！', msg['to_user_id'])

    def recommend(self, userid, msg_data):
        movie_cmd = [u'推荐一部电影', u'来一部电影', u'推荐电影', u'换一部', u'来部电影', u'推荐部电影', u'求推荐电影', u'有什么好看的电影']
        smallmovie_cmd = [u'来个种子', u'我要看片', u'来个番号']
        for i in movie_cmd:
            if i == msg_data:
                try:
                    reply = recomend.recommend_movie()
                    self.send_msg_by_uid(reply, userid)
                except:
                    self.send_msg_by_uid(u'抱歉，我心情不太好。等下再给你推荐电影吧', userid)
                return True
        for i in smallmovie_cmd:
            if i == msg_data:
                try:
                    reply = recomend.recommend_smallmovie()
                    self.send_msg_by_uid(reply, userid)
                except:
                    self.send_msg_by_uid(u'怎么天天想着看片！', userid)
                return True
        return False

    def handle_msg_all(self, msg):

        if not self.robot_switch and msg['msg_type_id'] != 1:
            return
        if msg['msg_type_id'] == 1 and msg['content']['type'] == 0:  # reply to self
            self.auto_switch(msg)
        elif msg['msg_type_id'] == 4 and msg['content']['type'] == 0:  # text message from contact
            # 处理推荐系统逻辑
            if self.recommend(msg['user']['id'], msg['content']['data']):
                return
            # 处理聊天逻辑
            self.send_msg_by_uid(self.tuling_auto_reply(msg['user']['id'], msg['content']['data']), msg['user']['id'])
        elif msg['msg_type_id'] == 3 and (msg['content']['type'] == 0 or msg['content']['type'] == 10):  # group text message
            # 处理撤回逻辑
            if msg['content']['redraw'] == 1:
                msg_data = msg['content']['data']
                print msg_data
                old_msgid = re.compile('<msgid>(.*)</msgid>').findall(msg_data)[0]
                print 'old_msgid is ' + old_msgid
                redraw_msg = self.redis.get_data(old_msgid)
                print type(redraw_msg)

                print 'redraw_msg is ' + str(redraw_msg).replace("\\\\", "\\")
                #redraw_json = json.loads(str(redraw_msg).replace("\\\\", "\\").replace("\'", "\""))
                #print type(redraw_json)
                #print redraw_json['data']
                username =  re.compile(': (.*), \'userid\'').findall(redraw_msg)[0]
                print username
                data = re.compile('\'data\': (.*)}').findall(redraw_msg)[0]
                reply = u'刚才'+username.decode("unicode_escape").replace("\'","").replace("u","")+u'撤回得是：'+\
                        data.decode("unicode_escape").replace("\'","").replace("u","")
                self.send_msg_by_uid(reply, msg['user']['id'])

            # 处理文本消息
            if 'detail' in msg['content']:
                my_names = self.get_group_member_name(self.my_account['UserName'], msg['user']['id'])
                if my_names is None:
                    my_names = {}
                if 'NickName' in self.my_account and self.my_account['NickName']:
                    my_names['nickname2'] = self.my_account['NickName']
                if 'RemarkName' in self.my_account and self.my_account['RemarkName']:
                    my_names['remark_name2'] = self.my_account['RemarkName']

                # 将消息存入redis
                msg_id = msg['msg_id']
                message = {'data': msg['content']['desc'], 'userid': msg['user']['id'], 'username': msg['user']['name']}
                #msg_json = json.loads(message)
                success = self.redis.set_data(msg_id, message)
                if success:
                    print (msg_id, message)
                    print u"群消息存入redis成功"

                is_at_me = False
                random_value = random.randint(1, 100)

                for detail in msg['content']['detail']:
                    if detail['type'] == 'at':
                        for k in my_names:
                            if my_names[k] and my_names[k] == detail['value']:
                                is_at_me = True
                                break

                #处理机器人是否退出流程


                #判断机器人是否退出


                # 处理推荐系统逻辑
                if self.recommend(msg['user']['id'], msg['content']['desc']):
                    return

                if is_at_me:
                    src_name = msg['user']['name']
                    reply = '@' + src_name + ': '
                    if msg['content']['type'] == 0:  # text message
                        reply += self.tuling_auto_reply(msg['content']['user']['id'], msg['content']['desc'])
                        if random_value > 70:
                            reply += '!'
                    else:
                        reply += u"对不起，只认字，其他杂七杂八的我都不认识，,,Ծ‸Ծ,,"
                    self.send_msg_by_uid(reply, msg['user']['id'])

                print random_value

                index = random.randint(0, 5)
                random_say = [u'23333333', u'能别说话了么，烦',u'呵呵',u'哦？',u'能不能聊点别的', u'可以的']

                if is_at_me is False and random_value > 95:
                    src_name = msg['user']['name']
                    reply = ''
                    if msg['content']['type'] == 0:  # text message
                        reply += self.tuling_auto_reply(msg['content']['user']['id'], msg['content']['desc'])
                        if random_value > 98:
                            reply += '!'
                    else:
                        reply += u"我很想知道你说的什么"
                    time.sleep(3)
                    print u"主动发言:"+reply
                    self.send_msg_by_uid(reply, msg['user']['id'])

                if is_at_me is False and random_value <=95 and random_value >90:
                    src_name = msg['user']['name']
                    reply = ''
                    if msg['content']['type'] == 0:  # text message
                        reply += random_say[index]
                        if random_value > 93:
                            reply += '!'
                    else:
                        reply += u"我很想知道你说的什么"
                    time.sleep(3)
                    print u"主动发言:"+reply
                    self.send_msg_by_uid(reply, msg['user']['id'])


def main():
    bot = TulingWXBot()
    bot.DEBUG = True
    bot.conf['qr'] = 'tty'

    bot.run()


if __name__ == '__main__':
    main()

