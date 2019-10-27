# -*- coding: utf-8 -*-
# @Time    : 10/18/19 10:55 AM
# @Author  : Alex Hu
# @Contact : jthu4alex@163.com
# @FileName: questionnaire_manage.py
# @Software: PyCharm
# @Blog    : http://www.gzrobot.net/aboutme
# @version : 0.1.0


from flask_restful import Resource, reqparse, request
from flask import jsonify, session
from app import STATE_CODE
from ..models import Questionnaire, MapPatientQuestionnaire, Patient, QuestionnaireStruct
import datetime
import time


parser = reqparse.RequestParser()
parser.add_argument("id", type=str, location=["form", "json", "args"])


class Questionnaires(Resource):
    def get(self):
        qid = parser.parse_args().get('id')
        unionid = session.get('unionid')
        if qid:
            ## query single questionnaire for one patient
            pass
        else:
            ## query all running questionnaire for one patient
            qns = MapPatientQuestionnaire.query.join(Patient, MapPatientQuestionnaire.patient_id == Patient.id).filter(
                Patient.unionid == unionid, MapPatientQuestionnaire.status == 1).all()
            print(qns)
            if qns:
                qn_list = []
                for qn in qns:
                    qn_id = qn.id
                    period = qn.current_period
                    # day_pass = (datetime.datetime.now() - qn.dt_built).days
                    rsl_s = QuestionnaireStruct.query.filter(QuestionnaireStruct.questionnaire_id == qn_id,
                                                             QuestionnaireStruct.period == period).one()
                    if rsl_s:
                        t = rsl_s.time
                        t_str = str(t.hour) + ':' + str(t.minute)
                        item = {'time': t_str, 'name': rsl_s.questionnaires.title, 'id': rsl_s.questionnaire_id}
                        qn_list.append(item)
                    else:
                        continue
                resp = {'today': qn_list}
                return jsonify(dict(resp, **STATE_CODE['200']))
            else:
                return STATE_CODE['204']

    def post(self):
        unionid = session.get('unionid')
