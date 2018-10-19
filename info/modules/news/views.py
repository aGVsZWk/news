from flask import abort
from flask import current_app, jsonify
from flask import g
from flask import render_template
from flask import request
from flask import session

from info.models import News, User
from info.utils.commons import user_login_data
from info.utils.response_code import RET
from . import news_blue


# 功能描述：收藏取消/收藏
# 请求路径：/news/news_collect
# 请求方式：POST
# 请求参数：news_id,action,g.user
# 返回值：errno,errmsg
@news_blue.route('/news_collect', methods=['POST'])
def news_collect():
    """
    1. 判断用户登陆状态
    2.获取参数
    3.校验参数，为空检验
    4.判断操作类型
    5.通过新闻编号取出新闻对象
    6.判断新闻对象是否存在
    7.根据操作类型，收藏，取消操作
    8.返回响应

    :return:
    """
    # 1.判断用户登陆状态
    if not g.user:
        return jsonify(errno=RET.NODATA,errmsg="用户未登录")

    # 2. 获取从参数
    news_id = request.json.get("news_id")
    action = request.json.get("action")

    # 3. 校验参数，为空校验
    if not all([news_id,action]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")

    # 4.判断操作类型
    if not action in ["collect","cancel_collect"]:
        return jsonify(errno=RET.DATAERR,errmsg="操作类型有误")

    # 5.通过新闻编号取出新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg="新闻获取失败")

    # 6.判断新闻对象是否存在
    if not news:
        return jsonify(errno=RET.NODATA,errmsg="新闻不错存在")

    # 7.根据操作类型，收藏，取消操作
    #　添加收藏
    try:
        if action == "collect":
            if not news in g.user.collection_news:
                g.user.collection_news.append(news)
        # 取消收藏
        else:
            if news in g.user.collection_news:
                g.user.collection_news.remove(news)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="操作失败")

    # 8.返回响应
    return jsonify(errno=RET.OK,errmsg="操作成功")





# 获取新闻详情
# 请求路径：/news/<int:news_id>
# 请求方式：GET
# 请求参数：news_id
# 返回值：detail.html页面，用户data字典数据

@news_blue.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):

    # 1.根据新闻编号获取，新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="新闻获取失败")
    # 2.判断新闻对象是否存在，后续会对404做统一处理
    if not news:
        abort(404)

    # 2.1 热门新闻，按照新闻的点击量，查询前10条新闻
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(8).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="新闻获取失败")
    # 2.2 将新闻列表对象，转换成字典列表对象

    click_news_list = []
    for click_news in news_list:
        click_news_list.append(click_news.to_dict())

    # # 2.3取出session中的用户编号
    # user_id = session.get("user_id")
    #
    # # 2.4 获取用户对象
    # user = None
    # if user_id:
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)

    # 2.3 判断用户是否收藏了该新闻
    is_collected = False
    if g.user and news in g.user.collection_news:
        is_collected = True


    # 3.携带新闻数据，到模板界面那显示
    data = {
        "news":news.to_dict(),
        "click_news_list":click_news_list,
        "user_info":g.user.to_dict() if g.user else "",
        "is_collected":is_collected
    }


    return render_template("news/detail.html",data=data)