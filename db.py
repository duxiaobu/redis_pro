import redis


def get_redis_client():
    return redis.Redis(host='192.168.0.200', db=3)


if __name__ == '__main__':
    # 测试连接
    redis_cli: redis = get_redis_client()
    # rs: bool = redis_cli.set("name", "bob")
    # rs1: bytes = redis_cli.get('name')
    # print(rs, rs1.decode('utf-8'))

    # 实例化命令管道
    pipe = redis_cli.pipeline()
    try:
        # 开启事务
        pipe.multi()
        # 使用hash结构存储每篇文章信息
        article_entity = {
            'title': '活着',
            'link': 'http://huozhe.com',
            'poster': '余华',
            'time': 1559185143.32,
            'votes': 528
        }
        pipe.hmset('article:10086', article_entity)

        # 根据发布时间排序文章有序集合(zset结构)
        article_time = {
            'article:10086': 1559185143.32,
            'article:10087': 1559185155.32,
            'article:10088': 1559185188.32
        }
        pipe.zadd('time:', article_time)

        # 根据文章分数排序文章有序集合
        article_score = {
            'article:10086': 7463,
            'article:10087': 19431,
            'article:10088': 5732
        }
        pipe.zadd('score:', article_score)

        # 每篇文章已投票用户组(使用set结构)
        article_user = ('user:23', 'user:34', 'user:77', 'user:45')
        pipe.sadd('voted:10086', *article_user)

        # 执行事务
        pipe.execute()
        print('redis数据填充成功')
    except Exception as e:
        print(e)
        pass
    finally:
        # 返回连接
        pipe.reset()
