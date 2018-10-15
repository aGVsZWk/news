import redis


class Config(object):
    # 调试模式
    DEBUG = True
    SECRET_KEY = "FJASJDL"

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@localhost:3306/information16"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # Redis配置
    REIDS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    #session配置
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.StrictRedis(host=REIDS_HOST,port=REDIS_PORT)
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = 3600*24*2 # 两天有效期，默认是秒
