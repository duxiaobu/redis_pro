import time


class LoginCookie(object):
    def __init__(self, conn):
        self.conn = conn

    def check_token(self, token: str):
        return self.conn.hget("login:" + token)

    def update_token(self, token: str, user, item=None):
        # 获取当前时间
        cur_timestamp = time.time()
        # 记录token和user的映射
        self.conn.hset("login:" + token, user)
        # 记录用户最后次登录时间
        self.conn.zadd("recent:", token, cur_timestamp)
        if item:
            # 记录用户浏览的商品
            self.conn.zadd("viewed:" + token, item, cur_timestamp)
            # 只记录最近浏览的25个商品
            self.conn.zremrangebyrank("viewed:" + token, 0, -26)

    def add_to_cart(self, token, item, count):
        """
        添加进购物车
        :param token:
        :param item:
        :param count:
        :return:
        """
        if count <= 0:
            # 移除商品
            self.conn.hrem("cart:" + token, item)
        else:
            # 添加商品
            self.conn.hset("cart:" + token, item, count)