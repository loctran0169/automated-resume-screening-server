from app.main.service.subcribe_topic_service import get_subcribe, subcribe_email
from flask_jwt_extended.utils import get_jwt_identity
from app.main.util.custom_jwt import Candidate_only
from app.main.util.dto import SubcribeEmailDto
from app.main.util.response import response_object
from flask_restx import Resource
from flask.globals import request

api = SubcribeEmailDto.api

subcribe_list_header = api.parser()
subcribe_list_header.add_argument("Authorization", location="headers", required=True)

subcribe_header = api.parser()
subcribe_header.add_argument("Authorization", location="headers", required=True)
subcribe_header.add_argument("topic", type=str ,location="args", required=True)
subcribe_header.add_argument("province_id", type=str ,location="args", required=False, default = None)

@api.route('')
@api.response(404, 'Subcribe not found.')
class SkillFind(Resource):
    @api.doc('get list subcribe email')
    @api.expect(subcribe_list_header)
    @Candidate_only
    def get(self):
        '''get list subcribe email'''
        identity = get_jwt_identity()
        cand_id = identity['id']

        subcribe = get_subcribe(cand_id)
        if not subcribe:
            return response_object()
        else:
            return response_object(200, "Thành công.", data=subcribe.to_json())
    
    @api.doc('subcribe email')
    @api.expect(subcribe_header)
    @Candidate_only
    def post(self):
        identity = get_jwt_identity()
        cand_id = identity['id']

        topic = request.args.get('topic')
        province_id = request.args.get('province_id')
        return subcribe_email(cand_id,topic,province_id)