from app.main.service.subcribe_topic_service import delete_subcribe, get_subcribe, subcribe_email, update_subcribe
from flask_jwt_extended.utils import get_jwt_identity
from app.main.util.custom_jwt import Candidate_only
from app.main.util.dto import SubcribeEmailDto
from app.main.util.response import response_object
from flask_restx import Resource
from flask.globals import request

api = SubcribeEmailDto.api

subcribe_header = api.parser()
subcribe_header.add_argument("Authorization", location="headers", required=True)

subcribe_new_header = api.parser()
subcribe_new_header.add_argument("Authorization", location="headers", required=True)
subcribe_new_header.add_argument("topic", type=str ,location="args", required=True)
subcribe_new_header.add_argument("province_id", type=str ,location="args", required=False, default = None)

@api.route('')
@api.response(404, 'Subcribe not found.')
class SubcribeEmail(Resource):
    @api.doc('get list subcribe email:')
    @api.expect(subcribe_header)
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
    
    @api.doc('subcribe email: (type= 0 daily, 1: week) (statis= 0: inactive, 1: active)')
    @api.expect(subcribe_new_header)
    @Candidate_only
    def post(self):
        '''subcribe email: (type= 0 daily, 1: week) (statis= 0: inactive, 1: active)'''
        identity = get_jwt_identity()
        cand_id = identity['id']

        topic = request.args.get('topic')
        province_id = request.args.get('province_id')
        return subcribe_email(cand_id,topic,province_id)

    @api.doc('delete subcribe email')
    @api.expect(subcribe_header)
    @Candidate_only
    def delete(self):
        '''Delete subcribe'''
        identity = get_jwt_identity()
        cand_id = identity['id']

        return delete_subcribe(cand_id)


subcribe_update_header = api.parser()
subcribe_update_header.add_argument("Authorization", location="headers", required=True)
subcribe_update_header.add_argument("topic", type=str ,location="json", required=True)
subcribe_update_header.add_argument("province_id", type=str ,location="json", required=True)
subcribe_update_header.add_argument("type", type=int ,location="json", required=True)
subcribe_update_header.add_argument("status", type=int ,location="json", required=True, default = 1)
@api.route('/update')
@api.response(404, 'Subcribe not found.')
class UpdateSubcribe(Resource):
    @api.doc('update subcribe email: (type= 0 daily, 1: week) (statis= 0: inactive, 1: active) ')
    @api.expect(subcribe_update_header)
    @Candidate_only
    def post(self):
        '''update subcribe: (type= 0 daily, 1: week) (statis= 0: inactive, 1: active)'''
        identity = get_jwt_identity()
        cand_id = identity['id']

        data = request.json

        topic = data['topic']
        province_id = data['province_id']
        type_sub = data['type']
        status = data['status']

        return update_subcribe(cand_id,topic,province_id,type_sub,status)