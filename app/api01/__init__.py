# -*- coding: utf-8 -*-
# @Time    : 10/18/19 10:55 PM
# @Author  : Alex Hu
# @Contact : jthu4alex@163.com
# @FileName: __init__.py.py
# @Software: PyCharm
# @Blog    : http://www.gzrobot.net/aboutme
# @version : 0.0.0

from flask import Blueprint

api_bp = Blueprint('api01', __name__, url_prefix='/api01')  # the 2 arg is Blueprint name and which package the Blueprint belong to


from flask_restful import Api
from .questionnaire_manage import Questionnaires
from .user_manage import User, Medicine
from .login_manage import UserLogin
from .util import Util


api = Api(api_bp)

api.add_resource(Questionnaires, '/questionnaire')
api.add_resource(User, '/user')
api.add_resource(Medicine, '/user/treatment')
api.add_resource(UserLogin, '/wxlogin')
api.add_resource(Util, '/util')
