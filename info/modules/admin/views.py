from flask import render_template

from . import admin_blue

# 显示登陆页面
@admin_blue.route("/login")
def admin_login():
    return render_template("admin/login.html")