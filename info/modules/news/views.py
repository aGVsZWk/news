from flask import abort
from flask import current_app, jsonify
from flask import g
from flask import render_template
from flask import session

from info.models import News, User
from info.utils.commons import user_login_data
from info.utils.response_code import RET
from . import news_blue


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


    # 3.携带新闻数据，到模板界面那显示
    data = {
        "news":news.to_dict(),
        "click_news_list":click_news_list,
        "user_info":g.user.to_dict() if g.user else ""
    }


    return render_template("news/detail.html",data=data)