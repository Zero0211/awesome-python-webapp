#!/usr/bin/env python
# -*- coding: utf-8 -*-


__author__ = 'Bruce'

'''

Database operation module
'''


import time, uuid, functools, threading, logging

#Dict object:

class Dict(dict):
    '''

    Simple dict but support access as x.y style


    >>> d1 = Dict()
    >>> d1['x'] = 100
    >>> d1.x
    100
    '''

# 数据库引擎对象：
class _Engine(object):
    def __init__(self, connect):
        self._connect = connect

    @property
    def connect(self):
        return self._connect()


engine = None


# 持有数据库连接的上下文
class _DbCtx(threading.local):
    def __init__(self):
        self.connection = None
        self.transaction = 0

    @property
    def is_init_(self):
        return not self.connection is None


    def init(self):
        self.connection = _LasyConnection()

