"""
项目的初始化配置信息:
项目的初始化配置信息:

1.数据库配置

2.redis配置

3.csrf配置，对‘POST’，‘PUT’，‘PATCH’，‘DELETE’请求方式做保护

4.session配置,为了后续登陆保持,做铺垫

5.日志信息配置

6.数据库迁移配置
"""""


from info import create_app,db,models
from flask_script import Manager
from flask_migrate import MigrateCommand,Migrate

app = create_app("develop")

# 创建Manager对象，关联app
manager = Manager(app)

# 使用Migrate，关联app,db
Migrate(app,db)

manager.add_command("db",MigrateCommand)


if __name__ == '__main__':
    # db.drop_all()
    # db.create_all()
    manager.run()