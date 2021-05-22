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

post = {
    'job_domain_id': 1,
    'description_text': "Swift",
    'requirement_text': "Python",
    'benefit_text': "Nothing",
    'job_title': "iOS",
    'contract_type': 0,
    'min_salary': 20000,
    'max_salary': 30000,
    'amount': 1,
    'education_level': 0,
    'province_id': "91",
    'recruiter_email': 'rec_email@gmail.com',
    'deadline': '2008-09-03T20:56:35.450686Z'
}


add_new_post(post)