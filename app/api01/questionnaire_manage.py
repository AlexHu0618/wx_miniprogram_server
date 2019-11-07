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
from ..models import Questionnaire, MapPatientQuestionnaire, Patient, QuestionnaireStruct, Option, ResultShudaifu
import datetime
import time
from sqlalchemy import and_, or_
import re
from .. import db


parser = reqparse.RequestParser()
parser.add_argument("id", type=str, location=["form", "json", "args"])
parser.add_argument("moduleID", type=str, location=["form", "json", "args"])
parser.add_argument("answer", type=str, location=["form", "json", "args"])


class Questionnaires(Resource):
    def get(self):
        qnid = parser.parse_args().get('id')
        unionid = session.get('unionid')
        if qnid:
            mid = int(parser.parse_args().get('moduleID'))
            ## query single questionnaire for one patient
            # rsl_map = MapPatientQuestionnaire.query.join(Patient, MapPatientQuestionnaire.patient_id == Patient.id).filter(
            #     Patient.unionid == unionid, MapPatientQuestionnaire.status == 1,
            #     MapPatientQuestionnaire.questionnaire_id == qnid).one()
            # if rsl_map:
            #     period = rsl_map.current_period
            #     day_now = (datetime.datetime.now() - rsl_map.dt_built).days + 1
            #     print(day_now)
            #     rsl_s = QuestionnaireStruct.query.filter(or_(and_(QuestionnaireStruct.period == period,
            #                                                       QuestionnaireStruct.questionnaire_id == qnid,
            #                                                       QuestionnaireStruct.respondent == 0),
            #                                                  and_(QuestionnaireStruct.questionnaire_id == qnid,
            #                                                       QuestionnaireStruct.period.is_(None),
            #                                                       QuestionnaireStruct.day_start == day_now,
            #                                                       QuestionnaireStruct.respondent == 0))).all()
            #     print(rsl_s)
            rsl_m = QuestionnaireStruct.query.filter_by(id=mid).one()
            if rsl_m:
                qid_str = re.split(',', rsl_m.question_id_list)
                qid_list = list(map(int, qid_str))
                os = Option.query.filter(Option.question_id.in_(qid_list)).order_by(Option.question_id).all()
                if os:
                    print(os)
                    qs_list = []
                    qid_temp = os[0].question_id
                    title_temp = os[0].question.title
                    type_temp = os[0].question.qtype
                    options = []
                    for o in os:
                        if o.question_id == qid_temp:
                            opt_dict = {'id': o.id, 'option': o.content}
                            options.append(opt_dict)
                            continue
                        else:
                            q_dict = {'id': qid_temp, 'title': title_temp, 'type': type_temp, 'options': options}
                            qs_list.append(q_dict)
                            options = []
                            qid_temp = o.question_id
                            title_temp = o.question.title
                            type_temp = o.question.qtype
                            options.append({'id': o.id, 'option': o.content})
                    q_dict_last = {'id': qid_temp, 'title': title_temp, 'type': type_temp, 'options': options}
                    qs_list.append(q_dict_last)
                    resp = {'questions': qs_list}
                    return jsonify(dict(resp, **STATE_CODE['200']))
                else:
                    return STATE_CODE['204']
            else:
                return STATE_CODE['204']
        else:
            ## query all running questionnaire for one patient
            qns = MapPatientQuestionnaire.query.join(Patient, MapPatientQuestionnaire.patient_id == Patient.id).filter(
                Patient.unionid == unionid, MapPatientQuestionnaire.status == 1,
                MapPatientQuestionnaire.need_answer_module.isnot(None)).all()
            qn_list = []
            if qns:
                modules_list = []
                for qn in qns:
                    module_str = re.split(',', qn.need_answer_module)
                    module_list = map(int, module_str)
                    modules_list += module_list
                for m in modules_list:
                    # day_pass = (datetime.datetime.now() - qn.dt_built).days
                    rsl_s = QuestionnaireStruct.query.filter(QuestionnaireStruct.id == m).one()
                    if rsl_s:
                        t = rsl_s.time
                        t_str = str(t.hour) + ':' + str(t.minute)
                        item = {'time': t_str, 'name': rsl_s.questionnaires.title, 'id': rsl_s.questionnaire_id,
                                'moduleID': m}
                        qn_list.append(item)
                    else:
                        continue
                resp = {'today': qn_list}
                return jsonify(dict(resp, **STATE_CODE['200']))
            else:
                resp = {'today': qn_list}
                return jsonify(dict(resp, **STATE_CODE['200']))

    def post(self):
        ## here just for SDF, it will be different for the others
        args = request.get_json()
        qnid = args['id']
        mid = args['moduleID']
        answer_list = args['answer']
        unionid = session.get('unionid')
        rsl_qn = Questionnaire.query.filter_by(id=qnid).one()
        rsl_p = Patient.query.filter_by(unionid=unionid).one()
        if rsl_qn and rsl_p:
            pid = rsl_p.id
            if answer_list:
                update_mpqn = {}
                for a in answer_list:
                    score = 0
                    qid = a['questionID']
                    if a['type'] == 1:  # single choice
                        oid = int(a['answer'])
                        o = Option.query.filter_by(id=oid).one()
                        if o:
                            score = o.score
                            ## handle the special status
                            if o.id == 1397:
                                ## stop push
                                update_mpqn['status'] = 3
                            if o.id == 1398:
                                s = QuestionnaireStruct.query.filter_by(id=o.goto).one()
                                if s:
                                    update_mpqn['current_period'] = s.period
                                    update_mpqn['days_remained'] = s.day_end - s.day_start + 2  ## 由于每天答题后的0点会减去1天，所以此处为2
                                    update_mpqn['interval'] = s.interval
                                else:
                                    return STATE_CODE['203']
                        else:
                            return STATE_CODE['203']
                        r = ResultShudaifu(patient_id=pid, question_id=a['questionID'], answer=a['answer'], type=a['type'],
                                           is_doctor=0, score=score, dt_answer=datetime.datetime.now())
                        db.session.add(r)
                    elif a['type'] == 3:  # gap filling
                        opt = Option(question_id=qid, content=a['answer'])
                        rsl_id = opt.save()
                        if rsl_id:
                            rsl_oid = Option.query.filter_by(question_id=qid, content=a['answer']).order_by(Option.id.desc()).first()
                            if rsl_oid:
                                rsl_sdf = ResultShudaifu(patient_id=pid, answer=rsl_oid.id, is_doctor=0, type=3,
                                                         dt_answer=datetime.datetime.now(), question_id=qid, )
                                db.session.add(rsl_sdf)
                            else:
                                return STATE_CODE['203']
                        else:
                            return STATE_CODE['203']
                    else:
                        pass
                    continue
                try:
                    mpqn = MapPatientQuestionnaire.query.filter_by(patient_id=pid, questionnaire_id=qnid).one()
                    if mpqn:
                        temp = re.split(',', mpqn.need_answer_module)
                        temp.remove(str(mid))
                        mpqn.need_answer_module = temp
                    else:
                        return STATE_CODE['203']
                    if update_mpqn:
                        MapPatientQuestionnaire.query.filter_by(patient_id=pid, questionnaire_id=qnid).update(update_mpqn)
                    db.session.commit()
                    return STATE_CODE['200']
                except Exception as e:
                    db.session.rollback()
                    print(e)
                    return STATE_CODE['203']
            else:
                return STATE_CODE['400']
        else:
            return STATE_CODE['204']


