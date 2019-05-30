import time

from db import get_redis_client

# 一周的秒数
ONE_WEEK_IN_SECONDS = 7 * 86400
# 一票的分数
VOTE_SCORE = 432


def article_vote(conn, user: str, article: str):
    # 计算一周前的时间点
    cutoff = time.time() - ONE_WEEK_IN_SECONDS
    # 判断文章发布时间是否过了一周
    if conn.zscore('time:', article) < cutoff:
        return

    article_id = article.partition(':')[-1]
    try:
        # 将用户添加到该文章已投票用户列表中去，根据返回bool判断是否投过票
        if conn.sadd('voted:' + article_id, user):
            # 增加对应文章的分数
            conn.zincrby(name='score:', value=article, amount=VOTE_SCORE)
            # 增加对应文章的票数
            conn.hincrby(article, 'votes', 1)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    redis_cli = get_redis_client()
    article_vote(redis_cli, 'user:70', 'article:10086')
