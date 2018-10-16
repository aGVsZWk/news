from info import redis_store
from . import index_blu
from flask import render_template,current_app


@index_blu.route("/")
def hello_world():


    # 使用logging日志输出内容
    # create_app("product")配好，使用等级为error，下面=只显示error信息
    # logging.debug("调试信息")
    # logging.info("详细信息")
    # logging.warning("警告信息")
    # logging.error("错误信息")

    # 使用current_app输出内容
    # current_app.logger.error("使用current_app.logger炸")

    # 测试redis
    # redis_store.set("name","laowang")
    # print(redis_store.get("name"))

    # 测试session
    # session["protect"] = "myprotect"
    # print(session.get("protect"))

    return render_template("news/index.html")

@index_blu.route('/favicon.ico')
def web_logo():

    return current_app.send_static_file("news/favicon.ico")