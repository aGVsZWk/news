from flask import g,redirect,render_template
from flask import request

from info.utils.commons import user_login_data
from . import user_blue

# 功能描述：展示基本资料信息
# 请求描述：/user/base_info
# 请求方式：GER,POST
# 请求参数：POST请求参数，nick_name.signature,gender
# 返回值：errno,errmsg
@user_blue.route('/base_info', methods=['GET', 'POST'])
@user_login_data
def base_info():
    # 1.判断如果是GET,携带用户数据，渲染页面
    if request.method == "GET":
        return render_template("news/user_base_info.html",user=g.user.to_dict())
    # 2.如果是POST请求，获取参数
    pass







# 功能: 获取用户个人中心页面
# 请求路径: /user/info
# 请求方式:GET
# 请求参数:无
# 返回值: user.html页面,用户字典data数据
@user_blue.route('/info')
@user_login_data
def user_info():
    # 判断用户是否有登陆
    if not g.user:
        return redirect("/")

    # 拼接数据，渲染页面
    data = {
        "user_info":g.user.to_dict()

    }
    return render_template("news/user.html",data=data)