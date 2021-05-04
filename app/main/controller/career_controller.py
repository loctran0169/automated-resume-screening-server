from app.main.dto.career_dto import CareerDto
from datetime import date

from flask_restx.utils import default_id
from app.main.service.career_service import match_domains_with_skill, match_domains_with_cand_skills
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
            'message': "Thành công",
            'data': match_domains_with_cand_skills(email,data)
        }


explore_domain_for_skill = api.parser()
explore_domain_for_skill.add_argument("Authorization", location="headers", required=True)
explore_domain_for_skill.add_argument("skill", type = str,location="args", required=True)
@api.route('/explore_domain_for_skill')
class ExploreSkillsForDomain(Resource):
    @api.doc("explore domains for skill matching with domain")
    @api.expect(explore_domain_for_skill)
    @api.marshal_with(CareerDto.explore_domain_for_skill, code=200) 
    @Candidate_only
    def get(self):
        identity = get_jwt_identity()
        email = identity['email']
        data = explore_domain_for_skill.parse_args() 
        return {
            'code': 200,
            'message': "Thành công",
            'data': match_domains_with_skill(data)
        }