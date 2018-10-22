from flask import Blueprint

# 创建管理员蓝图对象
from flask import redirect
from flask import request
from flask import session

admin_blue = Blueprint("admin",__name__,url_prefix="/admin")

# 装饰视图函数
from . import views


@admin_blue.before_request
def visit_admin():
    """
    如果不是管理员，必须从/admin/login登陆进入后台管理员界面
    :return:
    """

    if not request.url.endswith("/admin/login"):
        if not session.get("is_admin"):
            return redirect("/")