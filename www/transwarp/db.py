# 数据库引擎对象：
class _Engine(object):
    def __init__(self, connect):
        self._connect = connect

    @property
    def connect(self):
        return self._connect()
