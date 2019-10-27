# -*- coding: utf-8 -*-
# @Time    : 10/18/19 10:56 AM
# @Author  : Alex Hu
# @Contact : jthu4alex@163.com
# @FileName: user_manage.py
# @Software: PyCharm
# @Blog    : http://www.gzrobot.net/aboutme
# @version : 0.1.0

from flask_restful import Resource, reqparse, request
from flask import jsonify, session
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
        user_id = session.get('user_id')
        openid = parser.parse_args().get('openid')
        unionid = session.get('unionid')
        rsl_u = Patient.query.filter_by(unionid=unionid).one()
        if rsl_u:
            resp = {'name': rsl_u.name, 'sex': rsl_u.sex, 'birthday': datetime.datetime.strftime(rsl_u.birthday, '%Y-%m-%d'),
                    'nation': rsl_u.nation, 'phone': rsl_u.tel}
            return jsonify(dict(resp, **STATE_CODE['200']))
        else:
            return STATE_CODE['204']

    def post(self):
        print(request.get_json())
        openid = parser.parse_args().get('openid')
        name = parser.parse_args().get('name')
        sex = parser.parse_args().get('sex')
        birthday = parser.parse_args().get('birthday')
        nation = parser.parse_args().get('nation')
        unionid = session.get('unionid')
        rsl_u = Patient.query.filter_by(unionid=unionid).one()
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
        unionid = session.get('unionid')
        phone = parser.parse_args().get('phone')
        if not phone.isdigit():
            return STATE_CODE['400']
        else:
            try:
                Patient.query.filter(Patient.unionid == unionid).update({'tel': phone})
                return STATE_CODE['200']
            except Exception as e:
                return STATE_CODE['409']


class Medicine(Resource):
    def get(self):
        openid = parser.parse_args().get('openid')
        count = parser.parse_args().get('count')
        unionid = session.get('unionid')
        p = Patient.query.filter_by(unionid=openid).one()
        if p is None:
            return STATE_CODE['204']
        sql = MapPatientQuestionnaire.query.filter(MapPatientQuestionnaire.patient_id == p.id).order_by(
            MapPatientQuestionnaire.dt_built)
        if count is not None:
            rsl = sql.limit(count).all()
        else:
            rsl = sql.all()
        if rsl:
            t_list = []
            for r in rsl:
                which_day_on = (datetime.datetime.now() - r.dt_built).days
                t = {'hospital': r.doctor.hospital_id, 'subject': r.doctor.department_id, 'treatment': r.questionnaire.medicines.name,
                     'cycle': r.questionnaire.total_days, 'current': which_day_on,
                     'start': datetime.datetime.strftime(r.dt_built, '%Y-%m-%d %H:%M:%S'), 'state': r.status, 'id': r.id}
                t_list.append(t)
            resp = {'list': t_list}
            return jsonify(dict(resp, **STATE_CODE['200']))
        else:
            return STATE_CODE['204']
