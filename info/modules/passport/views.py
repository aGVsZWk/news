from flask import request

from info import redis_store,constants
from . import passport_blue
from info.utils.captcha.captcha import captcha


#功能:获取图片验证码
#请求地址: /passport/image_code
#请求方式: GET
#请求参数: cur_id, pre_id
#返回值: 图片验证码

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
        return  "必须要传递验证码编号"

    # 3.生产图片验证码
    name,text,image_data = captcha.generate_captcha()

    # 4.判断是否有上个图片验证码编号
    if pre_id:
        redis_store.delete("image_code:%s"%pre_id)

    # 5.保存一份到redis
    redis_store.set("image_code:%s"%cur_id,text,constants.IMAGE_CODE_REDIS_EXPIRES)

    # 6.返回图片验证码
    return image_data

