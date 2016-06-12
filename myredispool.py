#!/usr/bin/env python
# coding: utf-8

__author__ = 'iceke'

import redis
import json
import re

class RedisDBConfig:
    HOST = '127.0.0.1'
    PORT = 6379
    DBID = 0
    EXPIRE = 1800


def operator_status(func):
    '''get operatoration status
    '''
    def gen_status(*args, **kwargs):
        error, result = None, None
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            error = str(e)

        return result

    return gen_status


class RedisCache(object):
    def __init__(self):
        if not hasattr(RedisCache, 'pool'):
            RedisCache.create_pool()
        self._connection = redis.Redis(connection_pool = RedisCache.pool)

    @staticmethod
    def create_pool():
        RedisCache.pool = redis.ConnectionPool(
                host = RedisDBConfig.HOST,
                port = RedisDBConfig.PORT,
                db   = RedisDBConfig.DBID)

    @operator_status
    def set_data(self, key, value):
        '''set data with (key, value)
        '''
        self._connection.set(key, value)
        return self._connection.expire(key, RedisDBConfig.EXPIRE)

    @operator_status
    def get_data(self, key):
        '''get data by key
        '''
        return self._connection.get(key)

    @operator_status
    def del_data(self, key):
        '''delete cache by key
        '''
        return self._connection.delete(key)


if __name__ == '__main__':
    print RedisCache().set_data('Testkey', "Simple Test")
    print RedisCache().get_data('Testkey')
    redraw_msg =  RedisCache().get_data('2121948384685456854')
    print redraw_msg
    print type(redraw_msg)
    username =  re.compile(': (.*), \'userid\'').findall(redraw_msg)[0]
    print username
    msg = re.compile('\'data\': (.*)}').findall(redraw_msg)[0]
    print msg.decode("unicode_escape").replace("\'","").replace("u","")
    print username.decode("unicode_escape").replace("\'","").replace("u","")

    m =  u'\u9738\u738b\u522b\u59ec'
    print m
    print u'\u628a\u6301'

    json.loads(redraw_msg.replace("\'","\""))



    print 'redraw_msg is ' + str(redraw_msg).replace("\\\\", "\\")

