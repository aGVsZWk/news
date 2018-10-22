from flask import Blueprint

# 创建管理员蓝图对象
admin_blue = Blueprint("admin",__name__,url_prefix="/admin")

# 装饰视图函数
from . import views