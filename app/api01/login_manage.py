# -*- coding: utf-8 -*-
# @Time    : 10/26/19 1:26 PM
# @Author  : Alex Hu
# @Contact : jthu4alex@163.com
# @FileName: login_manage.py
# @Software: PyCharm
# @Blog    : http://www.gzrobot.net/aboutme
# @version : 0.1.0

from flask_restful import Resource, reqparse, request
import requests
from flask import jsonify, session
from app import STATE_CODE
from weixin import WXAPPAPI
from weixin.lib.wxcrypt import WXBizDataCrypt
from ..models import Patient
from .. import db


APP_ID = 'wx7469bbae33c99a3f'
APP_SECRET = '7ea4c89226d5933d8be87e07a37dc1cc'

wx_api = WXAPPAPI(appid=APP_ID, app_secret=APP_SECRET)


parser = reqparse.RequestParser()
parser.add_argument("code", type=str, location=["form", "json", "args"])
parser.add_argument("iv", type=str, location=["form", "json", "args"])
parser.add_argument("encryptedData", type=str, location=["form", "json", "args"])


class UserLogin(Resource):
    def get(self):
        pass

    def post(self):
        print(request.get_json())
        js_code = parser.parse_args().get('code')
        encrypted_data = parser.parse_args().get('encryptedData')
        iv = parser.parse_args().get('iv')
        if js_code:
            session_info = wx_api.exchange_code_for_session_key(code=js_code)
            if 'unionid' in session_info:
                ## someone has subscribed the Official Account
                unionid_user = session_info['unionid']
                minip_openid = session_info['openid']
                rsl = Patient.query.filter_by(unionid=unionid_user).one()
                if rsl:
                    rsl.minip_openid = minip_openid
                    db.session.commit()
                    session['unionid'] = session_info['unionid']
                else:
                    return STATE_CODE['204']
                # crypt = WXBizDataCrypt(APP_ID, session_info.get('session_key'))
                # user_info = crypt.decrypt(encrypted_data, iv)
                # print('user_info', user_info)
                # unionid = user_info['unionId']
                # session['user_id'] = user_info['unionId']
                # resp = {'unionid': unionid}
                # return jsonify(dict(resp, **STATE_CODE['200']))
            else:
                return STATE_CODE['204']
        else:
            return STATE_CODE['400']
