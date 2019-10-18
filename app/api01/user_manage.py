# -*- coding: utf-8 -*-
# @Time    : 10/18/19 10:56 AM
# @Author  : Alex Hu
# @Contact : jthu4alex@163.com
# @FileName: user_manage.py
# @Software: PyCharm
# @Blog    : http://www.gzrobot.net/aboutme
# @version : 0.1.0

from flask_restful import Resource, reqparse
from flask import jsonify
from .. import db
from app import STATE_CODE
from ..models import Patient, MapPatientQuestionnaire
import datetime

parser = reqparse.RequestParser()
parser.add_argument("openid", type=str, location=["form", "json", "args"])
parser.add_argument("name", type=str, location=["form", "json", "args"])
parser.add_argument("sex", type=int, location=["form", "json", "args"])
parser.add_argument("phone", type=str, location=["form", "json", "args"])
parser.add_argument("count", type=int, location=["form", "json", "args"])


class User(Resource):
    def get(self):
        openid = parser.parse_args().get('openid')
        rsl_u = Patient.query.filter_by(wechat_openid=openid).first()
        if rsl_u:
            resp = {'name': rsl_u.name, 'sex': rsl_u.sex, 'birthday': rsl_u.birthday, 'nation': rsl_u.nation,
                    'phone': rsl_u.tel}
            return jsonify(dict(resp, **STATE_CODE['200']))
        else:
            return STATE_CODE['204']

    def post(self):
        openid = parser.parse_args().get('openid')
        name = parser.parse_args().get('name')
        sex = parser.parse_args().get('sex')
        birthday = parser.parse_args().get('birthday')
        nation = parser.parse_args().get('nation')
        rsl_u = Patient.query.filter_by(wechat_openid=openid).first()
        if rsl_u:
            rsl_u.name = name
            rsl_u.sex = sex
            rsl_u.birthday = birthday
            rsl_u.nation = nation
            try:
                db.session.commit()
                return STATE_CODE['200']
            except Exception as e:
                db.session.rollback()
                return STATE_CODE['409']
        else:
            return STATE_CODE['204']

    def patch(self):
        openid = parser.parse_args().get('openid')
        phone = parser.parse_args().get('phone')
        if not phone.isdigit():
            return STATE_CODE['400']
        else:
            try:
                Patient.query.filter(Patient.wechat_openid == openid).update({'tel': phone})
                return STATE_CODE['200']
            except Exception as e:
                return STATE_CODE['409']


class Medicine(Resource):
    def get(self):
        openid = parser.parse_args().get('openid')
        count = parser.parse_args().get('count')
        sql = MapPatientQuestionnaire.query().filter(MapPatientQuestionnaire.patient.wechat_openid == openid).order_by(
            MapPatientQuestionnaire.dt_built)
        if count is not None:
            rsl = sql.limit(count).all()
        else:
            rsl = sql.all()
        if rsl:
            t_list = []
            for r in rsl:
                which_day_on = (datetime.datetime.now() - r.dt_built).days
                t = {'hospital': r.doctor.hospital_id, 'subject': r.doctor.department_id,
                        'treatment': r.doctor.medicine, 'cycle': r.questionnaire.total_days,
                        'current': which_day_on, 'start': r.dt_built, 'state': r.register_state, 'id': r.id}
                t_list.append(t)
            resp = {'list': t_list}
            return jsonify(dict(resp, **STATE_CODE['200']))
        else:
            return STATE_CODE['204']
