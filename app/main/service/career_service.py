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
from app.main.model.job_domain_model import JobDomainModel, domain_skills as domain_skills_model
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

def contain_domain(domain_ids):
    res = []
    for id in domain_ids:
        res.append(or_(JobPostModel.job_domain_id==id))
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
        db.session.add(resume)
        db.session.commit()

    except Exception as e:
        print(str(e.args))

    technical_skills = [skill.lower() for skill in data["skills"]]

    domains = JobDomainModel.query.all()
    if not domains or len(domains) == 0:
        return None

    domain_matched = []

    start_time = time_log.time()
    for domain in domains:
        
        max_job = len([job for job in domain.job_posts if job.deadline > datetime.now()])
        max_salary = 0
        min_salary = 0
        if domain.job_posts and len(domain.job_posts) > 0:
            max_salary = domain.job_posts[0].max_salary or 0
            min_salary = domain.job_posts[0].min_salary or 0
            for post in domain.job_posts:
                if post.max_salary and post.max_salary > max_salary:
                    max_salary = post.max_salary
                if post.min_salary and ((post.min_salary < min_salary and post.min_salary != 0) or (min_salary == 0)):
                    min_salary = post.min_salary

        skills = domain.skills
        domain_skills = [skill.name.lower() for skill in skills]
        matched_set_skills = set(technical_skills) & set(domain_skills)
        matched_list_skills = sorted(
            matched_set_skills, key=lambda k: technical_skills.index(k))

        skills_main = [skill for skill in skills if skill.is_main != None and (','+str(domain.id)+',') in skill.is_main]

        domain_matched.append({
            "domain": domain,
            "matchedSkills": matched_list_skills,
            "mainSkills": skills_main,
            "totalCount": max_job,
            "salary": {
                "max": max_salary,
                "min": min_salary
            }
        })
    print("---explore domain skills in %s seconds ---" %
          (time_log.time() - start_time))
    return domain_matched


def match_domains_with_skill(data):

    domains = JobDomainModel.query.all()
    if not domains or len(domains) == 0:
        return None

    start_time = time_log.time()
    domain_matched = []
    domain_ids = []

    for domain in domains:
        
        max_job = len([job for job in domain.job_posts if job.deadline > datetime.now()])
        max_salary = 0
        min_salary = 0
        if domain.job_posts and len(domain.job_posts) > 0:
            max_salary = domain.job_posts[0].max_salary or 0
            min_salary = domain.job_posts[0].min_salary or 0
            for post in domain.job_posts:
                if post.max_salary and post.max_salary > max_salary:
                    max_salary = post.max_salary
                if post.min_salary and ((post.min_salary < min_salary and post.min_salary != 0) or (min_salary == 0)):
                    min_salary = post.min_salary

        domain_skills = [skill.name.lower() for skill in domain.skills]
        is_matched = data['skill'].strip() in domain_skills

        if is_matched:
            domain_ids.append(domain.id)
            domain_matched.append({
                "domain": domain,
                "totalCount": max_job,
                "salary": {
                    "max": max_salary,
                    "min": min_salary
                }
            })

    jobs_in_provinces = []

    if len(domain_matched) > 0:
        query = JobPostModel.query.filter(JobPostModel.closed_in is not None).filter(
            JobPostModel.deadline > datetime.now())
        query = query.filter(or_(*contain_domain(domain_ids)))

        #get hot province
        provinces_ids = []
        for job in query:
                provinces_ids.append(job.province_id)
        
        provinces_str = "|".join(provinces_ids)

        province_job_count = dict()
        for i in range(1,97):
            province_str = str(i).zfill(2)
            count = provinces_str.count(province_str)
            if count > 0:
                province_job_count[province_str] = count
        
        sorted_x = sorted(province_job_count.items(), key=lambda x:x[1],reverse = True)

        provinces_hot_id = []
        
        for hot in sorted_x:
            provinces_hot_id.append(hot[0])

        #all_post top 10
        posts_all = query.filter(or_(JobPostModel.description_text.contains(
                data['skill'].strip()), JobPostModel.requirement_text.contains(data['skill'].strip()))).paginate(1, 5, error_out=False)

        jobs_in_provinces.append({
                "province_id": "00",
                "jobs": posts_all.items
            })

        for pro_id in provinces_hot_id:

            province_query = query.filter(
                JobPostModel.province_id.contains(pro_id))

            posts = province_query.filter(or_(JobPostModel.description_text.contains(
                data['skill'].strip()), JobPostModel.requirement_text.contains(data['skill'].strip()))).paginate(1, 5, error_out=False)

            jobs_in_provinces.append({
                "province_id": pro_id,
                "jobs": posts.items
            })
    print("---explore domain for skill "+str(data['skill'])+" in %s seconds ---" %
          (time_log.time() - start_time))
    return {
        "domain_matched": domain_matched,
        "jobs_in_hot_province": jobs_in_provinces
    }


def domain_description(domain_id):

    start_time = time_log.time()

    domain = JobDomainModel.query.get(domain_id)
    if not domain:
        print("Domain not exist")
        return None
    
    max_salary = 0
    min_salary = 0
    if domain.job_posts and len(domain.job_posts) > 0:
        max_salary = domain.job_posts[0].max_salary or 0
        min_salary = domain.job_posts[0].min_salary or 0
        for post in domain.job_posts:
            if post.max_salary and post.max_salary > max_salary:
                max_salary = post.max_salary
            if post.min_salary and ((post.min_salary < min_salary and post.min_salary != 0) or (min_salary == 0)):
                min_salary = post.min_salary

    skills_main = [skill for skill in domain.skills if skill.is_main != None and (','+str(domain.id)+',') in skill.is_main]

    jobs_in_provinces = []

    query = JobPostModel.query.filter(JobPostModel.closed_in is not None).filter(
        JobPostModel.deadline > datetime.now(), JobPostModel.job_domain_id==domain_id)
    max_job = query.count()

    provinces_ids = []
    for job in query:
            provinces_ids.append(job.province_id)
    
    provinces_str = "|".join(provinces_ids)

    province_job_count = dict()
    for i in range(1,97):
        province_str = str(i).zfill(2)
        count = provinces_str.count(province_str)
        if count > 0:
            province_job_count[province_str] = count
    
    sorted_x = sorted(province_job_count.items(), key=lambda x:x[1],reverse = True)

    provinces_hot_id = []
    
    for hot in sorted_x:
        provinces_hot_id.append(hot[0])

    posts = query\
            .order_by(JobPostModel.last_edit)\
            .paginate(page=1, per_page=10)

    for pro_id in provinces_hot_id:
            
        province_query = query.filter(JobPostModel.province_id.contains(pro_id))
        max_job_province = province_query.count()
        max_salary_province = 0
        min_salary_province = 0
        if province_query and province_query.count() > 0:
            max_salary_province = domain.job_posts[0].max_salary or 0
            min_salary_province = domain.job_posts[0].min_salary or 0
            for post in domain.job_posts:
                if post.max_salary and post.max_salary > max_salary_province:
                    max_salary_province = post.max_salary
                if post.min_salary and ((post.min_salary < min_salary_province and post.min_salary != 0) or (min_salary_province == 0)):
                    min_salary_province = post.min_salary

        jobs_in_provinces.append({
            "province_id": pro_id,
            "totalJobsCount": max_job_province,
            "salary": {
                "max": max_salary_province,
                "min": min_salary_province
            }
        })
    print("---domain description in %s seconds ---" %(time_log.time() - start_time))
    return {
            "domain": domain,
            "mainSkills" : skills_main,
            "totalJobsCount": max_job,
            "lastJobsPost" : posts.items,
            "salary": {
                "max": max_salary,
                "min": min_salary
            },
            "provinceSummary": jobs_in_provinces
        }