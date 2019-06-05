import time

from db import get_redis_client


class ArticleVote(object):
    # 一周的秒数
    ONE_WEEK_IN_SECONDS = 7 * 86400
    # 一票的分数
    VOTE_SCORE = 432
    # 每页文章数
    ARTICLE_PER_PAGE = 25

    def __init__(self, conn):
        self.conn = conn

    def article_vote(self, user: str, article: str):
        """
        文章投票函数
        :param user: 投票用户    user:22
        :param article: 文章   article:10088
        :return:
        """
        # 计算一周前的时间点
        cutoff = time.time() - self.ONE_WEEK_IN_SECONDS
        # 判断文章发布时间是否过了一周
        if self.conn.zscore('time:', article) < cutoff:
            return

        article_id = article.partition(':')[-1]
        try:
            # 将用户添加到该文章已投票用户列表中去，根据返回bool判断是否投过票
            if self.conn.sadd('voted:' + article_id, user):
                # 增加对应文章的分数
                self.conn.zincrby(name='score:', value=article, amount=self.VOTE_SCORE)
                # 增加对应文章的票数
                self.conn.hincrby(article, 'votes', 1)
        except Exception as e:
            print(e)

    def post_article(self, user, title, link):
        """
           发布新文章
           :param user:
           :param title:
           :param link:
           :return:
           """
        # 字符出自增生成文章id
        article_id = self.conn.incr('article:')

        # 将作者添加到以投票用户组，并设置过期时间为一周
        voted = 'voted:' + article_id
        self.conn.sadd(voted, user)
        self.conn.expire(voted, self.ONE_WEEK_IN_SECONDS)

        # 添加文章，添加文章分数和时间有序集合
        now = time.time()
        article = 'article:' + article_id
        self.conn.hmset(article, {
            'title': title,
            'link': link,
            'poster': user,
            'time': now,
            'votes': 1
        })

        self.conn.zadd('score:', article, now + self.VOTE_SCORE)
        self.conn.sadd('time:', article, now)

        return article_id

    def get_articles(self, page, order='score:'):
        """
        获取分数高的文章
        :param page:
        :param order:
        :return:
        """
        # 获取起始页
        start = (page - 1) * self.ARTICLE_PER_PAGE
        end = start + self.ARTICLE_PER_PAGE - 1

        ids = self.conn.zrevrange(order, start, end)
        # 文章列表
        articles = []
        for _id in ids:
            article_detail = self.conn.hgetall(_id)
            article_detail['id'] = _id
            articles.append(article_detail)

        return articles

    def add_remove_group(self, article_id: str, add_group: list, remove_group: list):
        """
        添加移除文章到分组
        :param article_id:
        :param add_group:
        :param remove_group:
        :return:
        """
        article = 'article:' + article_id
        # 将该文章添加到所属分组中
        for group in add_group:
            self.conn.sadd('group:' + group, article)

        # 将文章从分组中移除
        for group in remove_group:
            self.conn.srem('group:' + group, article)

    def get_group_articles(self, group: str, page: int, order: str = 'score:'):
        """
        获取分组文章
        :param group:
        :param page:
        :param order:
        :return:
        """
        key = order + group
        # 如果缓存中没有该数据，就去redis中获取
        if not self.conn.exists(key):
            self.conn.zinterstore(key, ['group:' + group, order], aggregate='max')
            # 将结果缓存60s
            self.conn.expire(key, 60)

        return self.get_articles(page, key)


if __name__ == '__main__':
    conn = get_redis_client()
    conn.zinterstore()
    article_vote = ArticleVote(conn)
