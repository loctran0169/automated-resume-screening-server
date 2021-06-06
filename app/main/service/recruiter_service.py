import datetime

from app.main.service.account_service import create_token
from app.main import db
from app.main.model.recruiter_model import RecruiterModel
from app.main.model.resume_model import  ResumeModel
from app.main.model.recruiter_resume_save_model import  RecruiterResumeSavesModel
from flask_restx import abort

def get_a_account_recruiter_by_email(email):
    return RecruiterModel.query.filter_by(email=email).first()

def get_all_recruiter():
    return RecruiterModel.query.all()


def insert_new_account_recruiter(account):
    new_account = RecruiterModel(
        email=account['email'],
        password=account['password'],
        phone = account['phone'],
        full_name = account['fullName'],
        gender = account['gender'],
        access_token=create_token(id = 1 ,email = account['email'], day = 1/24),
        registered_on=datetime.datetime.utcnow()
    )
    db.session.add(new_account)
    db.session.commit()


def delete_a_recruiter_by_email(email):
    recruiter = RecruiterModel.query.filter_by(email=email).first()
    db.session.delete(recruiter)
    db.session.commit()

def get_a_recruiter_by_email(name):
    return RecruiterModel.query.filter_by(name=name).first()

def set_token_recruiter(email, token):
    account = get_a_recruiter_by_email(email)
    account.access_token = token
    db.session.add(account)
    db.session.commit()

def verify_account_recruiter(email):
    account = get_a_account_recruiter_by_email(email)
    account.confirmed = True
    account.confirmed_on = datetime.datetime.utcnow()
    db.session.add(account)
    db.session.commit()



def alter_save_resume(rec_email, args):
    res_id = args['resume_id']
    status = args['status']

    #Check HR
    rec = RecruiterModel.query.filter_by(email=rec_email).first()
    if rec is None: abort(400)
    rec_id = rec.id
    
    # Create 
    if status != 0:
        # Check existence.
        res = ResumeModel.query.get(res_id)
        if res is None: abort(400)

        existed = RecruiterResumeSavesModel.query\
            .filter_by(recruiter_id=rec_id, resume_id=res_id)\
            .first()
        if existed is None:
            existed = RecruiterResumeSavesModel(
                recruiter_id=rec.id,
                resume_id=res_id,
            )
            db.session.add(existed)
            db.session.commit()

        return {
            'id': existed.id,
            'recruiter_id': existed.recruiter_id,
            'resume_id': existed.resume_id
        }

    # Remove
    if status == 0:
        # Check existence.
        remove = RecruiterResumeSavesModel.query\
            .filter_by(recruiter_id=rec_id, resume_id=res_id)\
            .first()
        if remove is None: abort(400, "No saved resume found to remove.")

        db.session.delete(remove)
        db.session.commit()

        return {
            'id': remove.id,
            'recruiter_id': remove.recruiter_id,
            'resume_id': remove.resume_id
        }


def get_saved_resumes(email, args):
    # Check HR
    rec = RecruiterModel.query.filter_by(email=email).first()
    if rec is None: abort(400)
    rec_id = rec.id

    query = RecruiterResumeSavesModel.query.filter(RecruiterResumeSavesModel.recruiter_id == rec_id)

    from_date = args.get('from-date', None)
    if from_date is not None:
        query = query.filter(RecruiterResumeSavesModel.created_on >= from_date)

    to_date = args.get('to-date', None)
    if to_date is not None:
        query = query.filter(RecruiterResumeSavesModel.created_on <= to_date)

    page = args.get('page')
    page_size = args.get('page-size')
    result = query.paginate(page=page, per_page=page_size)

    # get related info
    final_res = []
    for item in result.items:
        i = {}
        i['id'] = item.id
        i['recruiter_id'] = item.recruiter_id
        i['resume_id'] = item.resume_id
        i['created_on'] = item.created_on

        resume = ResumeModel.query.get(item.resume_id)
        i['resume'] =  resume
        final_res.append(i)

    return final_res, {
        'total': result.total,
        'page': result.page
    }