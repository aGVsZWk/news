from flask import Flask, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf import CSRFProtect

from config import config_dict


def create_app(config_name):
    app = Flask(__name__)

    config = config_dict.get(config_name)

    app.config.from_object(config)

    # 创建SQLAlchemy对象，关联app
    db = SQLAlchemy(app)

    # 创建redis对象
    redis_store = redis.StrictRedis(host=config.REIDS_HOST, port=config.REDIS_PORT, decode_responses=True)

    CSRFProtect(app)

    Session(app)

    return app
