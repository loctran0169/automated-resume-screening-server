from app.main.util.custom_fields import NullableFloat
from flask_restx import Namespace, fields, Model
from app.main.dto.base_dto import base
from app.main.util.format_text import format_contract, format_education, format_provinces, format_salary

class CareerDto:
    api = Namespace(
        'Career', description='career related operations')

    skills_str = api.inherit('skills_str', {
            "skills": fields.List(fields.String),
        })
    special_skills = api.inherit('special_skills', {
            "id": fields.Integer,
            "name": fields.String,
        })

    domain = api.inherit('domain', {
            "id" : fields.Integer,
            "name": fields.String,
            "alternative_name": fields.String,
            "logo": fields.String,
            "content": fields.String,
            "special_skills" : fields.List(fields.Nested(special_skills),attribute=lambda x: x.skills)
        })

    max_min_salary = api.inherit('max_min_salary', {
            "max": fields.Integer,
            "min": fields.Integer,
        })

    explore_skills_list = api.inherit('explore_skills_list', {
            "domain": fields.Nested(domain),
            "totalCount": fields.Integer,
            "matchedSkills": fields.List(fields.String),
            "salary": fields.Nested(max_min_salary)
        })

    explore_skills = api.inherit("explore_skills", base, {
        'data': fields.List(fields.Nested(explore_skills_list)),
    })

    explore_domain_for_skill_data = api.inherit('explore_domain_for_skill_data', {
            'domains': fields.List(fields.Nested(explore_skills_list)),
        })

    explore_domain_for_skill = api.inherit("explore_domain_for_skill", base, {
        'data': fields.Nested(explore_domain_for_skill_data),
    })