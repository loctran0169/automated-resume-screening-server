from app.main.util.response import json_serial
from app.main.service.job_post_service import contain_province_with_one
from sqlalchemy import or_, and_, not_, extract
from app.main.model.job_post_model import JobPostModel
from app.main.service.special_skills_service import add_new_skill
from os import name
from app.main.model.special_skills_model import SpecialSkillsModel
from app.main.util.data_processing import get_technical_skills
from flask_restx import abort
from app.main.model.candidate_model import CandidateModel
from app.main.model.job_domain_model import JobDomainModel
from app.main.util.thread_pool import ThreadPool
import time as time_log
from app.main import db
import json
from datetime import datetime, timedelta


def contain_provinces_at_least_one(province_ids):
    res = []
    for id in province_ids:
        res.append(and_(JobPostModel.province_id.contains(id)))
    return res


def match_domains_with_cand_skills(email, data):
    cand = CandidateModel.query.filter_by(email=email).first()
    if cand is None:
        abort(400)
    if len(cand.resumes) == 0:
        return None

    if len(data["skills"]) == 0:
        return None
    try:
        resume = cand.resumes[0]
        resume.technical_skills = ("|").join(data["skills"])
        # db.session.add(resume)
        # db.session.commit()

    except Exception as e:
        print(str(e.args))

    technical_skills = (" | ").join(data["skills"])

    domains = JobDomainModel.query.all()
    if not domains or len(domains) == 0:
        return None

    results = []

    start_time = time_log.time()
    for domain in domains:

        max_job = len(domain.job_posts)
        max_salary = 0
        min_salary = 0
        if domain.job_posts and len(domain.job_posts) > 0:
            max_salary = max(domain.job_posts,
                             key=lambda x: x.max_salary or 0).max_salary or 0
            min_salary = min(domain.job_posts,
                             key=lambda x: x.min_salary or 0).min_salary or 0

        domain_skills = [skill.name.lower() for skill in domain.skills]
        matched_set_skills = set(data["skills"]) & set(domain_skills)
        matched_list_skills = sorted(
            matched_set_skills, key=lambda k: data["skills"].index(k))
        # print(len(domain_skills))
        # print(matched_list_skills)
        # executor = ThreadPool.instance().executor
        # domain_skills_res = executor.submit(get_technical_skills, domain.alternative_name, technical_skills)

        # (matched_list_skills, _) = domain_skills_res.result()

        results.append({
            "domain": domain,
            "matchedSkills": matched_list_skills,
            "totalCount": max_job,
            "salary": {
                "max": max_salary,
                "min": min_salary
            }
        })
    print("---explore domain skills in %s seconds ---" %
          (time_log.time() - start_time))
    return results


def match_domains_with_skill(data):

    domains = JobDomainModel.query.all()
    if not domains or len(domains) == 0:
        return None

    results = []
    for domain in domains:

        max_job = len(domain.job_posts)
        max_salary = 0
        min_salary = 0
        if domain.job_posts and len(domain.job_posts) > 0:
            max_salary = max(domain.job_posts,
                             key=lambda x: x.max_salary or 0).max_salary or 0
            min_salary = min(domain.job_posts,
                             key=lambda x: x.min_salary or 0).min_salary or 0

        domain_skills = [skill.name.lower() for skill in domain.skills]
        is_matched = data['skill'].strip() in domain_skills

        if is_matched:
            results.append({
                "domain": domain,
                "totalCount": max_job,
                "salary": {
                    "max": max_salary,
                    "min": min_salary
                }
            })

    provinces_hot_id = ["46", "22", "74", "56", "89", "01", "38", "68"]
    
    jobs_in_provinces = []
    if len(results) > 0:
        query = JobPostModel.query.filter(JobPostModel.closed_in is not None).filter(
            JobPostModel.deadline > datetime.now())
        for pro_id in provinces_hot_id:
        
            province_query = query.filter(JobPostModel.province_id.contains(pro_id))            

            posts = province_query.filter(or_(JobPostModel.description_text.contains(
                data['skill'].strip()), JobPostModel.requirement_text.contains(data['skill'].strip()))).paginate(1, 5, error_out=False)

            res = [{
                'id': post.id,
                'job_title': post.job_title,
                'salary': 'Thoả thuận',
                'posted_in': json.dumps(post.posted_in, default=json_serial),
                'deadline': json.dumps(post.deadline, default=json_serial),
                'total_view': post.total_views,
                'total_save': post.total_saves,
                'total_apply': len(post.job_resume_submissions)
            } for post in posts.items]

    return results
