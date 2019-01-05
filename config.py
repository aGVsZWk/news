import logging
import redis


class Config(object):
    # 调试模式
    DEBUG = True
    SECRET_KEY = "FJASJDL"

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@localhost:3306/information16"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True # 当链接关闭的时候，会自动提交

    # Redis配置
    REIDS_HOST = "192.168.188.134"
    REDIS_PORT = 6379

    #session配置
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.StrictRedis(host=REIDS_HOST,port=REDIS_PORT)
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = 3600*24*2 # 两天有效期，默认是秒

    # 默认的日志等级
    LEVEL = logging.DEBUG

# 开发环境
class DevelopConfig(Config):
       # DEBUG = False
    pass

# 生产环境(线上环境)
class ProductConfig(Config):
    DEBUG = False
    LEVEL = logging.ERROR

# 测试环境
class TestingConfig(Config):
    TESTING = True

# 配置环境的统一访问入口
config_dict = {
    "develop":DevelopConfig,
    "product":ProductConfig,
    "testing":TestingConfig
}
