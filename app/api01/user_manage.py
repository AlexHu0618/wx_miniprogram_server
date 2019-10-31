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
from ..models import Patient, MapPatientQuestionnaire, Questionnaire
import datetime

parser = reqparse.RequestParser()
parser.add_argument("name", type=str, location=["form", "json", "args"])
parser.add_argument("sex", type=int, location=["form", "json", "args"])
parser.add_argument("phone", type=str, location=["form", "json", "args"])
parser.add_argument("count", type=int, location=["form", "json", "args"])
parser.add_argument("birthday", type=str, location=["form", "json", "args"])
parser.add_argument("nation", type=str, location=["form", "json", "args"])
parser.add_argument("hospitalID", type=int, location=["form", "json", "args"])
parser.add_argument("subjectID", type=int, location=["form", "json", "args"])
parser.add_argument("doctorID", type=int, location=["form", "json", "args"])
parser.add_argument("treatmentID", type=int, location=["form", "json", "args"])
parser.add_argument("height", type=float, location=["form", "json", "args"])
parser.add_argument("weight", type=float, location=["form", "json", "args"])
parser.add_argument("drinking", type=int, location=["form", "json", "args"])
parser.add_argument("smoking", type=int, location=["form", "json", "args"])


class User(Resource):
    def get(self):
        print(request.headers)
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
        print(request.headers)
        unionid = session.get('unionid')
        phone = parser.parse_args().get('phone')
        if phone:
            ## just modified telephone
            if not phone.isdigit():
                return STATE_CODE['400']
            else:
                try:
                    Patient.query.filter(Patient.unionid == unionid).update({'tel': phone})
                    return STATE_CODE['200']
                except Exception as e:
                    print(e)
                    return STATE_CODE['409']
        else:
            name = parser.parse_args().get('name')
            sex = parser.parse_args().get('sex')
            birthday = parser.parse_args().get('birthday')
            nation = parser.parse_args().get('nation')
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

    # def patch(self):
    #     openid = parser.parse_args().get('openid')
    #     unionid = session.get('unionid')
    #     phone = parser.parse_args().get('phone')
    #     if not phone.isdigit():
    #         return STATE_CODE['400']
    #     else:
    #         try:
    #             Patient.query.filter(Patient.unionid == unionid).update({'tel': phone})
    #             return STATE_CODE['200']
    #         except Exception as e:
    #             return STATE_CODE['409']


class Medicine(Resource):
    def get(self):
        count = parser.parse_args().get('count')
        unionid = session.get('unionid')
        p = Patient.query.filter_by(unionid=unionid).one()
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
                t = {'hospital': r.questionnaire.hospitals.name, 'subject': r.questionnaire.departments.name,
                     'treatment': r.questionnaire.medicines.name, 'id': r.id, 'state': r.status,
                     'cycle': r.questionnaire.total_days, 'current': which_day_on,
                     'start': datetime.datetime.strftime(r.dt_built, '%Y-%m-%d')}
                t_list.append(t)
            resp = {'list': t_list}
            return jsonify(dict(resp, **STATE_CODE['200']))
        else:
            return STATE_CODE['204']

    def post(self):
        print(request.headers)
        unionid = session.get('unionid')
        hospital_id = parser.parse_args().get('hospitalID')
        department_id = parser.parse_args().get('subjectID')
        medicine_id = parser.parse_args().get('treatmentID')
        doctor_id = parser.parse_args().get('doctorID')
        print(hospital_id, department_id, medicine_id)
        height = parser.parse_args().get('height')
        weight = parser.parse_args().get('weight')
        is_drink = parser.parse_args().get('drinking')
        is_smoking = parser.parse_args().get('smoking')
        qn = Questionnaire.query.filter_by(hospital_id=hospital_id, department_id=department_id, medicine_id=medicine_id).one()
        p = Patient.query.filter_by(unionid=unionid).one()
        if qn and p:
            qnid = qn.id
            pid = p.id
            rsl_map = MapPatientQuestionnaire.query.filter_by(patient_id=pid, questionnaire_id=qnid).count()
            if rsl_map:
                ## it is existed
                return STATE_CODE['207']
            else:
                age = datetime.date.today().year - p.birthday.year
                map_p_qn = MapPatientQuestionnaire(patient_id=pid, questionnaire_id=qnid, score=0, status=0,
                                                   dt_built=datetime.datetime.now(), dt_lasttime=datetime.datetime.now(),
                                                   current_period=1, weight=weight, height=height, is_smoking=is_smoking,
                                                   is_drink=is_drink, age=age, is_need_send_task=0, days_remained=10,
                                                   doctor_id=doctor_id)
                rsl = MapPatientQuestionnaire.save(map_p_qn)
                if rsl:
                    return STATE_CODE['200']
                else:
                    return STATE_CODE['203']
        else:
            return STATE_CODE['204']