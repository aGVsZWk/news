from datetime import datetime
import time
from flask import current_app
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session

from info.models import User
from info.utils.commons import user_login_data
from . import admin_blue


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
    # 5.携带数据，渲染页面
    data = {
        "total_count":total_count,
        "month_count":month_count,
        "day_count":day_count
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

