from logging import debug

from sqlalchemy.sql.expression import desc
from app.main.model.job_domain_model import JobDomainModel
import json
import sys
sys.path.append("/Users/vinhpham/Desktop/automated-resume-screening-server")
sys.path.append("/Users/vinhpham/Desktop/automated-resume-screening-server/app")
sys.path.append("/Users/vinhpham/Desktop/automated-resume-screening-server/app/main")
sys.path.append("/Users/vinhpham/Desktop/automated-resume-screening-server/app/main/model")

from app.main.model.recruiter_resume_save_model import RecruiterResumeSavesModel
from sys import float_info
from datetime import datetime, timedelta
import dateutil.parser
from flask import json
from app.main import db
from app.main.dto.job_post_dto import JobPostDto
from app.main.model.resume_model import ResumeModel
from app.main.model.job_post_model import JobPostModel
from app.main.model.recruiter_model import RecruiterModel
from app.main.model.candidate_model import CandidateModel
from app.main.model.job_resume_submissions_model import JobResumeSubmissionModel
from app.main.model.job_domain_model import JobDomainModel
from app.main.model.candidate_job_save_model import CandidateJobSavesModel
from random import randint

from flask_jwt_extended.utils import get_jwt_identity
from app.main.util.custom_jwt import HR_only
from app.main.util.format_text import format_contract, format_education
from app.main.util.response import json_serial, response_object
from app.main.util.data_processing import get_technical_skills
from flask_restx import abort
from sqlalchemy import or_
from app.main.util.data_processing import tree_matching_score
from app.main.util.thread_pool import ThreadPool

from app.main.service.job_post_service import add_new_post


def seed_data(db):

    # seed_domain("ios", "/Users/vinhpham/Desktop/automated-resume-screening-server/seeds/jp_ios.json")
    # seed_domain("backend", "seeds/back-end.json")
    # seed_domain("frontend", "seeds/front-end.json")
    # seed_domain("fullstack", "seeds/fullstask.json")
    # seed_domain("android", "seeds/android.json")
    # seed_domain("ai_engineer", "seeds/ai-engineer.json")
    # seed_domain("data_engineer", "seeds/data-engineer.json")
    # seed_domain("devops", "seeds/devops-engineer.json")
    
    

    domains = JobDomainModel.query.all()
    if (len(domains)) == 0:
        with open('seeds/domains.json') as json_file:
            data = json.load(json_file)

            for domain in data:
                d = JobDomainModel(id=domain['id'], name=domain['name'], alternative_name=domain['alternative_name'],logo=domain['logo'],content=domain['content'])
                db.session.add(d)

        db.session.commit()



def seed_domain(domain_key, file):
    d_file = open(file, 'r')
    data_file = json.load(d_file)

    domain = JobDomainModel.query.filter_by(alternative_name=domain_key).first()
    domain_id = domain.id

    for data in data_file:
        contract_type = randint(0, 1)
        amount = randint(1, 3)
        education_level = randint(0, 2)
        benefit = rand_benefits()

        min_salary = randint(8, 15)
        max_salary = min_salary + randint(5, 21)

        if min_salary == 8: min_salary = None
        if max_salary == 36: max_salary = None

        description_text = data["description_text"]
        requirement_text = data["requirement_text"]

        # dess = description_text.split("\n")
        # description_text = "<ul>"+ "".join(["<li>"+d+"</li>" for d in dess]) +"</ul>"

        # reqs = requirement_text.split("\n")
        # requirement_text = "<ul>"+ "".join(["<li>"+d+"</li>" for d in reqs]) +"</ul>"

        post = {
            'job_domain_id': domain_id,
            'description_text': description_text,
            'requirement_text': requirement_text,
            'benefit_text': benefit,
            'job_title': data["job_title"],
            'contract_type': contract_type,
            'amount': amount,
            'education_level': education_level,
            'province_id': "91",
            'recruiter_email': 'rec_email@gmail.com',
            'deadline': '2008-09-03T20:56:35.450686Z',
            'recruiter_id': 1,
            'min_salary': min_salary,
            'max_salary': max_salary
        }
        create_jp(post, domain_key)

    print("Done " + domain_key)

def rand_benefits():
    f = open("/Users/vinhpham/Desktop/automated-resume-screening-server/seeds/benefit.json", 'r')
    data = json.load(f)
    m = len(data) - 1
    return data[randint(0, m)]

def create_jp(post, domain):
    txt = " ".join([post.get('requirement_text', ""), post.get('description_text', "")])

    executor = ThreadPool.instance().executor
    domain_skills_res = executor.submit(get_technical_skills, domain, txt)
    general_skills_res = executor.submit(get_technical_skills, "general", txt)
    soft_skills_res = executor.submit(get_technical_skills, "softskill", txt)

    (domain_skills, _) = domain_skills_res.result()
    (general_skills, _)= general_skills_res.result()
    (soft_skills, _)= soft_skills_res.result()

    new_post = JobPostModel(
        job_domain_id=post['job_domain_id'],
        description_text=post['description_text'],
        requirement_text=post['requirement_text'],
        benefit_text=post['benefit_text'],
        job_title=post['job_title'],
        contract_type=post['contract_type'],
        min_salary=post.get('min_salary'),
        max_salary=post.get('max_salary'),
        amount=post['amount'],
        education_level=post['education_level'],
        province_id=post['province_id'],
        domain_skills='|'.join(domain_skills),
        general_skills='|'.join(general_skills),
        soft_skills='|'.join(soft_skills),
        deadline="2021-05-27 10:44:56",
        recruiter_id=post["recruiter_id"]
    )

    db.session.add(new_post)
    db.session.commit()
    print("Done " + str(new_post.id))