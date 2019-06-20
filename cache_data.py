import time


class CacheData(object):
    def __init__(self, conn):
        self.conn = conn

    def schedule_row_cache(self, row_id, delay):
        """
        通过组合使用调度函数和持续运行缓存函数，实现重复调度自动缓存的机制。
        对于特价促销等商品可以几秒缓存一次，对于不经常变动的数据，可以几分钟缓存一次
        :param row_id:
        :param delay:
        :return:
        """
        self.conn.zadd("delay:", row_id, delay)
        self.conn.zadd("schedule:", row_id, time.time())
