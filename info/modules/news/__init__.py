from flask import Blueprint

# 创建新闻蓝图对象
news_blue = Blueprint("news",__name__,url_prefix="/news")

from . import views
