from app.main.util.custom_fields import NullableFloat
from flask_restx import Namespace, fields, Model
from app.main.dto.base_dto import base
from app.main.util.format_text import format_contract, format_education, format_provinces, format_salary


class CareerDto:

    api = Namespace('Career', description='career related operations')

    skills_str = api.inherit('skills_str', {
        'skills': fields.List(fields.String),
    })

    special_skills = api.inherit('special_skills', {
        'id': fields.Integer,
        'name': fields.String,
        'name_vn': fields.String,
    })

    domain = api.inherit('domain', {
        'id': fields.Integer,
        'name': fields.String,
        'alternative_name': fields.String,
        'logo': fields.String,
        'content': fields.String,
        # 'special_skills': fields.List(fields.Nested(special_skills), attribute=lambda x: x.skills)
    })

    domain_no_special_skills = api.inherit('domain_no_special_skills', {
            'id': fields.Integer,
            'name': fields.String,
            'alternative_name': fields.String,
            'logo': fields.String,
            'content': fields.String,
        })

    max_min_salary = api.inherit('max_min_salary', {
        'max': fields.Integer,
        'min': fields.Integer,
    })

    explore_skills_list = api.inherit('explore_skills_list', {
        'domain': fields.Nested(domain),
        'totalCount': fields.Integer,
        'matchedSkills': fields.List(fields.String),
        'mainSkills' : fields.List(fields.Nested(special_skills)),
        'salary': fields.Nested(max_min_salary)
    })

    explore_skills_list_domain = api.inherit('explore_skills_list_domain', {
        'domain': fields.Nested(domain_no_special_skills),
        'totalCount': fields.Integer,
        'salary': fields.Nested(max_min_salary)
    })

    jobs_with_company = api.model('jobs_with_company', {
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

    jobs_in_hot_province = api.inherit('jobs_in_hot_province', {
        'jobs': fields.List(fields.Nested(jobs_with_company)),
        'province_id': fields.String
    })

    explore_skills = api.inherit('explore_skills', base, {
        'data': fields.List(fields.Nested(explore_skills_list)),
    })

    explore_domain_for_skill_data = api.inherit('explore_domain_for_skill_data', {
        'domain_matched': fields.List(fields.Nested(explore_skills_list_domain)),
        'jobs_in_hot_province' : fields.List(fields.Nested(jobs_in_hot_province))
    })
    
    explore_domain_for_skill = api.inherit('explore_domain_for_skill', base, {
        'data': fields.Nested(explore_domain_for_skill_data),
    })

    province_jobs_summary = api.inherit('province_jobs_summary', {
        'province_id': fields.String,
        'totalJobsCount': fields.Integer,
        'salary': fields.Nested(max_min_salary)
    })

    task = api.inherit('task', {
        'id': fields.Integer,
        'name': fields.String,
    })

    domain_tasks = api.inherit('task', {
        'id': fields.Integer,
        'name': fields.String,
        'alternative_name': fields.String,
        'logo': fields.String,
        'content': fields.String,
        'content_vn': fields.String,
        'tasks': fields.List(fields.Nested(special_skills), attribute=lambda x: x.tasks)
    })

    domain_description_data = api.inherit('domain_description_data', {
        'domain': fields.Nested(domain_tasks),
        'mainSkills' : fields.List(fields.Nested(special_skills)),
        'totalJobsCount': fields.Integer,
        'lastJobsPost' : fields.List(fields.Nested(jobs_with_company)),
        'salary': fields.Nested(max_min_salary),
        'provinceSummary' : fields.List(fields.Nested(province_jobs_summary))
    })

    domain_description = api.inherit('domain_description', base, {
        'data': fields.Nested(domain_description_data),
    })