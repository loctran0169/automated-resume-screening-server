import codecs
import os
import pickle
from app.main.process_data.classify_wrapper.skill_paper import SkillPaper
from sqlalchemy.sql.expression import true
from app.main.model.recruiter_resume_save_model import RecruiterResumeSavesModel
from sys import float_info
from datetime import datetime, timedelta
import time as time_log
import dateutil.parser
from flask import json
import math
from app.main import db
from app.main.dto.job_post_dto import JobPostDto
from app.main.model.resume_model import ResumeModel
from app.main.model.job_post_model import JobPostModel
from app.main.model.recruiter_model import RecruiterModel
from app.main.model.candidate_model import CandidateModel
from app.main.model.job_resume_submissions_model import JobResumeSubmissionModel
from app.main.model.job_domain_model import JobDomainModel
from app.main.model.candidate_job_save_model import CandidateJobSavesModel
from app.main.model.candidate_education_model import CandidateEducationModel

from flask_jwt_extended.utils import get_jwt_identity
from app.main.util.custom_jwt import HR_only
from app.main.util.format_text import format_contract, format_education, format_salary
from app.main.util.response import json_serial, response_object
from app.main.util.data_processing import distance_graph_score, generate_graph_tree_with, get_technical_skills, score_skills_grahp, tree_matching_score_jd
from flask_restx import abort
from sqlalchemy import or_, func, and_
from app.main.util.data_processing import tree_matching_score
from app.main.util.thread_pool import ThreadPool

api = JobPostDto.api


def contain_province(province_ids):
    res = []
    for id in province_ids:
        res.append(and_(JobPostModel.province_id.contains(id)))
    return res


def contain_province_with_one(province_id):
    res = []
    res.append(and_(JobPostModel.province_id.contains(province_id)))
    return res

def add_new_post(post):
    parse_deadline = dateutil.parser.isoparse(post['deadline'])

    recruiter = RecruiterModel.query.filter_by(
        email=post['recruiter_email']).first()
    job_domain = JobDomainModel.query.get(post['job_domain_id'])

    if (not recruiter) | (not job_domain):
        return "Error"

    txt = " ".join([post.get('requirement_text', ""),
                   post.get('description_text', "")])

    executor = ThreadPool.instance().executor
    domain_skills_res = executor.submit(
        get_technical_skills, job_domain.alternative_name, txt)
    general_skills_res = executor.submit(get_technical_skills, "general", txt)
    soft_skills_res = executor.submit(get_technical_skills, "softskill", txt)

    (domain_skills, _) = domain_skills_res.result()
    (general_skills, _) = general_skills_res.result()
    (soft_skills, _) = soft_skills_res.result()

    (domain_skills_graph, _) = generate_graph_tree_with(domain=job_domain.alternative_name, skills=domain_skills)
    (general_skills_graph, _) = generate_graph_tree_with(domain='general', skills=general_skills)
    (soft_skills_graph, _) = generate_graph_tree_with(domain='softskill', skills=soft_skills)

    pickled_domain = codecs.encode(pickle.dumps(domain_skills_graph), "base64").decode()
    pickled_general = codecs.encode(pickle.dumps(general_skills_graph), "base64").decode()
    pickled_softskill = codecs.encode(pickle.dumps(soft_skills_graph), "base64").decode()

    new_post = JobPostModel(
        recruiter_id = recruiter.id,
        job_domain_id=post['job_domain_id'],
        description_text=post['description_text'],
        requirement_text=post['requirement_text'],
        benefit_text=post['benefit_text'],
        job_title=post['job_title'],
        contract_type=post['contract_type'],
        min_salary=post['min_salary'],
        max_salary=post['max_salary'],
        amount=post['amount'],
        education_level=post['education_level'],
        province_id=post['province_id'],
        domain_skills='|'.join(domain_skills).replace("|True|","|").replace("True|","").replace("|True","").replace("True",""),
        general_skills='|'.join(general_skills).replace("|True|","|").replace("True|","").replace("|True","").replace("True",""),
        soft_skills='|'.join(soft_skills).replace("|True|","|").replace("True|","").replace("|True","").replace("True",""),
        deadline=parse_deadline,

        skill_graph=pickled_domain,
        domain_skill_graph=pickled_general,
        soft_skill_graph=pickled_softskill,
    )

    # recruiter.job_posts.append(new_post)
    # job_domain.job_posts.append(new_post)

    # db.session.add(recruiter)
    db.session.add(new_post)

    db.session.commit()

    return response_object(code=200, message="Đăng tin tuyển dụng thành công.", data=new_post.to_json()), 200


@HR_only
def get_hr_posts(page, page_size, sort_values, is_showing):
    identity = get_jwt_identity()
    email = identity['email']
    hr = RecruiterModel.query.filter_by(email=email).first()

    if is_showing:
        posts = JobPostModel.query\
            .filter(JobPostModel.recruiter_id == hr.id)\
            .filter((JobPostModel.deadline >= datetime.now()) & (JobPostModel.closed_in == None))\
            .order_by(*sort_job_list(sort_values))\
            .paginate(page, page_size, error_out=False)
    else:
        posts = JobPostModel.query\
            .filter(JobPostModel.recruiter_id == hr.id)\
            .filter((JobPostModel.deadline < datetime.now()) | (JobPostModel.closed_in != None))\
            .order_by(*sort_job_list(sort_values))\
            .paginate(page, page_size, error_out=False)

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

    pagination = {
        'total': posts.total,
        'page': posts.page
    }

    return response_object(code=200, message="Lấy danh sách thành công", data=res, pagination=pagination)


def sort_job_list(sort_values):
    posted_in = sort_values['posted_in']
    deadline = sort_values['deadline']
    view = sort_values['view']
    apply = sort_values['apply']
    save = sort_values['save']

    res = []

    if posted_in == -1:
        res.append(JobPostModel.posted_in.desc())
    elif posted_in == 1:
        res.append(JobPostModel.posted_in.asc())

    if deadline == -1:
        res.append(JobPostModel.deadline.desc())
    elif deadline == 1:
        res.append(JobPostModel.deadline.asc())

    if view == -1:
        res.append(JobPostModel.total_views.desc())
    elif view == 1:
        res.append(JobPostModel.total_views.asc())

    if apply == -1:
        res.append(JobPostModel.total_applies.desc())
    elif apply == 1:
        res.append(JobPostModel.total_applies.asc())

    if save == -1:
        res.append(JobPostModel.total_saves.desc())
    elif save == 1:
        res.append(JobPostModel.total_saves.asc())

    return res


def count_jobs():
    identity = get_jwt_identity()
    email = identity['email']
    hr = RecruiterModel.query.filter_by(email=email).first()

    is_showing = JobPostModel.query\
        .filter(JobPostModel.recruiter_id == hr.id)\
        .filter((JobPostModel.deadline >= datetime.now()) & (JobPostModel.closed_in == None))\
        .count()

    is_closed = JobPostModel.query\
        .filter(JobPostModel.recruiter_id == hr.id)\
        .filter((JobPostModel.deadline < datetime.now()) | (JobPostModel.closed_in != None))\
        .count()

    return response_object(code=200, message="", data={"is_showing": is_showing, "is_closed": is_closed})


@HR_only
def hr_get_detail(id):
    post = JobPostModel.query.get(id)

    if not post:
        return response_object(code=400, message="Thao tác không hợp lệ")

    return post


def update_jp(id, recruiter_email, args):
    job_post = JobPostModel.query.get(id)
    recruiter = RecruiterModel.query.filter_by(email=recruiter_email).first()
    if job_post == None or\
            recruiter == None or\
            job_post.recruiter_id != recruiter.id:
        abort(400)

    job_domain_id = args.get("job_domain_id", None)
    description_text = args.get("description_text", None)
    requirement_text = args.get("requirement_text", None)
    benefit_text = args.get("benefit_text", None)
    job_title = args.get("job_title", None)
    contract_type = args.get("contract_type", None)
    min_salary = args.get("min_salary", None)
    max_salary = args.get("max_salary", None)
    amount = args.get("amount", None)
    education_level = args.get("education_level", None)
    deadline = args.get("deadline", None)
    province_id = args.get("province_id", None)

    txt = " ".join([description_text, requirement_text])

    executor = ThreadPool.instance().executor
    global is_change_desc
    global is_change_req

    is_change_desc = False
    is_change_req = False
    
    if description_text != job_post.description_text or requirement_text != job_post.requirement_text or is_change_desc == False:
        domain_skills_res = executor.submit(get_technical_skills, job_post.job_domain.alternative_name, txt)
        general_skills_res = executor.submit(get_technical_skills, "general", txt)
        soft_skills_res = executor.submit(get_technical_skills, "softskill", txt)

        (domain_skills, _) = domain_skills_res.result()
        (general_skills, _) = general_skills_res.result()
        (soft_skills, _) = soft_skills_res.result()

        (domain_skills_graph, _) = generate_graph_tree_with(domain=job_post.alternative_name, skills=domain_skills)
        (general_skills_graph, _) = generate_graph_tree_with(domain='general', skills=general_skills)
        (soft_skills_graph, _) = generate_graph_tree_with(domain='softskill', skills=soft_skills)

        pickled_domain = codecs.encode(pickle.dumps(domain_skills_graph), "base64").decode()
        pickled_general = codecs.encode(pickle.dumps(general_skills_graph), "base64").decode()
        pickled_softskill = codecs.encode(pickle.dumps(soft_skills_graph), "base64").decode()

        #update skills
        job_post.domain_skills = '|'.join(domain_skills).replace("|True|","|").replace("True|","").replace("|True","").replace("True","")
        job_post.general_skills = '|'.join(general_skills).replace("|True|","|").replace("True|","").replace("|True","").replace("True","")
        job_post.soft_skills = '|'.join(soft_skills).replace("|True|","|").replace("True|","").replace("|True","").replace("True","")
        
        #update graph
        job_post.skill_graph = pickled_domain
        job_post.domain_skill_graph = pickled_general
        job_post.soft_skill_graph = pickled_softskill

    job_post.job_domain_id = job_domain_id
    job_post.description_text = description_text
    job_post.requirement_text = requirement_text
    job_post.benefit_text = benefit_text
    job_post.job_title = job_title
    job_post.min_salary = min_salary
    job_post.max_salary = max_salary
    job_post.amount = amount
    job_post.is_active = education_level
    job_post.deadline = dateutil.parser.isoparse(deadline)
    job_post.contract_type = contract_type
    job_post.province_id = province_id
    job_post.last_edit = datetime.now()

    db.session.add(job_post)
    db.session.commit()

    return job_post


def close_jp(id, recruiter_email):
    job_post = JobPostModel.query.get(id)
    recruiter = RecruiterModel.query.filter_by(email=recruiter_email).first()
    if job_post == None or\
            recruiter == None or\
            job_post.recruiter_id != recruiter.id:
        abort(400)

    job_post.is_active = False
    job_post.closed_in = datetime.now()

    db.session.add(job_post)
    db.session.commit()
    return job_post


def apply_cv_to_jp(jp_id, args):
    resume_id = args['resume_id']

    if ResumeModel.query.get(resume_id) == None:
        abort(400)

    if JobPostModel.query.get(jp_id) == None:
        abort(400)

    if JobResumeSubmissionModel.query.filter_by(resume_id=resume_id, job_post_id=jp_id).first() is not None:
        return 409

    submission = JobResumeSubmissionModel(
        resume_id=resume_id,
        job_post_id=jp_id,
        is_calculating=True,
    )

    # todo
    calculate_scrore(submission, jp_id, resume_id)

    db.session.add(submission)
    db.session.commit()

    return {
        "id": submission.id,
        "resume_id": submission.resume_id,
        "job_post_id": submission.job_post_id,
        "score_array": submission.score_array,
        "score_explanation_array": submission.score_explanation_array,
        "is_calculating": False
    }

def unapply_cv_to_jd(cand_id,jp_id):
    cand = CandidateModel.query.get(cand_id)
    if not cand:
        return response_object(400, "Candidate not found", data=None)
    if not cand.resumes:
        return response_object(400, "Candidate not resume", data=None)
    
    applies = JobResumeSubmissionModel.query.filter(JobResumeSubmissionModel.job_post_id==jp_id) \
                                    .filter(JobResumeSubmissionModel.resume_id==cand.resumes[0].id)

    for apply in applies:
        db.session.delete(apply)
    db.session.commit()
    return response_object(200, "Unapply success", data=None)

def add_note_apply(cand_id,jp_id,args):
    note = args['note']
    cand = CandidateModel.query.get(cand_id)
    if not cand:
        return response_object(400, "Candidate not found", data=None)
    if not cand.resumes:
        return response_object(400, "Candidate not resume", data=None)
    if not cand.resumes[0].job_resume_submissions:
        return response_object(400, "Candidate not apply jobs", data=None)
    for sub in cand.resumes[0].job_resume_submissions:
        if sub.job_post_id == jp_id:
            sub.note = note
            db.session.add(sub)
            db.session.commit()
            return response_object(200, "Update note success", data=None)
    return response_object(400, "Candidate not apply this job", data=None)

def delete_note_apply(cand_id,jp_id):
    cand = CandidateModel.query.get(cand_id)
    if not cand:
        return response_object(400, "Candidate not found", data=None)
    if not cand.resumes:
        return response_object(400, "Candidate not resume", data=None)
    if not cand.resumes[0].job_resume_submissions:
        return response_object(400, "Candidate not apply jobs", data=None)
    for sub in cand.resumes[0].job_resume_submissions:
        if sub.job_post_id == jp_id:
            db.session.delete(sub)
            db.session.commit()
            return response_object(200, "Delete note success", data=None)
    return response_object(200, "Delete note success", data=None)

def add_note_save(cand_id,jp_id,args):
    note = args['note']
    cand = CandidateModel.query.get(cand_id)
    if not cand:
        return response_object(400, "Candidate not found", data=None)
    if not cand.saved_job_posts:
        return response_object(400, "Candidate not save jobs", data=None)
    for save in cand.saved_job_posts:
        if save.job_post_id == jp_id:
            save.note = note
            db.session.add(save)
            db.session.commit()
            return response_object(200, "Update note success", data=None)
    return response_object(400, "Candidate not save this job", data=None)

def delete_note_save(cand_id,jp_id):
    cand = CandidateModel.query.get(cand_id)
    if not cand:
        return response_object(400, "Candidate not found", data=None)
    if not cand.saved_job_posts:
        return response_object(400, "Candidate not save jobs", data=None)
    for save in cand.saved_job_posts:
        if save.job_post_id == jp_id:
            db.session.delete(save)
            db.session.commit()
            return response_object(200, "Delete note success", data=None)
    return response_object(200, "Delete note success", data=None)

def calculate_scrore(submission, job_post_id, resume_id):

    # Get resume
    job_post = JobPostModel.query.get(job_post_id)
    resume = ResumeModel.query.get(resume_id)

    job_post_text = job_post.description_text + " " + job_post.requirement_text
    resume_text = " ".join([resume.educations, resume.experiences, resume.technical_skills, resume.soft_skills])

    # Scores
    domain_dict = tree_matching_score(job_post_text, resume_text, job_post.job_domain.alternative_name)

    _softskill_score = distance_graph_score(pickle.loads(codecs.decode(job_post.soft_skill_graph.encode(), "base64")),
                                            pickle.loads(codecs.decode(resume.soft_skill_graph.encode(), "base64")))
    _general_score = distance_graph_score(pickle.loads(codecs.decode(job_post.skill_graph.encode(), "base64")),
                                            pickle.loads(codecs.decode(resume.technical_skill_graph.encode(), "base64")))

    domain_score = domain_dict['score']
    softskill_score = _softskill_score
    general_score = _general_score

    score_explanation_array = '|'.join(
        ['domain_score', 'general_score', 'softskill_score'])
    score_array = '|'.join(
        [str(domain_score), str(softskill_score), str(general_score)])

    # Update
    submission.is_calculating = False
    submission.score_array = score_array
    submission.score_explanation_array = score_explanation_array

def get_job_post_for_candidate(jp_id, cand_email):

    # Check if signed in
    cand = None
    if cand_email is not None:
        cand = CandidateModel.query.filter_by(email=cand_email).first()

    save_record = None
    soft_skills = None
    technical_skills = None
    isApplied = False
    if cand is not None:
        save_record = CandidateJobSavesModel \
            .query \
            .filter_by(cand_id=cand.id, job_post_id=jp_id) \
            .first()
        if cand.resumes and len(cand.resumes) != 0:
            soft_skills = cand.resumes[0].soft_skills
            technical_skills = cand.resumes[0].technical_skills
            for apply in cand.resumes[0].job_resume_submissions:
                if apply.job_post_id == jp_id:
                    isApplied = True
    saved_date = None
    if save_record is not None:
        saved_date = save_record.created_on

    post = JobPostModel.query.get(jp_id)
    if not post:
        abort(400)

    post.total_views += 1

    db.session.add(post)
    db.session.commit()

    return {
        'post': post,
        'cand_soft_skills': soft_skills,
        'cand_technical_skills': technical_skills,
        'saved_date': saved_date,
        'is_applied': isApplied
    }

def search_jd_for_cand(args):
    query = JobPostModel.query.filter(JobPostModel.closed_in is not None).filter(
        JobPostModel.deadline > datetime.now()).order_by(JobPostModel.last_edit.desc())

    posted_date = args.get('posted_date')
    contract_type = args.get('contract_type')
    min_salary = args.get('min_salary')
    max_salary = args.get('max_salary')
    page = args.get('page')
    page_size = args.get('page-size')
    keyword = args.get('q')
    province_id = args.get('province_id')
    job_domain_id = args.get('job_domain_id')

    if contract_type is not None:
        query = query.filter(JobPostModel.contract_type == contract_type)

    if min_salary is not None:
        query = query.filter(or_(
            JobPostModel.max_salary == None,
            JobPostModel.max_salary >= min_salary)
        )

    if max_salary is not None:
        query = query.filter(or_(
            JobPostModel.min_salary == None,
            JobPostModel.min_salary >= max_salary)
        )

    if keyword is not None:
        key = "%{word}%".format(word=keyword)
        query = query.filter(JobPostModel.job_title.ilike(key))

    if province_id:
        query = query.filter(JobPostModel.province_id.contains(province_id))

    if job_domain_id is not None:
        query = query.filter(JobPostModel.job_domain_id == job_domain_id)

    if posted_date is not None:
        query = query.filter(
            (datetime.now() - timedelta(days=posted_date)) < JobPostModel.posted_in)

    result = query\
        .order_by(JobPostModel.last_edit)\
        .paginate(page=page, per_page=page_size)

    return result.items, {
        'total': result.total,
        'page': result.page
    }


def delete_job_post(ids):
    for id in ids:
        job = JobPostModel.query.get(id)

        if not job:
            abort(400)

        db.session.delete(job)

    db.session.commit()

    return response_object(message="Xoá tin tuyển dụng thành công")


def proceed_resume(id, recruiter_email, args):
    submission_id = args['submission_id']
    status = args['status']
    job_post = JobPostModel.query.get(id)
    recruiter = RecruiterModel.query.filter_by(email=recruiter_email).first()
    submission = JobResumeSubmissionModel.query.get(submission_id)

    if job_post == None or\
            recruiter == None or\
            submission == None or\
            job_post.recruiter_id != recruiter.id or\
            submission.job_post_id != id:
        abort(400)

    if status != 0 or status != 1:
        abort(400)

    submission.process_status = status
    db.session.commit()
    return submission


def get_matched_cand_info_with_job_post(rec_email, job_id, resume_id):
    # Check existed rec
    recruiter = RecruiterModel.query.filter_by(email=rec_email).first()
    if recruiter is None:
        abort(400)

    # Check job post
    job = JobPostModel.query.get(job_id)
    if job is None:
        abort(400)
    if job.recruiter_id != recruiter.id:
        abort(400)

    resume = ResumeModel.query.get(resume_id)
    if resume is None:
        abort(400)

    cand = CandidateModel.query.get(resume.cand_id)

    # Check submission
    submission = JobResumeSubmissionModel.query \
        .filter_by(resume_id=resume_id, job_post_id=job_id) \
        .first()
    if submission is None:
        abort(400)

    # Check save date
    saved_date = None
    save_record = RecruiterResumeSavesModel.query \
        .filter_by(resume_id=resume_id, recruiter_id=recruiter.id) \
        .first()
    if save_record is not None:
        saved_date = save_record.created_on

    return {
        'submission': submission,
        'candidate': cand,
        'resume': resume,
        'scores': submission.score_dict,
        'saved_date': saved_date
    }


def get_matched_list_cand_info_with_job_post(rec_email, job_id, args):
    # Check existed rec
    recruiter = RecruiterModel.query.filter_by(email=rec_email).first()
    if recruiter is None:
        abort(400, "No recruiter found.")

    # Check job post
    job = JobPostModel.query.get(job_id)
    if job is None:
        abort(400, "No job post found.")
    if job.recruiter_id != recruiter.id:
        abort(400, "The job post is not belong to the recruiter.")

    domain_weight = args['domain_weight']
    general_weight = args['general_weight']
    soft_weight = args['soft_weight']

    page = args['page']
    page_size = args['page-size']

    # if skill_weight + domain_weight != 1: abort(400)

    # Filter
    all_items = JobResumeSubmissionModel.query \
        .filter_by(job_post_id=job.id) \
        .all()

    all_items = sorted(all_items, key=lambda x: x.avg_score(domain_weight=domain_weight,
                                                            soft_weight=soft_weight,
                                                            general_weight=general_weight), reverse=True)

    chunks = [all_items[i:i+page_size]
              for i in range(0, len(all_items), page_size)]
    items = []

    if page > len(chunks):
        items = []
    else:
        items = chunks[page - 1]

    final_res = []
    for submission in items:
        resume = ResumeModel.query.get(submission.resume_id)
        scores = submission.score_dict
        scores['avg'] = submission.avg_score(domain_weight=domain_weight,
                                             soft_weight=soft_weight,
                                             general_weight=general_weight)

        saved = RecruiterResumeSavesModel.query.filter_by(
            recruiter_id=recruiter.id, resume_id=resume.id).first()

        final_res.append({
            'submission': submission,
            'scores': scores,
            'candidate': resume.candidate,
            'resume': resume,
            'saved': True if saved else False
        })

    avg_soft_score = 0
    avg_domain_score = 0
    avg_general_score = 0
    if len(all_items) > 0:
        scores = [sub.score_dict for sub in all_items]
        avg_general_score = sum([s["general_score"]
                                for s in scores]) / len(all_items)
        avg_soft_score = sum([s["softskill_score"]
                             for s in scores]) / len(all_items)
        avg_domain_score = sum([s["domain_score"]
                               for s in scores]) / len(all_items)

    return final_res, {
        'total': len(all_items),
        'page': page
    }, {
        'avg_soft_score': avg_soft_score,
        'avg_domain_score': avg_domain_score,
        'avg_general_score': avg_general_score
    }


def get_similar_job_post_with_id(job_id):
    # Check job post
    job = JobPostModel.query.get(job_id)
    if job is None:
        abort(400)

    query = JobPostModel.query.filter(JobPostModel.closed_in is not None).filter(
        JobPostModel.deadline > datetime.now())

    query = query.filter(JobPostModel.id != job_id)
    query = query.filter(JobPostModel.job_domain_id == job.job_domain_id)
    query = query.filter(and_(*contain_province(job.province_id)))

    result = query\
        .order_by(JobPostModel.last_edit.desc())
    start_time = time_log.time()
    
    _job_result = []
    scores = dict()
    for _job in result:
        score = distance_graph_score(pickle.loads(codecs.decode(job.domain_skill_graph.encode(), "base64")),
                                    pickle.loads(codecs.decode(_job.domain_skill_graph.encode(), "base64")))
        if score > 0.8:
            scores[_job.id] = score
            _job_result.append(_job)
    
    all_items = sorted(_job_result, key=lambda x: scores[x.id], reverse=True)
    _all_items = []
    for index, item in enumerate(all_items):
        if index <=9:
            _all_items.append(item)
        else:
            break
    print("---similar job %s seconds ---" %(time_log.time() - start_time))
    return all_items


def get_suggested_job_posts(email, args):

    # Check Cand
    cand = CandidateModel.query.filter_by(email=email).first()
    if cand is None:
        abort(400)

    province_id = args['province_id']
    if not cand.resumes or len(cand.resumes) == 0 or province_id == "":
        return None, {
            'total': 0,
            'page': 0
        }
    resume  = cand.resumes[0]

    page = args['page']
    page_size = args['page_size']
    domain_id = args['domain_id']

    query = JobPostModel.query.filter(JobPostModel.closed_in is not None).filter(
        JobPostModel.deadline > datetime.now(), JobPostModel.job_domain_id == domain_id)

    max_job = query.count()
    max_salary = db.session.query(func.max(
        JobPostModel.max_salary)).filter(JobPostModel.job_domain_id == domain_id).scalar()

    min_salary = db.session.query(func.max(
        JobPostModel.min_salary)).filter(JobPostModel.job_domain_id == domain_id).scalar()
    
    query = query.filter(JobPostModel.job_domain_id == domain_id)
    query = query.filter(and_(*contain_province_with_one(province_id)))
    all_items = query.all()
    start_time = time_log.time()

    def cacular_score(job,dict, id):                                                                   

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

        dict[id] = overall
        # print(str(id)+" "+str(overall)+" "+str(id)+" "+str(match_general['score'])+" "+str(match_domain['score'])+" "+str(match_softskill['score']))
        return overall

    scores = dict()

    all_items = sorted(all_items, key=lambda x: cacular_score(x,scores,x.id), reverse=True)

    MIN_SIMILAR = 3.3

    all_items = list(filter(lambda x: scores[x.id] >= MIN_SIMILAR, all_items))

    chunks = [all_items[i:i+page_size] for i in range(0, len(all_items), page_size)]

    items = []

    if page > len(chunks):
        items = []
    else:
        items = chunks[page - 1]

    data = {
        'items': items,
        'province_id': province_id,
        'totalCount': max_job,
        'salary': {
            'max': max_salary,
            'min': min_salary
        }
    }
    print("---domain description in %s seconds ---" %(time_log.time() - start_time))
    return data, {
        'page': page,
        'total': len(all_items)
    }