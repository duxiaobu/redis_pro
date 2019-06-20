import time
import json

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


def cache_rows(conn):
    """
    持续运行缓存函数
    :param conn:
    :return:
    """
    while not QUIT:
        # 获取最新需要缓存的数据ID
        next_row = conn.zrange("schedule:", 0, 0, withscores=True)
        now = time.time()
        if not next_row or next_row[0][1] > now:
            time.sleep(0.05)
            continue

        row_id = next_row[0][0]
        delay = conn.zscore("delay:", row_id)
        if delay <= 0:
            # 删除相关数据
            conn.zrem("delay:", row_id)
            conn.zrem("schedule:", row_id)
            conn.delete("inv:" + row_id)
            continue

        # 从数据库中读取数据行，这里使用模拟数据
        data = {"qty": 120, "name": "可口可乐", "desc": "cool~~"}
        # 更新调度时间
        conn.zadd("schedule:", row_id, now+delay)
        # 缓存数据
        conn.set("inv:" + row_id, json.dumps(data))


if __name__ == '__main__':
    print(min(123, 100))
