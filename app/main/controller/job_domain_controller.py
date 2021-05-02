from flask.globals import request
from app.main.service.job_domain_service import add_new_skill_to_domain, add_new_task_to_domain, get_all_domain
from ..dto.job_domain_dto import JobDomainDto
from flask_restx import Resource

api = JobDomainDto.api
_domain = JobDomainDto.job_domain

domain_search = api.parser()
domain_search.add_argument("name", type=str, location="args", required=False)
@api.route('')
class JobDomainList(Resource):
    @api.doc('list of job domain')
    @api.expect(domain_search)
    def get(self):
        name = request.args.get('name')
        return get_all_domain(name)

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

add_task_parser = api.parser()
add_task_parser.add_argument("domain_id", type=int, location="args", required=True)
add_task_parser.add_argument("content", type=str, location="args", required=True)
@api.route('/add-task')
class JobDomainAddSkills(Resource):
    @api.doc('add task to domain')
    @api.expect(add_skill_parser)
    def post(self):
        data = request.args
        return add_new_task_to_domain(data)