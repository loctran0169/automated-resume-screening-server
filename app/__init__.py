from app.main.util.dto import CandidateDto
from datetime import datetime
from os import error

from flask import Blueprint
from flask.globals import request
from flask_mail import Message
from flask_restx import Api, fields

from app.main.resource.errors import UnauthorizedError

from .main.controller.company_controller import api as company_ns
from .main.controller.account_controller import api as account_ns
from .main.controller.candidate_controller import apiCandidate as candidate_ns
from .main.controller.recruiter_controller import apiRecruiter as recruiter_ns
from .main.controller.job_post_controller import api as job_post_ns
from .main.controller.job_domain_controller import api as job_domain_ns
# from .main.controller.upload_controller import api as upload_ns
from .main.controller.resume_controller import api as resume_ns
from .main.controller.filter_controller import api as filter_ns
from .main.controller.test_controller import api as test_ns
from .main.controller.special_skills_controll import api as skills_ns
from .main.controller.career_controller import api as career_ns
from .main.controller.add_data_controller import api as data_ns
from .main.controller.province_controller import api as province_ns

blueprint = Blueprint('api', __name__, url_prefix="/api", template_folder='templates')


api = Api(blueprint,
          title='API DOCUMENT FOR AUTOMATED RESUME SCREENING',
          version='1.0'
          )

api.add_namespace(test_ns, path='/test')
api.add_namespace(account_ns, path='/user')
api.add_namespace(company_ns, path='/company')
api.add_namespace(candidate_ns, path='/user')
api.add_namespace(recruiter_ns, path='/user')
api.add_namespace(job_post_ns, path='/job-posts')
api.add_namespace(job_domain_ns, path='/job-domains')
# api.add_namespace(upload_ns, path='/upload')
api.add_namespace(resume_ns, path='/resume')
api.add_namespace(filter_ns, path='/filters')
api.add_namespace(skills_ns, path='/skill')
api.add_namespace(career_ns, path='/career')
api.add_namespace(data_ns, path='/data')
api.add_namespace(province_ns, path='/province')

@api.errorhandler(UnauthorizedError)
def handle_custom_exception(error):
    '''Access denied'''
    return {
        "timestamp": datetime.now().strftime("%Y/%m/%d, %H:%M:%S"),
        "status": 403,
        "error": "Forbidden",
        "message": "Access denied",
        "path": request.url
    }, 403
