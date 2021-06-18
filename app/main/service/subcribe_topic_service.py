from email import message

from app.main.service.account_service import get_url_verify_email
from flask.templating import render_template
from app.main.util.data_processing import distance_graph_score, score_skills_grahp, tree_matching_score_jd
from app.main.model.job_post_model import JobPostModel
from app.main.model.job_domain_model import JobDomainModel
from app.main.model.candidate_model import CandidateModel
from app.main.util.response import response_object
from app.main.model.subcribe_topic_mode import SubcribeModel
from app.main import db, send_email
from datetime import datetime, timedelta,date
import time as time_log
from app.main.config import Config as config
import atexit
from flask_apscheduler import APScheduler


def get_subcribe(cand_id):
    subcribe = SubcribeModel.query.filter(SubcribeModel.cand_id==cand_id).first()
    return subcribe

def update_subcribe(cand_id,topic,province_id,_type,status):
    subcribe = SubcribeModel.query.filter(SubcribeModel.cand_id==cand_id).first()
    subcribe.topic = topic
    subcribe.province_id = province_id
    subcribe.type = _type
    subcribe.status = status
    try:
        db.session.add(subcribe)
        db.session.commit()
        return response_object(200, "Update success|Cập nhật thành công", data=subcribe.to_json())
    except Exception as ex:
        return response_object(200, "Update fail|Cập nhậ thất bại", data=None)

def delete_subcribe(cand_id):
    cand = CandidateModel.query.get(cand_id)
    if not cand:
        return response_object(400, "Candidate not found|Không tìm thấy ứng viên", data=None)

    if not cand.subcribe:
        return response_object(200, "Delete success|Xóa thành công", data=None)

    try:
        db.session.delete(cand.subcribe)
        db.session.commit()
        return response_object(200, "Delete success|Xóa thành công", data=None)
    except Exception as ex:
        return response_object(400, "Delete fail|Xóa thất bại", data=None)

def subcribe_email(cand_id, topic,province_id):
    cand = CandidateModel.query.get(cand_id)
    if not cand:
        return response_object(400, "Candidate not exist.|Candidate not exist", data=None)

    if not topic:
        return response_object(400, "You must subcribe not empty topic.|Phải đăng ký vào 1 chủ đề", data=None)

    subcribe = SubcribeModel.query.filter(SubcribeModel.cand_id==cand_id).first()
    if not subcribe:
        subcribe = SubcribeModel(
            cand_id = cand.id,
            topic = topic,
            province_id = province_id,        
        )
    else:
        subcribe.topic = topic
        subcribe.province_id = province_id
    try:
        db.session.add(subcribe)
        db.session.commit()
        return response_object(200, "Register topic search success|Đăng ký thông báo thành công", data=subcribe.to_json())
    except Exception as ex:
        return response_object(200, "Register fail|Đăng ký thông báo thất bại", data=None)

def cacular_score_jobs(jobs,resume,results):
        MIN_SIMILAR = 3.3
        resume_graph_technical_gen = None
        resume_graph_technical_dom = None
        resume_graph_technical_soft = None

        for job in jobs:            
            if  resume_graph_technical_gen == None or resume_graph_technical_dom == None or resume_graph_technical_soft == None:
                match_general = tree_matching_score_jd(job.general_skills.split("|"),
                                    resume.technical_skills,
                                    job.job_domain.alternative_name)

                match_domain = tree_matching_score_jd(job.domain_skills.split("|"),
                                    resume.technical_skills,
                                    job.job_domain.alternative_name)

                match_softskill = tree_matching_score_jd(job.soft_skills.split("|"),
                                    resume.soft_skills,
                                    job.job_domain.alternative_name)

                overall = match_domain['score'] * 2 + match_softskill['score'] * 1 + match_general['score'] * 1


                resume_graph_technical_gen = match_general['post2_graph']
                resume_graph_technical_dom = match_domain['post2_graph']
                resume_graph_technical_soft = match_softskill['post2_graph']
            else:
                general_score = score_skills_grahp(job.general_skills.split("|"),
                                    resume_graph_technical_gen,
                                    job.job_domain.alternative_name)

                domain_score = score_skills_grahp(job.domain_skills.split("|"),
                                    resume_graph_technical_dom,
                                    job.job_domain.alternative_name)

                softskill_score = score_skills_grahp(job.soft_skills.split("|"),
                                    resume_graph_technical_soft,
                                    job.job_domain.alternative_name)     

                overall = domain_score * 2 + softskill_score * 1 + general_score * 1

            if overall >= MIN_SIMILAR:
                results.append(job)

def send_subcribe_mail(candidate,topic, province_id):
    query = JobPostModel.query \
        .filter(JobPostModel.closed_in is not None) \
        .filter(JobPostModel.deadline > datetime.now()) \
        .filter(JobPostModel.posted_in > datetime.now() - timedelta(30)) \
        .order_by(JobPostModel.last_edit.desc())

    key = "%{word}%".format(word=topic)
    query = query.filter(JobPostModel.job_title.ilike(key))

    if province_id and province_id != "":
        query = query.filter(JobPostModel.province_id.contains(province_id))
    jobs = []
    
    start_time = time_log.time()    

    if not candidate.resumes:
        jobs = [i for i in query]
    else:            
        cacular_score_jobs(query,candidate.resumes[0],jobs)
    print("jobs: "+str(len(jobs)))
    if jobs:
        title = "Hi, " + candidate.full_name
        message = "These job ads match find "+str(len(jobs))+" " + topic+" jobs for you."
        html = render_template('robot_suggest.html',title = title, message=message,content = jobs,my_website = config.BASE_URL_FE)
        subject = "AI Machting is hiring for "+topic
        send_email("loctran0169@gmail.com", subject, html)

    print("---send mail topic in %s seconds ---" %(time_log.time() - start_time))
    return None

def func_scheduler():
    print("start scheduler send email")
    subcribes = SubcribeModel.query.filter(SubcribeModel.status==1)
    for subcribe in subcribes:
        if date.today().weekday() != 0 and subcribe.type == 1:
            continue
        try:
            send_subcribe_mail(subcribe.candidate,subcribe.topic,subcribe.province_id)
        except Exception as ex:
            print(str(ex.args))

scheduler = APScheduler()