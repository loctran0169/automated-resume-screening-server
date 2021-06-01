
from app.main.util.custom_fields import NullableFloat
from flask_restx import Namespace, fields, Model
from app.main.dto.base_dto import base
from app.main.util.format_text import format_contract, format_education, format_provinces, format_salary
from app.main.dto.resume_dto import ResumeDTO


class JobPostDto:
    api = Namespace('Job Posts', description='job post related operation')

    job_post = api.model('job_post', {
        'recruiter_email': fields.String(required=True, description='email of hr who post this job'),
        'job_domain_id': fields.Integer(required=True, description='id domain of this post'),
        'description_text': fields.String(required=True, description='job description'),
        'requirement_text': fields.String(required=True, description='job requirement'),
        'benefit_text': fields.String(required=True, description='benefit for candidate'),
        'job_title': fields.String(required=True, description='job title'),
        'contract_type': fields.Integer(required=True, description='type of contract'),
        'min_salary': NullableFloat(required=False, description='minimum salary'),
        'max_salary': NullableFloat(required=False, description='maximum salary'),
        'amount': fields.Integer(required=True, description='amount of candidates is recruiting'),
        'education_level': fields.Integer(required=True, description='education_level of candidates is recruiting'),
        'province_id': fields.String(required=True, description='locations of candidates is recruiting'),
        'deadline': fields.DateTime(required=True, description='last day for candidate to apply'),
    })

    job_post_update = api.model('job_post_update', {
        'job_domain_id': fields.Integer(required=True, description='id domain of this post'),
        'description_text': fields.String(required=True, description='job description'),
        'requirement_text': fields.String(required=True, description='job requirement'),
        'benefit_text': fields.String(required=True, description='benefit for candidate'),
        'job_title': fields.String(required=True, description='job title'),
        'contract_type': fields.Integer(required=True, description='type of contract'),
        'min_salary': NullableFloat(required=False, description='minimum salary'),
        'max_salary': NullableFloat(required=False, description='maximum salary'),
        'amount': fields.Integer(required=True, description='amount of candidates is recruiting'),
        'is_active': fields.Boolean(required=True, description='is allow show'),
        'province_id': fields.String(required=True, description='locations of candidates is recruiting'),
        'deadline': fields.DateTime(required=True, description='last day for candidate to apply'),
    })

    job_list = api.model('job_list', {
        'id': fields.Integer(description='id of job post'),
        'job_title': fields.String(description='job title'),
        'salary': fields.String(description='salary for candidate'),
        'posted_in': fields.DateTime(description='when did this post?'),
        'deadline': fields.DateTime(description='last day for candidate to apply'),
        'total_apply': fields.Integer(description='nums of candidate who applied this post'),
        'new_apply': fields.Integer(description='nums of candidate who applied this post recently'),
        'total_view': fields.Integer(description='nums of candidate who viewed this post'),
    })

    # Response job post for cand
    job_post_for_cand_fields = api.model("job_post_for_cand_fields", {
        'id': fields.Integer,
        'job_title': fields.String,
        'job_domain': fields.String(attribute='job_domain.name'),
        'salary': fields.String(attribute=lambda x: format_salary(x.min_salary, x.max_salary)),
        'posted_in': fields.DateTime(attribute='posted_in'),
        'deadline': fields.DateTime(attribute='deadline'),
        'contract_type': fields.String(attribute=lambda x: format_contract(x.contract_type)),
        'description': fields.String(attribute='description_text'),
        'requirement': fields.String(attribute='requirement_text'),
        'benefit': fields.String(attribute='benefit_text'),
        'amount': fields.String(attribute=lambda x: "Không giới hạn" if x.amount == 0 or x.amount is None else str(x.amount)),
        'company_name': fields.String(attribute=lambda x: x.recruiter.company.name if x.recruiter.company is not None else None),
        'company_logo': fields.String(attribute=lambda x: x.recruiter.company.logo if x.recruiter.company is not None else None),
        'company_background': fields.String(attribute=lambda x: x.recruiter.company.background if x.recruiter.company is not None else None),
        'provinces': fields.List(fields.String, attribute=lambda x: format_provinces(x.province_id)),
        'education': fields.String(attribute=lambda x: format_education(x)),
        'domain_skills': fields.String,
        'soft_skills': fields.String,
        'general_skills': fields.String,
        # 'saved_date': fields.String
    })
    job_post_response_for_cand_fields = api.model("job_post_response_for_cand_fields", {
        'post': fields.Nested(job_post_for_cand_fields),
        'cand_soft_skills': fields.String,
        'cand_technical_skills': fields.String,
        'saved_date': fields.DateTime()
    })
    job_post_for_cand = api.inherit('job_post_for_cand', base, {
        'data': fields.Nested(job_post_response_for_cand_fields)
    })

    job_post_for_edit = api.model("job_post_for_edit", {
        'id': fields.Integer,
        'job_title': fields.String,
        'job_domain': fields.String(attribute='job_domain.name'),
        'job_domain_id': fields.Integer,
        'salary': fields.String(attribute=lambda x: format_salary(x.min_salary, x.max_salary)),
        'min_salary': fields.Float,
        'max_salary': fields.Float,
        'posted_in': fields.DateTime,
        'deadline': fields.DateTime,
        'contract_type': fields.String(attribute=lambda x: format_contract(x.contract_type)),
        'contract_type_id': fields.Integer(attribute='contract_type'),
        'amount': fields.String(attribute=lambda x: "Không giới hạn" if x.amount == 0 or x.amount is None else str(x.amount)),
        'description': fields.String(attribute='description_text'),
        'requirement': fields.String(attribute='requirement_text'),
        'benefit': fields.String(attribute='benefit_text'),
        'total_view': fields.Integer(attribute='total_views'),
        'total_save': fields.Integer(attribute='total_saves'),
        'total_apply': fields.Integer(attribute=lambda x: len(x.job_resume_submissions)),
        'provinces': fields.List(fields.String, attribute=lambda x: x.province_id.split(",")),
        'education': fields.String(attribute=lambda x: format_education(x)),
        'education_level': fields.Integer,
        'domain_skills': fields.String,
        'soft_skills': fields.String,
        'general_skills': fields.String,
    })

    response_jp_for_edit = api.inherit('response_jp_for_edit', base, {
        'data': fields.Nested(job_post_for_edit)
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
    # Response for search job post
    single_job_post_in_search_fields = api.model("single_job_post_in_search_fields", {
        'company_name': fields.String(attribute=lambda x: x.recruiter.company.name if x.recruiter.company is not None else None),
        'company_logo': fields.String(attribute=lambda x: x.recruiter.company.logo if x.recruiter.company is not None else None),
        'company_background': fields.String(attribute=lambda x: x.recruiter.company.background if x.recruiter.company is not None else None),
        'job_title': fields.String,
        'last_edit': fields.DateTime(),
        'salary': fields.String(attribute=lambda x: format_salary(x.min_salary, x.max_salary)),
        'contact_type': fields.String(attribute=lambda x: format_contract(x.contract_type)),
        'province_id': fields.String,
        'job_post_id': fields.Integer(attribute=lambda x: x.id),
        'job_description': fields.String(attribute=lambda x: x.description_text),
        'posted_in': fields.String(attribute=lambda x: x.last_edit),
    })
    single_job_post_in_search_fields_with_company = api.model("single_job_post_in_search_fields_with_company", {
        'company_name': fields.String(attribute=lambda x: x.recruiter.company.name if x.recruiter.company is not None else None),
        'company_logo': fields.String(attribute=lambda x: x.recruiter.company.logo if x.recruiter.company is not None else None),
        'company_background': fields.String(attribute=lambda x: x.recruiter.company.background if x.recruiter.company is not None else None),
        'job_title': fields.String,
        'last_edit': fields.DateTime(),
        'salary': fields.String(attribute=lambda x: format_salary(x.min_salary, x.max_salary)),
        'contact_type': fields.String(attribute=lambda x: format_contract(x.contract_type)),
        'province_id': fields.String,
        'job_post_id': fields.Integer(attribute=lambda x: x.id),
        'job_description': fields.String(attribute=lambda x: x.description_text),
        'posted_in': fields.String(attribute=lambda x: x.last_edit),
    })
    pagination = api.model('pagination', {
        'page': fields.Integer,
        'total': fields.Integer,
    })
    job_post_in_search_cand_response = api.inherit('job_post_in_search_cand_response', base, {
        'data': fields.List(fields.Nested(single_job_post_in_search_fields)),
        'pagination': fields.Nested(pagination)
    })
    job_post_similar_in_search_cand_response = api.inherit('job_post_similar_in_search_cand_response', base, {
        'data': fields.List(fields.Nested(single_job_post_in_search_fields_with_company)),
        'pagination': fields.Nested(pagination)
    })

    max_min_salary = api.inherit('max_min_salary', {
        "max": fields.Integer,
        "min": fields.Integer,
    })
    list_suggest_job = api.inherit('list_suggest_job', {
        "items": fields.List(fields.Nested(single_job_post_in_search_fields_with_company)),
        "province_id": fields.String,
        "totalCount": fields.Integer,
        "salary": fields.Nested(max_min_salary)
    })
    suggest_job = api.inherit('suggest_job', base, {
        'data': fields.Nested(list_suggest_job)
    })

    # Response for update job post from HR
    response_for_update_job_post_from_hr_fields = api.model("response_for_update_job_post_from_hr_fields", {
        'id': fields.Integer,
        'job_title': fields.String,
        'job_domain': fields.String(attribute="job_domain.name"),
        'salary': fields.String(attribute=lambda x: format_salary(x.min_salary, x.max_salary)),
        'posted_in': fields.DateTime(),
        'deadline': fields.DateTime(),
        'last_edit': fields.DateTime(),
        'contract_type': fields.String(attribute=lambda x: format_contract(x.contract_type)),
        'amount': fields.String(attribute=lambda x: "Không giới hạn" if x.amount == 0 or x.amount is None else str(x.amount)),
        'description': fields.String(attribute='description_text'),
        'requirement': fields.String(attribute='requirement_text'),
        'benefit': fields.String(attribute='benefit_text'),
        'total_views': fields.Integer,
        'total_saves': fields.Integer,
        'total_applies': fields.Integer
    })
    response_for_update_job_post_from_hr = api.inherit('response_for_update_job_post_from_HR', base, {
        'data': fields.List(fields.Nested(single_job_post_in_search_fields)),
    })

    ########################################
    # Get matched cand info with job post
    ########################################
    candidate_detail_fields = api.model('candidate_detail_fields', {
        'id': fields.Integer,
        'email': fields.String,
        'password_hash': fields.String,
        'phone': fields.String,
        'full_name': fields.String,
        'gender': fields.Boolean,
        'date_of_birth': fields.DateTime(),
        'status': fields.Integer,
        'province_id': fields.String,
        'access_token': fields.String,
        'registered_on': fields.DateTime(),
        'confirmed': fields.Boolean,
        'confirmed_on': fields.DateTime()
    })
    submission_fields = api.model('submission_fields', {
        'id': fields.Integer,
        'resume_id': fields.Integer,
        'job_post_id': fields.Integer,
        'submit_date': fields.DateTime(),
        'score': fields.Float,
        'process_status': fields.Boolean,
        'score_array': fields.String,
        'score_explanation_array': fields.String
    })
    submission_cand_info_fields = api.model('submission_cand_info_fields', {
        'submission': fields.Nested(submission_fields),
        'candidate': fields.Nested(candidate_detail_fields),
        'resume': fields.Nested(ResumeDTO.resume_detail_fields),
        'scores': fields.Raw,
        'saved_date': fields.DateTime()
    })
    get_cand_info_with_matched_job_post_response = api.inherit('get_cand_info_with_matched_job_post_response', base, {
        'data': fields.Nested(submission_cand_info_fields)
    })

    ###############################
    # Get list applied candidates
    ###############################
    statistics_fields = api.model('statistics_fields', {
        'avg_soft_score': fields.Float,
        'avg_domain_score': fields.Float,
        'avg_general_score': fields.Float,
    })
    applied_cand_fields = api.model('applied_cand_fields', {
        'submission': fields.Nested(submission_fields),
        'candidate': fields.Nested(candidate_detail_fields),
        'resume': fields.Nested(ResumeDTO.resume_detail_fields),
        'scores': fields.Raw,
        'saved': fields.Boolean
    })
    applied_cand_list_response = api.inherit('applied_cand_list_response', base, {
        'data': fields.List(fields.Nested(applied_cand_fields)),
        'pagination': fields.Nested(pagination),
        'statistics': fields.Nested(statistics_fields)
    })

    suggest_list = api.inherit("suggest_list", base, {
        'data': fields.Nested(list_suggest_job),
        'pagination': fields.Nested(pagination)
    })
