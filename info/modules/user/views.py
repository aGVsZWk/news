from flask import current_app
from flask import g,redirect,render_template, jsonify
from flask import request

from info import constants, db
from info.models import Category, News, User
from info.utils.commons import user_login_data
from info.utils.image_storage import image_storage
from info.utils.response_code import RET
from . import user_blue


# 功能描述：获取作者新闻列表
# 请求路径：/user/other_news_list
# 请求方式：GET
# 请求参数：p,user_id
# 返回值：errno,errmsg
@user_blue.route('/other_news_list')
def other_news_list():
    """
    1.获取参数
    2.校验参数，作者编号
    3.参数类型转换
    4.分页查询
    5.获取分页对象属性，总页数，当前页，当前页对象列表
    6.对象列表转换成字典列表
    7.携带数据，返回响应
    :return:
    """
    # 1.获取参数
    author_id = request.args.get("user_id")
    page = request.args.get("p","1")

    # 2.校验参数，作者编号
    if not author_id:
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")

    # 3.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        page = 1

    # 3.1根据编号取出作者对象，判断作者对象是否存在
    try:
        author = User.query.get(author_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取用户失败")

    if not author: return jsonify(errno=RET.NODATA,errmsg="作者不存在")

    # 4.分页查询
    try:
        paginate = author.news_list.order_by(News.create_time.desc()).paginate(page,3,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取新闻列表失败")

    # 5.获取分页对象属性，总页数，当前页，当前页对象列表
    total_page = paginate.pages
    current_page = paginate.page
    items = paginate.items

    # 6.对象列表转换成字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_dict())

    # 7.携带数据，返回响应
    data = {
        "total_page":total_page,
        "current_page":current_page,
        "news_list":news_list
    }
    return jsonify(errno=RET.OK,errmsg="获取成功",data=data)




# 功能描述：作者页面信息展示
# 请求路径：/user/other
# 请求方式：GET
# 请求参数：id
# 返回值：渲染other.html页面，字典data数据
@user_blue.route('/other')
@user_login_data
def other_info():
    """
    1.获取参数
    2.校验参数，非空
    3.通过编号查询，并判断作者是否存在
    4.携带作者信息，渲染页面
    :return:
    """
    # 1.获取参数
    author_id = request.args.get("id")

    # 2.校验参数，非空
    if not author_id:
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")

    # 3.通过编号查询，并判断作者是否存在
    try:
        author = User.query.get(author_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="用户查询失败")
    # 3.1 判断当前登陆用户是否有关注过该作者
    is_followed = False
    if g.user:
        if g.user in author.followers:
            is_followed = True

    # 4.携带作者信息，渲染页面
    data = {
        "author":author.to_dict(),
        "user_info":g.user.to_dict() if g.user else "",
        "is_followed":is_followed
    }
    return render_template("news/other.html",data=data)




# 功能描述：获取我的关注
# 请求路径：/user/user_follow
# 请求方式：GET
# 请求参数：p
# 返回值：渲染user_follow.html界面
@user_blue.route('/user_follow')
@user_login_data
def user_follow():
    """
    1.获取参数
    2.参数类型转换
    3.分页查询
    4.或许分页对象属性，总页数，当前页，当前页对象列表
    5.对象列表转成字典列表
    6.携带数据渲染页面
    :return:
    """""
    # 1.获取参数
    # TODO 获取和转换类型开起来不太顺啊
    page = request.args.get("p","1")

    # 2.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        page = 1

    # 3.分页查询
    try:
        paginate = g.user.followed.paginate(page,4,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取新闻列表失败")

    # 4.或许分页对象属性，总页数，当前页，当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5.对象列表转成字典列表
    author_list = []
    for author in items:
        author_list.append(author.to_dict())

    # 6.携带数据渲染页面
    data = {
        "totalPage":totalPage,
        "currentPage":currentPage,
        "author_list":author_list
    }
    return render_template("news/user_follow.html",data=data)




# 功能描述：获取新闻发布列表
#　请求路径：/user/news_list
# 请求方式：GET
# 请求参数：p
# 返回值：GET渲染user_news_list.html页面
@user_blue.route('/news_list')
@user_login_data
def news_list():
    """
    1.获取参数
    2.参数类型转换
    3.分页查询
    4.获取分页对象属性，总页数，当前页，当前页对象列表
    5.对象列表转成字典
    6.携带数据渲染页面
    :return:
    """
    # 1.获取参数
    page = request.args.get("p","1")

    # 2.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DBER,errmsg="获取新闻列表失败")

    # 3.分页查询
    try:
        paginate = News.query.filter(News.user_id == g.user.id).order_by(News.create_time.desc()).paginate(page,3,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取新闻列表失败")

    # 4.获取分页对象属性，总页数，当前页，当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5.对象列表转成字典
    news_list = []
    for news in items:
        news_list.append(news.to_review_dict())

    # 6.携带数据渲染页面
    data = {
        "totalPage":totalPage,
        "currentPage":currentPage,
        "news_list":news_list
    }
    return render_template("news/user_news_list.html",data=data)



# 功能描述：新闻发布
# 请求路径：/user/news_release
# 请求方式：GET,POST
# 请求参数：GET无，POST， title,category_id,digest,index_image,content
# 返回值：GET请求，user_news_release.html，data分类列表字段数据,POST,errno,errmsg
@user_blue.route('/news_release', methods=['GET', 'POST'])
@user_login_data
def news_release():
    """
    1.判断是否是GET请求，携带分类数据展示
    2.如果是POST，获取参数
    3.校验参数，为空校验
    4.判断图片是否上传成功
    5.创建新闻镀锡，设置新闻属性
    6.保存到数据库
    7.返回响应
    :return:
    """
    # 1.判断是否是GET请求，携带分类数据展示
    if request.method == "GET":
        try:
            categories = Category.query.all()
            categories.pop(0)
        except Exception as e:
            current_app.logger(e)
            return jsonify(errno=RET.DBERR,errmsg="获取分类失败")

        # 分类对象列表，转字典列表
        category_list = []
        for category in categories:
            category_list.append(category)

        return render_template("news/user_news_release.html",categories=category_list)

    # 2.如果是POST，获取参数
    title = request.form.get("title")
    category_id = request.form.get("category_id")
    digest = request.form.get("digest")
    index_image = request.files.get("index_image")
    content = request.form.get("content")

    # 3.校验参数，为空校验
    if not all([title,category_id,digest,content,index_image]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")
    # # 上传图片
    try:
        image_name = image_storage(index_image.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="七牛云上传异常")

    # 4.判断图片是否上传成功
    if not image_name:
        return jsonify(errno=RET.NODATA,errmsg="上传失败")

    # 5.创建新闻属性，设置新闻属性
    news = News()
    news.title = title
    news.source = g.user.nick_name
    news.digest = digest
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + image_name
    news.content = content
    news.category_id = category_id
    news.user_id = g.user.id
    news.status = 1 # 表示正审核中

    # 6.保存到数据库
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="新闻发布失败")
    # 7.返回响应
    return jsonify(errno=RET.OK,errmsg="发布成功")




# 功能描述: 获取用户收藏新闻
# 请求路径: /user/ collection
# 请求方式:GET
# 请求参数:p(页数)
# 返回值: user_collection.html页面,携带新闻数据data
@user_blue.route('/collection')
@user_login_data
def collection():
    """
    - 1.获取参数,页数
    - 2.参数类型转换
    - 3.分页查询,获取到分页对象
    - 4.获取分页对象属性,总页数,当前页,当前页对象列表
    - 5.对象列表转成字典列表
    - 6.拼接数据渲染页面
    :return: m
    """
    # - 1.获取参数,页数
    page = request.args.get("p","1")

    # - 2.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        page = 1

    # - 3.分页查询,获取到分页对象
    try:
        paginate = g.user.collection_news.order_by(News.create_time.desc()).paginate(page,10,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取新闻失败")

    # - 4.获取分页对象属性,总页数,当前页,当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # - 5.对象列表转成字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_dict())

    # - 6.拼接数据渲染页面
    data = {
        "totalPage":totalPage,
        "currentPage":currentPage,
        "news_list":news_list
    }
    return render_template("news/user_collection.html",data=data)




# 功能描述：上传图片
# 请求路径：/user/pic_info
# 请求方式：POST,GET
# 请求参数：无，POST有参数，avatar
# 返回值：GET请求，user_pci_info.html页面,data字典数据，POST请求：errno,errmsg,avatar_url
@user_blue.route('/pic_info', methods=['GET', 'POST'])
@user_login_data
def pic_info():
    """
    1.判断请求方式，如果是GET，渲染页面，携带用户数据
    2.如果是POST请求，获取参数
    3.校验参数，为空校验
    4.上传图片
    5.判断是否上传成功
    6.设置图片到用户对象
    7.返回响应，携带图片

    :return:
    """
    # 1.判断请求方式，如果是GET,渲染界面，携带用户数据
    if request.method == "GET":
        return render_template("news/user_pic_info.html",user=g.user.to_dict())

    # 2.如果是POST请求，获取参数
    avatar = request.files.get("avatar")

    # 3.校验参数，为空校验
    if not avatar:
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")

    # 4.上传图片
    try:
        image_name = image_storage(avatar.read())
    except Exception as e:
        # current_app.logger(e)
        return jsonify(errno=RET.THIRDERR,errmsg="七牛云异常")

    # 5.判断是否上传成功
    if not image_name:
        return jsonify(errno=RET.NODATA,errmsg="上传失败")

    # 6.设置图片到用户对象
    g.user.avatar_url = image_name

    # 7.返回响应，携带图片
    data = {
        "avatar":constants.QINIU_DOMIN_PREFIX + image_name
    }
    return jsonify(errno=RET.OK,errmsg="上传成功",data=data)





# 功能描述：密码修改
# 请求路径：/user/pass_info
# 请求方式：GET,POST
# 请求参数：GET无，POST有参数,old_password,new_password
# 返回值：GET请求：user_pass_info.html页面，data字典数据；POST请求：errno,errmsg

@user_blue.route('/pass_info', methods=['GET','POST'])
@user_login_data
def pass_info():
    """
    1.判断请求方式
    2.如果式POST请求，获取参数
    3.为空校验
    4.判断旧密码是否正确
    5.修改新密码
    6.返回响应
    :return:
    """
    # 1.判断请求方式，如果是GET，渲染页面
    if request.method == "GET":
        return render_template("news/user_pass_info.html")
    # 2.如果是POST请求，获取参数
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")

    # 3.为空校验
    if not all([old_password,new_password]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")

    # 4.判断旧密码是否正确
    if not g.user.check_passowrd(old_password):
        return jsonify(errno=RET.DATAERR,errmsg="旧密码错误")
    # 5.修改新密码
    g.user.password = new_password

    # 6.返回响应
    return jsonify(errno=RET.OK,errmsg="修改成功")



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
    # 2.1 获取参数
    nick_name = request.json.get("nick_name")
    signature = request.json.get("signature")
    gender = request.json.get("gender")

    # 2.2 校验参数，为空校验
    if not all([nick_name,signature,gender]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")

    # 2.3 性别类型校验
    if gender not in ["MAN","WOMAN"]:
        return jsonify(errno=RET.DATAERR,errmsg="性别异常")

    # 2.4 修改用户信息
    g.user.signature = signature
    g.user.nick_name = nick_name
    g.user.gender = gender

    # 2.5 返回响应
    return jsonify(errno=RET.OK,errmsg="修改成功")






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