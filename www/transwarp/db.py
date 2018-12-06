#!/usr/bin/env python
# -*- coding: utf-8 -*-


__author__ = 'Bruce'

'''

Database operation module
'''

import time, uuid, functools, threading, logging


# Dict object:

class Dict(dict):
    """

    Simple dict but support access as x.y style


    >>> d1 = Dict()
    >>> d1['x'] = 100
    >>> d1.x
    100
    >>> d2 = Dict(a=1,b=2,c='3')
    >>> d2.c
    '3'
    >>> d2['empty']
    Traceback (most recent call last)
    >>> d3 = Dict(('a','b','c'),(1,2,3))
    >>> d3.a
    1
    >>> d3.b
    2
    """

    def __init__(self, name=(), value=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(name, value):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict',object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value


def next_id(t=None):
    """

    Return next id as 50-char string


    Args:
        t: unix timestamp, default to None and using time.time().
    """

    if t is None:
        t = time.time()
    return '%015d%s000' % (int(t * 1000), uuid.uuid4().hex)


def _profiling(start, sql=''):
    t = time.time() - start
    if t > 0.1:
        logging.warning('[PROFILING] [DB] %s: %s' % (t, sql))
    else:
        logging.info('[PROFILING] [DB] %s: %s' % (t, sql))


class DBError(Exception):
    pass


class MultiColumnsError(DBError):
    pass


class _LasyConnection(object):

    def __init__(self):
        self.connection = None

    def cursor(self):
        if self.connection is None:
            connection = engine.connect()
            logging.info('open connection <%s>...' % hex(id(connection)))
            self.connection = connection
        return self.connection.cursor()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def cleanup(self):
        if self.connection:
            connection = self.connection
            self.connection = None
            logging.info('close connection <%s>...' % hex(id(connection)))
            connection.close()


class _DbCtx(threading.local):
    """

    Thread local object that holds connection info.
    """

    def __init__(self):
        self.connection = None
        self.transaction = 0

    def is_init_(self):
        return not self.connection is None

    def init(self):
        logging.info('open lazy connection...')
        self.connection = _LasyConnection()
        self.transaction = 0

    def cleanup(self):
        self.connection.cleanup()
        self.connection = None

    def cursor(self):
        """

        Return cursor
        """
        return self.connection.cursor()


# thread-local db context:
_db_ctx = _DbCtx()

# global engine object
engine = None


class _Engine(object):

    def __init__(self, connect):
        self._connect = connect

    def connect(self):
        return self._connect()


def create_engine(user, password, database, host='127.0.0.1', port=3306, **kw):
    import mysql.connector
    global engine
    if engine is not None:
        raise DBError('Engine is already initialized. ')
    params = dict(user=uer, password=password, database=database, host=host, port=port)
    defaults = dict(use_unicode=True, charset='utf8', collation='utf8_general_ci', autocommit=False)
    for k,v in defaults.iteritem():
        params[k] = kw.pop(k, v)
    params.update(kw)
    params['buffered'] = True
    engine = _Engine(lambda: mysql.connector.connect(**params))
    # test connection...
    logging.info('Init mysql engine <%s> ok.' % hex(id(engine)))


class _ConnectionCtx(object):
    """

    _ConnectionCtx object that can open and close connection context. _ConnectionCtx object can be nested and only the
    most outer connection has effect.


    with connection():
        pass
        with connection():
            pass
    """

    def __enter__(self):
        global _db_ctx
        self.should_cleanup = False
        if not _db_ctx.is_init():
            _db_ctx.init()
            self.should_cleanup = True
        return self

    def __exit__(self, exctype, excvalue, traceback):
        global _db_ctx
        if self.should_cleanup:
            _db_ctx.cleanup()


    def connection():
        """

        Return _ConnectionCtx object that can be used by 'with' statement:

        with connection()
            pass
        """
        return _ConnectionCtx()


    def with_connection(func):
        """

        Decorator for reuse connection


        @with_connection
        def foo(*args, **kw):
            f1()
            f2()
            f3()
        """
        @functool.wraps(func)
        def _wrapper(*args, **kw)
            with _ConnectionCtx():
                return func(*args, **kw)
        return _wrapper



    class _TransactionCtx(object):
        """

        _TransactionCtx object that can handle transactions.

        with _TransactionCtx()
            pass
        """

        def __enter__(self):
            global _db_ctx
            self.should_close_conn = False
            if not _db_ctx.is_init():
                # needs open a connection first
                _db_ctx.init()
                self.should_close_conn = True
            _db_ctx.transactions = _db_ctx.transactions + 1
            logging.info('begin transaction...' if _db_ctx.transactions==1 else 'join current transaction...')
            return self













