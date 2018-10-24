from datetime import datetime, timedelta
import time
from flask import current_app, jsonify
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session

from info.models import User, News, Category
from info.utils.commons import user_login_data
from info.utils.image_storage import image_storage
from info.utils.response_code import RET
from . import admin_blue


# 功能描述；新闻编辑详情
# 请求路径：/admin/news_edit_detail
# 请求方式：GET，POST
# 请求参数：GET,news_id,POST(news_id,title,digest,content,index_image,category_id)
# 返回值:GET,渲染news_edit_detail.html页面,data字典数据, POST(errno,errmsg)
@admin_blue.route('/news_edit_detail', methods=['GET', 'POST'])
def news_edit_detail():
    """
    1.判断请求方式，如果是GET
    1.1 获取参数
    1.2 校验参数
    1.3 取出新闻对象，判断新闻对象是否存在
    1.4 携带新闻数据，渲染页面
    2.获取参数
    3.校验参数，为空校验
    4.根据新闻编号，获取新闻对象
    5.上传图片
    6.判断图片是否上传成功
    7.设置编辑信息，到对象列表
    8.返回响应

    :return:
    """
    # 1.判断请求方式，如果是GET
    if request.method == "GET":

        # 1.1 获取参数
        news_id = request.args.get("news_id")

        # 1.2 校验参数
        if not news_id: return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

        # 1.3 取出新闻对象，判断新闻对象是否存在
        try:
            news = News.query.get(news_id)
            categories = Category.query.all()
            categories.pop(0) # 弹出最新
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg="获取新闻或分类失败")

        # 1.4 携带新闻数据，渲染页面
        if not news:return jsonify(errno=RET.DBERR,errmsg="新闻不存在")

        # 分类列表，转成字典列表
        category_list = []
        for category in categories:
            category_list.append(category.to_dict())
        return render_template("admin/news_edit_detail.html",news=news.to_dict(),categories=category_list)

    # 2.获取参数
    news_id = request.form.get("news_id")
    title = request.form.get("title")
    digest = request.form.get("digest")
    content = request.form.get("content")
    # 不知道为啥，收不到图片
    index_image = request.form.get("index_image")
    category_id = request.form.get("category_id")

    # 3.校验参数，为空校验
    # if not all([news_id,title,digest,content,index_image,category_id]):
    # TODO 收不到图片
    if not all([news_id,title,digest,content,category_id]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")

    # 4.根据新闻编号，获取新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取新闻失败")

    # 5.上传图片
    # try:
    #     image_name = image_storage(index_image.read())
    # except Exception as e:
    #     current_app.logger.error(e)
    #     request jsonify(errno=RET.THIRDERR,errmsg="七牛云异常")
    # 6.判断图片是否上传成功
    # if not image_name:return jsonify(errno=RET.DATAERR,errmsg="图片上传失败")

    # 7.设置编辑信息，到对象列表
    news.title = title
    news.digest = digest
    news.content = content
    news.index_image_url = "ASDHKHQ"
    news.category_id = category_id

    # 8.返回响应
    return jsonify(errno=RET.OK,errmsg="编辑成功")



# 功能描述:新闻编辑列表
# 请求路径：/admin/news_edit
# 请求方式：GET
# 请求参数：GET，P,keywords
# 返回值：GET，渲染news_edit.html页面，data字典数据
@admin_blue.route('/news_edit')
def news_edit():
    """
    1.获取参数
    2.参数类型转换
    3.分页查询
    4.获取分页对象属性，总页数，当前页，当前页对象
    5.将对象列表，转成字典列表
    6.携带数据渲染界面
    :return:
    """

    # 1.获取参数
    page = request.args.get("p","1")
    keywords = request.args.get("keywords")

    # 2.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # 3.分页查询
    try:
        # 判断，是否有搜索关键字
        filters = []
        if keywords:
            filters.append(News.title.contains(keywords))

        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,10,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取新闻失败")

    # 4.获取分页对象属性，总页数，当前页，当前页对象
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5.将对象列表，转成字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_review_dict())

    # 6.携带数据渲染界面
    data = {
        "totalPage":totalPage,
        "currentPage":currentPage,
        "news_list":news_list
    }
    return render_template("admin/news_edit.html",data=data)

# 功能描述：新闻审核详情
# 请求路径：/admin/news_review_detail
# 请求方式：GET，POST
# 请求参数：GET,news_id,POST,news_id,action
# 返回值：GET，渲染news_review_detail.html页面，data字典数据
@admin_blue.route('/news_review_detail', methods=['GET', 'POST'])
def news_review_detail():
    """
    1.判断请求方式，如果是GET
    1.1获取参数
    1.2校验参数
    1.3取出新闻对象，判断新闻对象是否存在
    1.4携带新闻数据，渲染页面
    2.获取参数
    3.校验参数，为空校验
    4.校验操作类型
    5.根据新闻编号，查询新闻对象
    6.判断新闻对象是否存在
    7.根据操作类型，改变新闻的状态
    8.返回响应
    :return:
    """
    # 1.判断请求方式，如果是GET
    if request.method == "GET":
        # 1.1获取参数
        news_id = request.args.get("news_id")

    # 1.2校验参数
        if not news_id:return jsonify(errno=RET.PARAMERR,errmsg="参数不全")

    # 1.3取出新闻对象，判断新闻对象是否存在
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg="获取新闻不存在")
        if not news:return jsonify(errno=RET.NODATA,errmsg="新闻不存在")

        # 1.4携带新闻数据，渲染页面
        return render_template("admin/news_review_detail.html",news=news.to_dict())
    # 2.获取参数
    news_id = request.json.get("news_id")
    action = request.json.get("action")

    # 3.校验参数，为空校验
    if not all([news_id,action]):
        return jsonify(errno=RET.DATAERR,errmsg="操作类型有误")

    # 4.校验操作类型
    if not action in ["accept","reject"]:
        return jsonify(errno=RET.DATAERR,errmsg="操作类型有误")

    # 5.根据新闻编号，查询新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取新闻失败")

    # 6.判断新闻对象是否存在
    if not news:return jsonify(errno=RET.NODATA,errmsg="新闻不存在")

    # 7.根据操作类型，改变新闻的状态
    if action == "accept":
        news.status = 0
    else:
        reason = request.json.get("reason","")
        news.reason = reason
        news.status = -1
    # 8.返回响应
    return jsonify(errno=RET.OK,errmsg="审核成功")

# 功能：新闻审核列表
# 请求路径：/admin/news_review
# 请求方式：GET
# 请求参数：GET，p
# 返回值：渲染user_list.html页面，data字典数据
@admin_blue.route('/news_review')
def news_review():
    """
    1.获取参数
    2.参数类型转换
    3.分页查询
    4.获取分页对象属性，总页数，当前页，当前页对象
    5.将对象列表，转成字典列表
    6.携带数据渲染界面
    :return:
    """
    # 1.获取参数
    page = request.args.get("p","1")
    keywords = request.args.get("keywords")

    # 2.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # 3.分页查询
    try:
        #判断，是否有搜索关键字
        filters = [News.status != 0 ]
        if keywords:
            filters.append(News.title.contains(keywords))

        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,10,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取新闻失败")


    # 4.获取分页对象属性，总页数，当前页，当前页对象
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5.将对象列表，转成字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_review_dict())

    # 6.携带数据渲染界面
    data = {
        "totalPage":totalPage,
        "currentPage":currentPage,
        "news_list":news_list
    }
    return render_template("admin/news_review.html",data=data)


# 功能描述：用户列表统计
# 请求路径：/admin/user_list
# 请求方式：GET
# 请求参数：p
# 返回值：渲染user_list.html页面，data字典数据
@admin_blue.route("/user_list")
def user_list():
    """
    1.获取参数
    2.参数类型转换
    3.分页查询
    4.获取分页对象属性，总页数，当前页，当前页对象
    5.将对象列表，转成字典列表
    6.携带数据渲染页面
    :return:
    """
    # 1.获取参数
    page = request.args.get("p","1")

    # 2.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # 3.分页查询
    try:
        paginate = User.query.filter(User.is_admin == False).order_by(User.create_time.desc()).paginate(page,10,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取用户失败")

    # 4.获取分页对象属性，总页数，当前页，当前页对象
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5.将对象列表，转成字典列表
    user_list = []
    for user in items:
        user_list.append(user.to_admin_dict())

    # 6.携带数据渲染页面
    data = {
        "totalPage":totalPage,
        "currentPage":currentPage,
        "user_list":user_list
    }

    return render_template("admin/user_list.html",data=data)


# 用户统计
# 请求路径：/admin/user_count
# 请求方式：GET
# 请求参数：无
# 返回值：渲染页面 user_count.html，字典数据
@admin_blue.route('/user_count')
def user_count():
    """
    1.查询总人数，不包含管理员
    2.查询月活人数
    3.查询日活人数
    4.时间段内的，活跃人数
    5.携带数据，渲染页面
    :return:
    """
    # 1.查询总人数，不包含管理员
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger(e)

    # 2.查询月活人数
    cal = time.localtime()
    try:
        # 2.1 本月1号的0点的字符串表示
        month_startTime_str = "%d-%d-01"%(cal.tm_year,cal.tm_mon)
        month_startTime_data = datetime.strptime(month_startTime_str,"%Y-%m-%d")

        # 2.2 此时的时间
        month_endTime_data = datetime.now()

        # 2.3 查询时间段内的人数
        month_count = User.query.filter(User.last_login >= month_startTime_data,User.last_login <= month_endTime_data, User.is_admin ==False).count()
    except Exception as e:
        current_app.logger.error(e)


    # 3.查询日活人数
    try:
        # 2.1 本月1号的0点的字符串表示
        day_startTime_str = "00-00-00"
        day_startTime_data = datetime.strptime(day_startTime_str,"%H-%M-%S")

        # 2.2 此时的时间
        day_endTime_data = datetime.now()

        # 2.3 查询时间段内的人数
        day_count = User.query.filter(User.last_login >= day_startTime_data,User.last_login <= day_endTime_data, User.is_admin ==False).count()
    except Exception as e:
        current_app.logger.error(e)

    # 4.时间段内的，活跃人数
    time_startTime_str = "%d-%d-%d"%(cal.tm_year,cal.tm_mon,cal.tm_mday)
    time_startTime_data = datetime.strptime(time_startTime_str, "%Y-%m-%d")

    active_date = [] # 活跃的日期
    active_count = [] #　获取人数
    for i in range(0,31):
        # 当前开始的时间 A
        begin_date = time_startTime_data - timedelta(days=i)
        # 当天开始时间的后一天B
        end_date = time_startTime_data - timedelta(days=i - 1)

        # 添加当天开始时间字符串到活跃日期中
        active_date.append(begin_date.strftime("%m-%d"))

        # 查询时间Ａ到时间Ｂ这一天的注册人数
        everyday_active_count = User.query.filter(User.is_admin == False, User.last_login >= begin_date, User.last_login <= end_date).count()



        #添加当天注册人数，到获取数量中
        active_count.append(everyday_active_count)

    # 为了方便查看反转图标
    active_date.reverse()
    active_count.reverse()



    # 5.携带数据，渲染页面
    data = {
        "total_count":total_count,
        "month_count":month_count,
        "day_count":day_count,
        "active_date":active_date,
        "active_count":active_count
    }
    return render_template("admin/user_count.html",data=data)

# 显示管理员首页界面
# 请求路径：/admin/index
#　请求方式： GET
# 请求参数：无
#　返回值：渲染界面index.html,user字典数据
@admin_blue.route('/index')
@user_login_data
def admin_index():
    admin = g.user.to_dict()
    return render_template("admin/index.html",admin=admin)






# 显示登陆页面
@admin_blue.route("/login",methods=["GET","POST"])

def admin_login():
    """
    1.判断请求方式，如果是GET请求，直接返回登陆页面
    2.如果是POST,获取参数
    3.校验参数，为空校验x
    4.通过用户名，查询管理员对象，并判断管理员是否存在
    5.判断密码是否正确
    6.记录管理员session信息
    7.重定向到首页
    :return:
    """

    # 1.判断请求方式，如果是GET请求，直接返回登陆页面
    if request.method == "GET":

        # 判断管理员是否，已经登陆过
        if session.get("is_admin"):
            return  redirect("/admin/index")

        return render_template("admin/login.html")

    # 2.如果是POST,获取参数
    username = request.form.get("username")
    password = request.form.get("password")

    # 3.校验参数，为空校验
    if not all([username,password]):
        return render_template("admin/login.html",errmsg="参数不全")

    # 4.通过用户名，查询管理员对象，并判断管理员是否存在
    try:
        admin = User.query.filter(User.mobile == username,User.is_admin == True).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/login.html",errmsg="获取管理员失败")

    if not admin:
        return render_template("admin/login.html",errmsg="管理员不存在")

    # 5.判断密码是否正确
    if not admin.check_passowrd(password):
        return render_template("admin/login.html",errmsg="密码错误")

    # 6.记录管理员session信息
    session["name"] = admin.id
    session["nick_name"] = admin.nick_name
    session["mobile"] = admin.mobile
    session["is_admin"] = admin.is_admin

    # 7.重定向到首页
    return redirect("/admin/index")

