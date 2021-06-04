from app.main.service.candidate_service import is_have_resume
from app.main.util.format_text import format_edit_time
from flask_restx import Namespace, fields

from app.main.model.company_model import CompanyModel
from app.main.dto.base_dto import base
from app.main.dto.resume_dto import ResumeDTO
from app.main.dto.job_post_dto import JobPostDto

class ProvinceDto:
    api = Namespace(
        'Province', description='Province related operations')

class DataDto:
    api = Namespace(
        'Data', description='data related operations')
class CompanyDto:
    api = Namespace(
        'Company', description='company related operations')
    company = api.model('company', {
        'name': fields.String(required=True, description='company name'),
        'location': fields.String(required=True, description='company location'),
        'phone': fields.String(required=True, description='company phone number'),
        'email': fields.String(required=True, description='company email'),
        'logo': fields.String(required=False, description='company logo'),
        'background': fields.String(required=False, description='company background'),
        'website': fields.String(required=True, description='company website'),
        'description': fields.String(required=True, description='company description'),
    })
class SkillDto:
    api = Namespace(
        'Skill', description='skill related operations')
    skill = api.model('skill', {
        'name': fields.String(required=True, description='company name')
    })

class CandidateDto:
    api = Namespace(
        'Candidate', description='candidate related operations')
    candidate = api.model('candidate_register', {
        'email': fields.String(required=True, description='user email address'),
        'password': fields.String(required=True, description='user password'),
        'fullName': fields.String(required=True, description='user full name'),
        'phone': fields.String(required=True, description='user phone'),
        'gender': fields.Boolean(required=True, description='user gender'),
        'dateOfBirth': fields.DateTime(required=True, description='candidate birthday'),
        'province_id': fields.String(required=True, description='candidate location'),
    })
    profile_update = api.model('profile_update', {
        'fullName': fields.String(required=True, description='user full name'),
        'phone': fields.String(required=True, description='user phone'),
        'gender': fields.Boolean(required=True, description='user gender'),
        'dateOfBirth': fields.String(attribute=lambda x: x.date_of_birth.strftime("%Y-%m-%d")),
        'provinceId': fields.String(required=True , description='province_id'),
    })
    account = api.model('account', {
        'email': fields.String(required=True, description='user email address'),
        'password': fields.String(required=True, description='user password'),
    })

    response_resume = api.model('response_resume', {
        'id': fields.Integer,
        'months_of_experience': fields.Integer,
        'soft_skills': fields.String,
        'technical_skills': fields.List(fields.String, attribute=lambda x: x.technical_skills.split("|")),
        'store_url': fields.String,
        'resume_filename': fields.String,
        'resume_file_extension': fields.String,
        'download_url': fields.String,
        'educations': fields.String,
        'experiences': fields.String,
        'job_domain_id': fields.Integer,
        'edit': fields.DateTime(attribute='last_edit'),
        'created_on': fields.DateTime(attribute='created_on')
    })

    response_profile = api.model('response_profile', {
        'id': fields.Integer,
        'email': fields.String,
        'phone': fields.String,
        'fullName': fields.String(attribute='full_name'),
        'dateOfBirth': fields.String(attribute=lambda x: x.date_of_birth.strftime("%d/%m/%Y")),
        'gender': fields.Boolean,
        'status': fields.Boolean,
        'provinceId': fields.String(attribute='province_id'),
        'registeredOn': fields.String(attribute=lambda x: x.registered_on.strftime("%H:%M - %d/%m/%Y")),
        'isHaveResume': fields.Boolean(attribute=lambda x: is_have_resume(x.resumes)),
        'resumes': fields.Nested(response_resume)
    })

    candidate_profile = api.inherit('candidate_profile', base, {
        'data': fields.Nested(response_profile)
    })

    ########################
    # Candidate detail model
    ########################
    candidate_detail_fields = api.model('candidate_detail_fields', {
        'id': fields.Integer(attribute="cand.id"),
        'email': fields.String(attribute="cand.email"),
        'password_hash': fields.String(attribute="cand.password_hash"),
        'phone': fields.String(attribute="cand.phone"),
        'full_name': fields.String(attribute="cand.full_name"),
        'gender': fields.Boolean(attribute="cand.gender"),
        'date_of_birth': fields.DateTime(attribute="cand.date_of_birth"),
        'status': fields.Integer(attribute="cand.status"),
        'province_id': fields.String(attribute="cand.province_id"),
        'access_token': fields.String(attribute="cand.access_token"),
        'registered_on': fields.DateTime(attribute="cand.registered_on"),
        'confirmed': fields.Boolean(attribute="cand.confirmed"),
        'confirmed_on': fields.DateTime(attribute="cand.confirmed_on"),
        'resumes': fields.List(fields.Nested(ResumeDTO.resume_detail_fields), attribute="cand.resumes"),
        'saved_date': fields.DateTime()
    })
    candidate_detail_response = api.inherit('candidate_detail_response', base, {
        'data': fields.Nested(candidate_detail_fields)
    })

    ####################
    # Get saved job posts
    ####################
    saved_job_post_fields = api.model("saved_job_post_fields", {
        'id': fields.Integer, 
        'recruiter_id': fields.Integer, 
        'resume_id': fields.Integer, 
        'created_on': fields.DateTime(),
        'job_post': fields.Nested(JobPostDto.job_post_for_cand_fields),
        'saved_date': fields.DateTime(),
    })
    pagination = api.model('pagination', {
        'page': fields.Integer,
        'total': fields.Integer,
    })
    get_saved_job_post_list_response = api.inherit('get_saved_job_post_list_response', base, {
        'data': fields.List(fields.Nested(saved_job_post_fields)),
        'pagination': fields.Nested(pagination)
    })

    ########################
    # Get applied job posts
    ########################
    applied_job_post_fields = api.model("applied_job_post_fields", {
        'id': fields.Integer,
        'resume_id': fields.Integer,
        'job_post_id': fields.Integer,
        'submit_date': fields.DateTime(),
        'job_post': fields.Nested(JobPostDto.job_post_for_cand_fields),
    })
    get_applied_job_post_list_response = api.inherit('get_applied_job_post_list_response', base, {
        'data': fields.List(fields.Nested(applied_job_post_fields)),
        'pagination': fields.Nested(pagination)
    })

    ########################
    # Get uploaded resumes
    ########################
    single_resume = api.model("single_resume", {
        'id': fields.Integer,
        'resume_filename': fields.String,
        'resume_file_extension': fields.String,
        'store_url': fields.String
    })
    resume_list = api.inherit('resume_list', base, {
        'data': fields.List(fields.Nested(single_resume)),
    })


class RecruiterDto:
    api = Namespace(
        'Recruiter', description='Recruiter related operations')
    recruiter = api.model('recruiter', {
        'email': fields.String(required=True, description='user email address'),
        'password': fields.String(required=True, description='user password'),
        'fullName': fields.String(required=True, description='user full name'),
        'phone': fields.String(required=True, description='user phone'),
        'gender': fields.Boolean(required=True, description='user gender'),
    })
    account = api.model('account', {
        'email': fields.String(required=True, description='user email address'),
        'password': fields.String(required=True, description='user password'),
    })

    company_job = api.model('company_job', {
        'name': fields.String(required=True, description='company name'),
        'location': fields.String(required=True, description='company location'),
        'phone': fields.String(required=True, description='company phone number'),
        'email': fields.String(required=True, description='company email'),
        'logo': fields.String(required=False, description='company logo'),
        'background': fields.String(required=False, description='company background'),
        'website': fields.String(required=True, description='company website'),
        'description': fields.String(required=True, description='company description'),
    })
    ####################
    # Get saved resumes
    ####################
    resume_detail_fields = api.model("resume_detail_fields", {
        'id': fields.Integer,
        'months_of_experience': fields.Integer,
        'cand_id': fields.Integer,
        'cand_linkedin': fields.String,
        'cand_github': fields.String,
        'cand_facebook': fields.String,
        'cand_twitter': fields.String,
        'cand_mail': fields.String,
        'cand_phone': fields.String,
        'soft_skills': fields.String,
        'technical_skills': fields.String,
        'store_url': fields.String,
        'download_url': fields.String,
        'is_finding_job': fields.Boolean,
        'resume_filename': fields.String,
        'resume_file_extension': fields.String,
        'total_views': fields.Integer,
        'total_saves': fields.Integer,
        'educations': fields.String,
        'experiences': fields.String,
        'job_domain_id': fields.Integer,

        'job_domain_name': fields.String(attribute='job_domain.name'),
        'cand_name': fields.String(attribute='candidate.full_name'),
        'cand_email': fields.String(attribute='candidate.email'),
        'cand_phone_from_user_input': fields.String(attribute='candidate.phone'),
        'province_id': fields.String(attribute='candidate.province_id'),
        'last_edit': fields.String(attribute=lambda x: format_edit_time(x))
    })
    saved_resume_info_fields = api.model("saved_resume_info_fields", {
        'id': fields.Integer, 
        'recruiter_id': fields.Integer, 
        'resume_id': fields.Integer, 
        'created_on': fields.DateTime(),
        'resume': fields.Nested(resume_detail_fields),
    })
    pagination = api.model('pagination', {
        'page': fields.Integer,
        'total': fields.Integer,
    })
    get_saved_resume_list_response = api.inherit('get_saved_resume_list_response', base, {
        'data': fields.List(fields.Nested(saved_resume_info_fields)),
        'pagination': fields.Nested(pagination)
    })
    

class AccountDto:
    api = Namespace(
        'Account', description='account related operations')

    company = api.model('account_company', {
        'companyName': fields.String(required=True, description='user email address'),
        'companyLocation': fields.String(required=True, description='user email address'),
        'companyPhone': fields.String(required=True, description='user email address'),
        'companyEmail': fields.String(required=True, description='user email address'),
        'companyLogo': fields.String(required=True, description='user email address'),
        'companyWebsite': fields.String(required=True, description='user email address'),
        'companyDescription': fields.String(required=True, description='user email address'),
    })

    candidate = api.model('candidate_company', {
        'dateOfBirth': fields.DateTime(required=True, description='candidate birthday'),
    })

    account = api.model('account', {
        'email': fields.String(required=True, description='user email address'),
        'password': fields.String(required=True, description='user password'),
        'fullName': fields.String(required=True, description='user full name'),
        'phone': fields.String(required=True, description='user phone'),
        'gender': fields.Boolean(required=True, description='user gender'),
        'isCandidate': fields.Boolean(required=True, description='true is candidate, false is recruiter'),
        'company' : fields.Nested(company,allow_null=True),
        'candidate' : fields.Nested(candidate,allow_null=True),
    })
    account_login = api.model('account_login', {
        'email': fields.String(required=True, description='user email address'),
        'password': fields.String(required=True, description='user password'),
    })