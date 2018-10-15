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
import logging

from flask import current_app

from info import create_app

app = create_app("develop")


@app.route("/")
def hello_world():


    # 使用logging日志输出内容
    logging.debug("调试信息")
    logging.error("炸了")

    # 使用current_app输出内容
    # current_app.logger.error("使用current_app.logger炸")

    # 测试redis
    # redis_store.set("name","laowang")
    # print(redis_store.get("name"))

    # 测试session
    # session["protect"] = "myprotect"
    # print(session.get("protect"))

    return "helloworld100"


if __name__ == '__main__':
    app.run()