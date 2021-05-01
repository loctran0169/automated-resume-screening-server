from flask.globals import request
from app.main.service.job_domain_service import add_new_skill_to_domain, get_all_domain
from ..dto.job_domain_dto import JobDomainDto

from flask_restx import Resource

api = JobDomainDto.api
_domain = JobDomainDto.job_domain

@api.route('')
class JobDomainList(Resource):
    @api.doc('list of job domain')
    def get(self):
        return get_all_domain()

add_skill_parser = api.parser()
add_skill_parser.add_argument("domain_id", type=int, location="args", required=True)
add_skill_parser.add_argument("skill_id", type=int, location="args", required=True)
@api.route('/add-skill')
class JobDomainAddSkills(Resource):
    @api.doc('add special skill to domain')
    @api.expect(add_skill_parser)
    def post(self):
        data = request.args
        return add_new_skill_to_domain(data)