from flask import current_app
from flask import redirect
from flask import render_template
from flask import request
from flask import session

from info.models import User
from . import admin_blue

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
    return redirect("http://www.baidu.com")

