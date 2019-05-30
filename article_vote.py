import time

from db import get_redis_client

# 一周的秒数
ONE_WEEK_IN_SECONDS = 7 * 86400
# 一票的分数
VOTE_SCORE = 432
# 每页文章数
ARTICLE_PER_PAGE = 25


def article_vote(conn, user: str, article: str):
    """
    文章投票函数
    :param conn: redis客户端
    :param user: 投票用户    user:22
    :param article: 文章   article:10088
    :return:
    """
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


def post_article(conn, user, title, link):
    """
       发布新文章
       :param conn:
       :param user:
       :param title:
       :param link:
       :return:
       """
    # 字符出自增生成文章id
    article_id = conn.incr('article:')

    # 将作者添加到以投票用户组，并设置过期时间为一周
    voted = 'voted:' + article_id
    conn.sadd(voted, user)
    conn.expire(voted, ONE_WEEK_IN_SECONDS)

    # 添加文章，添加文章分数和时间有序集合
    now = time.time()
    article = 'article:' + article_id
    conn.hmset(article, {
        'title': title,
        'link': link,
        'poster': user,
        'time': now,
        'votes': 1
    })

    conn.zadd('score:', article, now + VOTE_SCORE)
    conn.sadd('time:', article, now)

    return article_id


def get_articles(conn, page, order='score:'):
    """
    获取分数高的文章
    :param conn:
    :param page:
    :param order:
    :return:
    """
    # 获取起始页
    start = (page - 1) * ARTICLE_PER_PAGE
    end = start + ARTICLE_PER_PAGE - 1

    ids = conn.zrevrange(order, start, end)
    # 文章列表
    articles = []
    for id in ids:
        article_detail = conn.hgetall(id)
        article_detail['id'] = id
        articles.append(article_detail)

    return articles


if __name__ == '__main__':
    redis_cli = get_redis_client()
    article_vote(redis_cli, 'user:70', 'article:10086')
