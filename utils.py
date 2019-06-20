import time

QUIT = False
LIMIT = 1000000


def clean_sessions(conn):
    """
    定时任务，当登录的token超过1000000时，就删除旧数据
    :param conn:
    :return:
    """
    while not QUIT:
        size = conn.zcard("recent:")
        if size < LIMIT:
            time.sleep(1)
            continue

        end_index = min(size, 100)
        # 获取需要移除的令牌
        token = conn.zrange("recent:", 0, end_index - 1)
        # 构建要删除的键名
        session_keys = []
        for t in token:
            session_keys.append("viewed:" + t)
            session_keys.append("cart:" + t)
        # 删除用户浏览的商品，购物车数据
        conn.delete(*session_keys)
        # 删除用户映射
        conn.hdel("login:", *token)
        # 删除最近登录
        conn.zrem("recent:", *token)


if __name__ == '__main__':
    print(min(123, 100))
