from flask import request

from info import redis_store
from info.utils.response_code import RET
from . import index_blu
from flask import render_template,current_app, jsonify
from flask import session
from info.models import User, News, Category


#功能描述: 首页新闻列表获取
# 请求路径: /newslist
# 请求方式: GET
# 请求参数: cid,page,per_page
# 返回值: data数据
@index_blu.route('/newslist')
def news_list():

    """
    1.获取参数
    2.参数类型转换,为了分页 做准备,paginate(page,per_page,False)
    3.分页查询
    4.取出分页对象中的属性,总页数,当前页,当前页对象
    5.将当前页对象列表,转成字典列表
    6.返回响应
    :return:
    """
    # 1.获取参数
    cid = request.args.get("cid","1")
    page = request.args.get("page","1")
    per_page = request.args.get("per_page","10")

    # 2.参数类型转换，为了分页做准备，paginate(page,per_page,False)
    try:
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        page = 1
        per_page = 10

    # 3.分页查询
    try:
        # paginate = News.query.filter(News.category_id == cid).\
        #     order_by(News.create_time.desc()).paginate(page,per_page,False)

        # 判断是否cid != 1，不是最新
        # condition = ""
        filters = []
        if cid != "1":
            # condition = News.category_id == cid
            filters.append(News.category_id == cid)

        # paginate = News.query.filter(News.category_id == cid).order_by(News.create_time.desc()).paginate(page,per_page,False)
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,per_page,False)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取新闻失败")

    # 4.取出分类对象中的属性，总页数，当前页，当前页对象
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items


    # 5.将当前页对象列表，转成字典列表
    newsList = []
    for item in items:
        newsList.append(item.to_dict())

    # 6.返回响应
    return jsonify(errno=RET.OK,errmsg="获取成功",totalPage=totalPage,
                   currentPage=currentPage,newsList=newsList)


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

    # 2,3 查询所有分类信息
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)

    # 2.4 讲分类对象列表，转成字典列表
    category_list = []
    for category in categories:
        category_list.append(category.to_dict())


    # 3.拼接用户数据渲染界面
    data = {
        # 如果user不为空，返回左边的内容，为空返回右边的内容
        "user_info":user.to_dict() if user else "",
        "click_news_list":click_news_list,
        "categories":category_list
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