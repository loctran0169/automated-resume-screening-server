from flask_restx.fields import Boolean
from app.main.util.response import response_object
from app.main.service.special_skills_service import add_new_skill, get_a_skills_by_name
from flask_restx import Resource
from app.main.util.dto import SkillDto
from flask.globals import request

api = SkillDto.api
_skill = SkillDto.skill

skill_parser = api.parser()
skill_parser.add_argument("name", type=str, location="args", required=False)
skill_parser.add_argument("isMainSkill",type=bool, location="args", required=False, default=True)


@api.route('')
@api.response(404, 'Skill not found.')
class SkillFind(Resource):
    @api.doc('Find list skills by name')
    @api.expect(skill_parser)
    def get(self):
        '''get list skills by name'''
        name = request.args.get('name')
        is_main_skill = request.args.get('isMainSkill')

        skills = get_a_skills_by_name(name, is_main_skill)

        if not skills:
            return response_object()
        else:
            return response_object(200, "Thành công.", data=[skill.to_json() for skill in skills])

    @api.doc('add a new skill')
    @api.expect(skill_parser)
    def post(self):
        name = request.args.get('name')
        return add_new_skill(name)
