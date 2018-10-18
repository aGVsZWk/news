from info import redis_store
from info.utils.response_code import RET
from . import index_blu
from flask import render_template,current_app, jsonify
from flask import session
from info.models import User, News


@index_blu.route("/")
def hello_world():
    # 1.取出session中的用户编号
    user_id = session.get("user_id")

    # 2.获取用户对象
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 2.1 热门新闻，按照新闻的点击量，查询前10条新闻
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(10).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取新闻失败")

    # 2.2 将新闻列表对象，搞成字典列表对象
    click_news_list = []
    for news in news_list:
        click_news_list.append(news.to_dict())


    # 3.拼接用户数据渲染界面
    data = {
        # 如果user不为空，返回左边的内容，为空返回右边的内容
        "user_info":user.to_dict() if user else "",
        "click_news_list":click_news_list
    }

    return render_template("news/index.html",data=data)








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

    # return render_template("news/index.html")

@index_blu.route('/favicon.ico')
def web_logo():

    return current_app.send_static_file("news/favicon.ico")