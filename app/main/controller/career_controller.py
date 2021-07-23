from app.main.dto.career_dto import CareerDto
from datetime import date

from flask_restx.utils import default_id
from app.main.service.career_service import domain_description, match_domains_with_skill, match_domains_with_cand_skills
from app.main.util.custom_jwt import Candidate_only
from flask_restx import Resource
from flask import request
from flask_jwt_extended.utils import get_jwt_identity

api = CareerDto.api
api_explore_skills = CareerDto.skills_str

explore_skills = api.parser()
explore_skills.add_argument("Authorization", location="headers", required=True)
@api.route('/explore_skills')
class ExploreSkills(Resource):
    @api.doc("explore skills matching with domain")
    @api.expect(explore_skills,api_explore_skills)
    @api.marshal_with(CareerDto.explore_skills, code=200) 
    @api.header("Authorization")
    @Candidate_only
    def post(self):
        identity = get_jwt_identity()
        email = identity['email']
        data = request.json      
        return {
            'code': 200,
            'message': "Success|Thành công",
            'data': match_domains_with_cand_skills(email,data)
        }


explore_domain_for_skill = api.parser()
explore_domain_for_skill.add_argument("skill", type = str,location="args", required=True)
@api.route('/explore_domain_for_skill')
class ExploreSkillsForDomain(Resource):
    @api.doc("explore domains for skill matching with domain")
    @api.expect(explore_domain_for_skill)
    @api.marshal_with(CareerDto.explore_domain_for_skill, code=200) 
    def get(self):
        data = explore_domain_for_skill.parse_args() 
        return {
            'code': 200,
            'message': "Success|Thành công",
            'data': match_domains_with_skill(data)
        }

explore_domain = api.parser()
explore_domain.add_argument("domain_id", type = int,location="args", required=True)
@api.route('/domain')
class DomainDescription(Resource):
    @api.doc("Get description domain")
    @api.expect(explore_domain)
    @api.marshal_with(CareerDto.domain_description, code=200) 
    def get(self):
        identity = get_jwt_identity()
        data = explore_domain.parse_args() 
        return {
            'code': 200,
            'message': "Success|Thành công",
            'data': domain_description(data['domain_id'])
        }