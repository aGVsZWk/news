"""
项目的初始化配置信息:
项目的初始化配置信息:

1.数据库配置

2.redis配置

3.csrf配置，对‘POST’，‘PUT’，‘PATCH’，‘DELETE’请求方式做保护

4.session配置,为了后续登陆保持,做铺垫

5.日志信息配置

6.数据库迁移配置
"""""

from flask import Flask,session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf import CSRFProtect

app = Flask(__name__)


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

app.config.from_object(Config)

# 创建SQLAlchemy对象，关联app
db = SQLAlchemy(app)

# 创建redis对象
redis_store = redis.StrictRedis(host=Config.REIDS_HOST,port=Config.REDIS_PORT,decode_responses=True)



CSRFProtect(app)


Session(app)

@app.route("/")
def hello_world():
    # 测试redis
    redis_store.set("name","laowang")
    print(redis_store.get("name"))
    # 测试session
    session["protect"] = "myprotect"
    print(session.get("protect"))

    return "helloworld100"


if __name__ == '__main__':
    app.run()
