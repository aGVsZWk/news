"""
项目的初始化配置信息:
项目的初始化配置信息:

1.数据库配置

2.redis配置

3.csrf配置

4.session配置,为了后续登陆保持,做铺垫

5.日志信息配置

6.数据库迁移配置
"""""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
class Config(object):
    # 调试模式
    DEBUG =True

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@localhost:3306/information16"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app.config.from_object(Config)

# 创建SQLAlchemy对象，关联app
db = SQLAlchemy(app)



@app.route("/")
def hello_world():
    return "helloworld100"


if __name__ == '__main__':
    app.run()
