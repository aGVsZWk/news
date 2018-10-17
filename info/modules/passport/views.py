import random
import re

from flask import current_app, make_response, jsonify
from flask import json

from flask import request
from flask import session

from info.models import User
from info import redis_store, constants, db
from info.utils.response_code import RET
from . import passport_blue
from info.utils.captcha.captcha import captcha




# 功能描述：退出登陆
# 请求路径: /passport/logout
# 请求方式: POST
# 请求参数: 无
# 返回值: errno, errmsg
@passport_blue.route("/logout",methods=["POST"])
def logout():
    # 1.清除session
    session.pop("user_id",None)
    session.pop("nick_name",None)
    session.pop("mobile",None)

    # 2.返回响应
    return jsonify(errno=RET.OK,errmsg="退出成功")






#功能描述: 登陆用户
# 请求路径: /passport/login
# 请求方式: POST
# 请求参数: mobile,password
# 返回值: errno, errmsg
@passport_blue.route("/login",methods=["POST"])
def login():
    """
    1.获取参数
    2.校验参数,为空校验
    3.根据手机号,查询用户对象
    4.判断用户对象是否存在
    5.判断密码是否正确
    6.将用的登陆信息,保存到session
    7.返回响应
    :return:
    """
    # 1.获取参数
    mobile = request.json.get("mobile")
    password = request.json.get("password")

    # 2.校验参数，为空校验
    if not all([mobile,password]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不完整")

    # 3.根据手机号，查询用户对象
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="用户查询失败")

    # 4.判断用户是否存在
    if not user:
        return jsonify(errno=RET.NODATA,errmsg="该用户不存在")

    # 5.判断密码是否正确
    if not user.check_passowrd(password):

        # current_app.logger.error(user.check_passowrd(password))
        # current_app.logger.error(password)
        return jsonify(errno=RET.DATAERR,errmsg="密码错误")

    # 6.将用户的登陆信息，保存到session
    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile

    # 7.返回响应
    return jsonify(errno=RET.OK,errmsg="登陆成功")








#功能描述: 注册用户
# 请求路径: /passport/register
# 请求方式: POST
# 请求参数: mobile, sms_code,password
# 返回值: errno, errmsg

@passport_blue.route("/register",methods=["POST"])
def register():
    """
     1.获取参数
     2.校验参数,为空校验
     3.手机号格式校验
     4.通过手机号取出redis中的短信验证码
     5.判断短信验证码是否过期
     6.删除redis中的短信验证码
     7.校验传入的短信验证码和,redis中的是否相等
     8.创建用户对象,设置属性
     9.保存用户到数据库
     10.返回响应
     :return:
     """
    # 1.获取参数
    # json_data = request.data
    # dict_data = json.loads(json_data)

    # 上面两句话可以写成一句话
    # dict_data = request.get_json() #等价于 request.json

    dict_data = request.get_json()
    mobile = dict_data.get("mobile")
    sms_code = dict_data.get("sms_code")
    password = dict_data.get("password")

    # 2.校验参数
    if not all([mobile,sms_code,passport_blue]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不完整")

    # 3.校验手机号格式
    if not re.match("1[3456789]\d{9}", mobile):
        return jsonify(errno=RET.DATAERR, errmsg="手机号格式错误")


    # 4.通过手机号取出redis中的短信验证码
    try:
        redis_sms_code = redis_store.get("smg_code:%s"%mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取短信验证码过期")

    # 5.判断短信验证码是否过期
    if not redis_sms_code:
        return jsonify(errno=RET.NODATA,errmsg="短信验证码过期")


    # 6.删除redis中的短信验证码
    try:
        redis_store.delete("smg_code:%s"%mobile)
    except Exception as e:
        return jsonify(errno=RET.NODATA, errmsg="删除短信验证码异常")


    # 7.校验传入的短信验证码和redis中短信验证码是否相等
    if sms_code != redis_sms_code:
        return jsonify(errno=RET.DATAERR,errmsg="短信验证码填写错误")



    # 8.创建用户对象，设置属性
    user = User()
    user.nick_name = mobile
    user.password = password

    user.mobile = mobile

    # 9.保存用户数据到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg="用户注册失败")
    return jsonify(errno=RET.OK,errmsg="注册成功")









# 功能：获取短信验证码
# 请求路径：/passort/sms_code
# 请求方式：POST
# 请求参数：mobile,image_code,image_code_id
# 返回值：errno,errmsg

@passport_blue.route('/sms_code',methods=['POST'])
def sms_code():
    """
    1.获取参数
    2.校验参数，为空校验
    3.校验手机号格式
    4.根据传入的图片验证码编号获取redis中的图片验证码A
    5.判断图片验证码A,是否过期
    6.删除redis中图片验证码A
    7.判断传入的验证码B,和redis中传入的验证码是否相等
    8.生成短信验证码
    9.调用CCP发送，并判断
    10.将短信验证码保存一份到redis
    11.返回响应

    """""

    # 1.获取参数

    json_data = request.data
    dict_data = json.loads(json_data)
    mobile = dict_data.get("mobile")
    image_code = dict_data.get("image_code")

    image_code_id = dict_data.get("image_code_id")
    # 2.校验参数，为空校验
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不能为空")
    # 3.校验手机号格式
    if not re.match("1[3456789]\d{9}",mobile):
        return jsonify(errno=RET.DATAERR, errmsg="手机号格式错误")
    # 4.根据传入的图片验证码编号获取redis中的图片验证码A
    try:
        redis_image_code = redis_store.get("image_code:%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取图片验证码失败")
    # 5.判断图片验证码A,是否过期
    if not redis_image_code:
        return jsonify(errno=RET.NODATA,errmsg="图片验证码已经过期")
    # 6.删除redis中图片验证码A
    try:
        redis_store.delete("image_code:%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="删除图片验证码失败")

    # 7.判断传入的验证码B,和redis中传入的验证码是否相等
    if image_code.lower() != redis_image_code.lower():
        return jsonify(errno=RET.DATAERR,errmsg="图片验证码填写错误")
    # 8.生成短信验证码
    # sms_code = "%06d"%random.randint(0,999999)
    sms_code = 888888
    # 9.调用CCP发送，并判断

    result = 0
    # if result == -1:
    #     return jsonify(errno=RET.DATAERR,errmsg="短信发送失败")

    # 10.将短信验证码保存一份到redis
    try:
        redis_store.set("smg_code:%s"%mobile,sms_code,constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBEER,errmsg="短信保存异常")
    # 11.返回响应
    return jsonify(errno=RET.OK,errmsg="短信发送成功")





# 功能:获取图片验证码
# 请求地址: /passport/image_code
# 请求方式: GET
# 请求参数: cur_id, pre_id
# 返回值: 图片验证码

@passport_blue.route("/image_code")
def image_code():
    """
        1.获取请求参数
        2.参数的校验
        3.生成图片验证码
        4.判断是否有上个图片验证码编号
        5.保存一份到redis
        6.返回图片验证码
        :return:
        """
    # 1.获取请求参数
    cur_id = request.args.get("cur_id")
    pre_id = request.args.get("pre_id")

    # 2.参数的校验
    if not cur_id:
        return "必须要传递验证码编号"

    # 3.生产图片验证码
    name, text, image_data = captcha.generate_captcha()

    # 4.判断是否有上个图片验证码编号
    try:
        if pre_id:
            redis_store.delete("image_code:%s" % pre_id)

        # 5.保存一份到redis
        redis_store.set("image_code:%s" % cur_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.log(e)
        return "redis操作图片失败"

    # 6.返回图片验证码
    response = make_response(image_data)
    response.headers["Content-Type"] = "image/jpg"
    return response
