from app.main.model.job_domain_model import JobDomainModel
from app.main.model.candidate_model import CandidateModel
from flask_jwt_extended.utils import get_jwt_identity
from app.main.util.resume_extractor import ResumeExtractor, remove_temp_files
from app.main.util.firebase import Firebase
from app.main.util.thread_pool import ThreadPool
from app.main import db
from app.main.model.resume_model import ResumeModel
from flask_restx import abort
import os


def create_cv(cv_local_path, args, filename, file_ext):
    identity = get_jwt_identity()
    email = identity['email']

    is_pdf = file_ext == 'pdf'

    candidate = CandidateModel.query.filter_by(email=email).first()
    
    executor = ThreadPool.instance().executor
    info_res = executor.submit(ResumeExtractor(cv_local_path, is_pdf).extract)
    blob_res = executor.submit(Firebase().upload, cv_local_path)

    resume_info = info_res.result()
    blob = blob_res.result()

    if os.path.exists(cv_local_path): 
        os.remove(cv_local_path)

    resume = ResumeModel(
        months_of_experience=0,
        cand_id=candidate.id,
        cand_linkedin=resume_info['linkedin'],
        cand_github=resume_info['github'],
        cand_facebook=resume_info['facebook'],
        cand_twitter=resume_info['twitter'],
        cand_mail=resume_info['email'],
        cand_phone=resume_info['phone'],
        soft_skills="|".join(resume_info['soft_skills']),
        technical_skills="|".join(resume_info['tech_skills']),
        store_url=blob.public_url,
        download_url=blob.media_link,
        is_finding_job=False,
        total_views=0,
        total_saves=0,
        educations=resume_info["educations"],
        experiences=resume_info["experiences"],
        resume_filename=filename,
        resume_file_extension=file_ext
    )

    db.session.add(resume)
    db.session.commit()

    return resume


def update_cv(args):
    resume = ResumeModel.query.get(args['resume_id'])
    if not resume:
        abort(404)
    # resume.resume_id = args['resume_id']
    resume.educations = args['educations']
    resume.experiences = args['experiences']
    resume.technical_skills = args['skills']
    resume.months_of_experience = args['months_of_experience']

    db.session.add(resume)
    db.session.commit()

    return resume
    
def delete_cv_by_id(id):
    resume = ResumeModel.query.get(id)
    if not resume:
            abort(400)
    urlCV = resume.store_url
    db.session.delete(resume)
    db.session.commit()

    executor = ThreadPool.instance().executor
    executor.submit(Firebase().delete, urlCV)
