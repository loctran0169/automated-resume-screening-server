from app.main.model.job_post_model import JobPostModel
from app.main.service.account_service import create_token
import datetime
from app.main import db
from app.main.model.candidate_model import CandidateModel
from app.main.model.candidate_job_save_model import CandidateJobSavesModel
from app.main.model.job_resume_submissions_model import JobResumeSubmissionModel
from app.main.model.recruiter_model import RecruiterModel
from app.main.model.recruiter_resume_save_model import RecruiterResumeSavesModel
from flask_restx import abort
from sqlalchemy import or_

def is_have_resume(resumes):
    if not resumes or len(resumes)==0:
        return False
    return True

def get_a_account_candidate_by_email(email):
    return CandidateModel.query.filter_by(email=email).first()

def get_all_candidate():
    return CandidateModel.query.all()

def insert_new_account_candidate(account):
    new_account = CandidateModel(
        email=account['email'],
        password=account['password'],
        phone = account['phone'],
        full_name = account['fullName'],
        gender = account['gender'],
        date_of_birth = account['dateOfBirth'],
        access_token=create_token(id =1,email = account['email'], day = 1/24),
        province_id=account['province_id'],
        registered_on=datetime.datetime.utcnow()
    )
    db.session.add(new_account)
    db.session.commit()

def delete_a_candidate_by_id(id):
    return CandidateModel.query.filter_by(id=id).first()

def set_token_candidate(email, token):
    account = get_a_account_candidate_by_email(email)
    account.access_token = token
    db.session.add(account)
    db.session.commit()

def verify_account_candidate(email):
    account = get_a_account_candidate_by_email(email)
    account.confirmed = True
    account.confirmed_on = datetime.datetime.utcnow()
    db.session.add(account)
    db.session.commit()

def get_candidate_by_id(id, rec_email, resume_id):

    # Check existed rec
    recruiter = RecruiterModel.query.filter_by(email=rec_email).first()
    if recruiter is None: abort(400)

    # Check save date
    saved_date = None
    if resume_id is not None:
        save_record = RecruiterResumeSavesModel.query \
            .filter_by(resume_id=resume_id, recruiter_id=recruiter.id) \
            .first()
        if save_record is not None:
            saved_date = save_record.created_on

    cand = CandidateModel.query.get(id)
    return {
        "cand": cand,
        "saved_date": saved_date
    }

def update_candidate_profile(id,profile):
    candidate = CandidateModel.query.get(id)
    candidate.full_name = profile['fullName']
    candidate.phone = profile['phone']
    candidate.gender = profile['gender']
    candidate.date_of_birth = profile['dateOfBirth']
    candidate.province_id = profile['provinceId']
    db.session.add(candidate)
    db.session.commit()


def alter_save_job(cand_email, args):
    job_post_id = args['job_post_id']
    status = args['status']

    #Check candidate
    cand = CandidateModel.query.filter_by(email=cand_email).first()
    if cand is None: abort(400)
    cand_id = cand.id
    
    # Create 
    if status != 0:
        # Check existence.
        jp = JobPostModel.query.get(job_post_id)
        if jp is None: abort(400)

        existed = CandidateJobSavesModel.query\
            .filter_by(cand_id=cand_id, job_post_id=job_post_id)\
            .first()
        if existed is None:
            existed = CandidateJobSavesModel(
                cand_id=cand_id,
                job_post_id=job_post_id,
            )
            db.session.add(existed)
            db.session.commit()

        return {
            'id': existed.id,
            'cand_id': existed.cand_id,
            'job_post_id': existed.job_post_id
        }

    # Remove
    if status == 0:
        # Check existence.
        remove = CandidateJobSavesModel.query\
            .filter_by(cand_id=cand_id, job_post_id=job_post_id)\
            .first()
        if remove is None: abort(400)

        db.session.delete(remove)
        db.session.commit()

        return {
            'id': remove.id,
            'job_post_id': remove.job_post_id,
            'cand_id': remove.cand_id
        }


def get_saved_job_posts(email, args):
    # Check Cand
    cand = CandidateModel.query.filter_by(email=email).first()
    if cand is None: abort(400)
    cand_id = cand.id

    query = CandidateJobSavesModel.query.filter(CandidateJobSavesModel.cand_id == cand_id)

    from_date = args.get('from-date', None)
    if from_date is not None:
        query = query.filter(CandidateJobSavesModel.created_on >= from_date)

    to_date = args.get('to-date', None)
    if to_date is not None:
        query = query.filter(CandidateJobSavesModel.created_on <= to_date)

    page = args.get('page')
    page_size = args.get('page-size')
    result = query.paginate(page=page, per_page=page_size)

    # get related info
    final_res = []
    for item in result.items:
        i = {}
        i['id'] = item.id
        i['cand_id'] = item.cand_id
        i['job_post_id'] = item.job_post_id
        i['created_on'] = item.created_on
        i['saved_date'] = item.created_on

        job_post = JobPostModel.query.get(item.job_post_id)
        i['job_post'] =  job_post
        final_res.append(i)

    return final_res, {
        'total': result.total,
        'page': result.page
    }


def get_applied_job_posts(email, args):
    # resume_id = args["resume_id"]


    # Check Cand
    cand = CandidateModel.query.filter_by(email=email).first()
    if cand is None: abort(400)

    # Get resumes
    resume_ids = [re.id for re in cand.resumes]

    # Check resume
    # resume = None
    # for r in cand.resumes:
    #     if r.id == resume_id:
    #         resume = r
    # if resume is None:
    #     abort(400, message="No resume with id=" + resume_id + " found.")
    

    query = JobResumeSubmissionModel.query.filter(JobResumeSubmissionModel.resume_id.in_(resume_ids))

    from_date = args.get('from-date', None)
    if from_date is not None:
        query = query.filter(CandidateJobSavesModel.created_on >= from_date)

    to_date = args.get('to-date', None)
    if to_date is not None:
        query = query.filter(CandidateJobSavesModel.created_on <= to_date)

    page = args.get('page')
    page_size = args.get('page-size')
    result = query.paginate(page=page, per_page=page_size)

    # get related info
    final_res = []
    for item in result.items:
        i = {}
        i['id'] = item.id
        i['resume_id'] = item.resume_id
        i['job_post_id'] = item.job_post_id
        i['submit_date'] = item.submit_date
        job_post = JobPostModel.query.get(item.job_post_id)
        i['job_post'] =  job_post
        final_res.append(i)

    return final_res, {
        'total': result.total,
        'page': result.page
    }

def get_candidate_resumes(email):
    hr = CandidateModel.query.filter_by(email=email).first()

    return hr.resumes
