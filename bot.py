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
        self.master_id = ''
        self.master_mode = 0

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
        elif msg['msg_type_id'] == 4 and (msg['content']['type'] == 0 or msg['content']['type'] == 6):  # text message from contact
            # 处理管理员公告
                # 进行密码登录
            print msg['user']['id']
            if msg['content']['data'] == 'open the console':
                self.master_id = msg['user']['id']
                self.master_mode = 1
                self.send_msg_by_uid(u"管理员模式开启", msg['user']['id'])
                return
            if msg['content']['data'] == 'close the console':
                self.master_id = ''
                self.master_mode = 0
                self.send_msg_by_uid(u"管理员模式关闭", msg['user']['id'])
                return
                # 判断是否为管理员
            if msg['user']['id'] == self.master_id and msg['content']['data'] != 'open the console':
                for group in self.group_members:
                    print group
                    self.send_msg_by_uid(msg['content']['data'], group)
                self.send_msg_by_uid(u"公告发送成功", msg['user']['id'])
                return
            if self.master_mode == 1:
                return

            if msg['content']['type'] == 6:
                self.send_random_emoji(msg['user']['id'])
                return

            # 处理推荐系统逻辑
            if self.recommend(msg['user']['id'], msg['content']['data']):
                return
            # 处理聊天逻辑
            self.send_msg_by_uid(self.tuling_auto_reply(msg['user']['id'], msg['content']['data']), msg['user']['id'])

        elif msg['msg_type_id'] == 3 and (msg['content']['type'] == 0 or msg['content']['type'] == 10
                                          or msg['content']['type'] ==3 or msg['content']['type']  == 6
                                          or msg['content']['type'] == 4 or msg['content']['type'] == 12):  # group text message
            if self.master_mode == 1:
                #if msg['content']['data'] == 'test':
                   # print 'send picture!'
                   # self.send_image('data/image/img_476620686838734673.jpg', msg['user']['id'])
                    #self.send_file('data/voice/voice_6364321762328836396.mp3', msg['user']['id'])
                return

            # 处理撤回逻辑
            print 'group message'
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
                redraw_type = re.compile('\'type\': (.*)}').findall(redraw_msg)[0]
                print redraw_type
                data = re.compile('\'data\': (.*), \'type\'').findall(redraw_msg)[0]
                if int(redraw_type) == 3:
                    print data.replace('u', '').replace('\'', '')
                    self.send_image(data.replace('u', '').replace('\'', ''), msg['user']['id'])
                    reply = u'刚才'+username.decode("unicode_escape").replace("\'","").replace("u","")+u'撤回得是'+\
                        u'这张图片'
                    self.send_msg_by_uid(reply, msg['user']['id'])
                elif int(redraw_type) == 4:
                    self.send_file(data.replace('u', '').replace('\'', ''), msg['user']['id'])
                    reply = u'刚才'+username.decode("unicode_escape").replace("\'","").replace("u","")+u'撤回得是'+\
                        u'这段语音'
                    self.send_msg_by_uid(reply, msg['user']['id'])
                else:
                    reply = u'刚才'+username.decode("unicode_escape").replace("\'","").replace("u","")+u'撤回得是：'+\
                        data.decode("unicode_escape").replace("\'","").replace("u","")
                    self.send_msg_by_uid(reply, msg['user']['id'])

            # 将消息存入redis
            msg_id = msg['msg_id']
            print msg_id
            redis_data = ''
            if msg['content']['type'] == 0:
                redis_data = msg['content']['desc']
            elif msg['content']['type'] == 3:
                redis_data = msg['content']['image_url']
            elif msg['content']['type'] == 4:
                redis_data = msg['content']['voice_url']
            else:
                redis_data = u'一种未知事物'
            message = {'data': redis_data, 'userid': msg['user']['id'], 'username': msg['user']['name'], 'type': msg['content']['type']}
            success = self.redis.set_data(msg_id, message)
            if success:
                print (msg_id, message)
                print u"群消息存入redis成功"

            # 处理表情消息
            if msg['content']['type'] == 6:
                self.send_random_emoji(msg['user']['id'])
                return

            # 处理新拉入群操作
            if msg['content']['is_entergroup'] == 1:
                reply = u'各位好，我是长者。'
                reply += u'我的功能有：1.艾特我，我会和你对话； 2.在群聊中进行随机说话； 3.可以咨询天气或者部分词条，回复推荐电影，推荐豆瓣电影，回复我要看片，推荐老司机电影；' \
                         u'4.支持群聊天消息撤回的重发，包括文字，图片，语音，暂不支持表情；5.回复艾特全员，自动帮你艾特全部群成员；6.当有红包消息时，自动艾特所有群成员进行提醒'
                self.send_msg_by_uid(reply, msg['user']['id'])
                return


            # 处理红包
            if msg['content']['is_hongbao'] == 1:
                reply = u'有人发红包啦！！ '
                for member_name in self.get_all_group_member_name(msg['user']['id']):
                    reply+='@'+member_name+' '
                self.send_msg_by_uid(reply, msg['user']['id'])
                return

            if 'test' in msg['content']['desc']:
                #self.send_msg_by_uid('<span class=\"emoji emoji1f61e\">', msg['user']['id'])
                #self.send_msg_by_uid('\"emoji emoji1f61e\"', msg['user']['id'])
                self.send_msg_by_uid('<img class=\"emoji emoji1f625\"  src=\"https://wx.qq.com/zh_CN/htmledition/v2/images/spacer.gif\">', msg['user']['id'])
                return
            # 处理艾特全员逻辑
            if u'艾特' in msg['content']['desc'] and u'全员' in msg['content']['desc']:
                reply = ''
                for member_name in self.get_all_group_member_name(msg['user']['id']):
                    reply+='@'+member_name+' '
                self.send_msg_by_uid(reply,msg['user']['id'])
                return


            # 处理文本消息
            if 'detail' in msg['content']:
                #my_names = self.get_group_member_name(self.my_account['UserName'], msg['user']['id'])
                my_names = self.get_group_member_name(msg['user']['id'], msg['to_user_id'])
                if my_names is None:
                    my_names = {}
                if 'NickName' in self.my_account and self.my_account['NickName']:
                    my_names['nickname2'] = self.my_account['NickName']
                if 'RemarkName' in self.my_account and self.my_account['RemarkName']:
                    my_names['remark_name2'] = self.my_account['RemarkName']



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
                random_say = [u'23333333', u'啧啧',u'呵呵',u'哦？',u'嘎嘎', u'可以的']

                if is_at_me is False and (random_value == 95 or random_value == 96):
                    self.send_random_emoji(msg['user']['id'])
                if is_at_me is False and random_value ==99:
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

                if is_at_me is False and random_value ==98:
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

