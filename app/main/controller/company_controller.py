import os
import uuid

from flask_restx.fields import String
from app.main.util.resume_extractor import remove_temp_files
from flask_jwt_extended.utils import get_jwt_identity
from app.main.util.response import response_object
from app.main.util.custom_jwt import HR_only
from flask.globals import request
from app.main.service.company_service import add_new_company, get_a_company_by_name, update_company
from flask_restx import Resource
from ..util.dto import CompanyDto
from app.main.util.data_processing import tree_matching_score_jd

api = CompanyDto.api
_company = CompanyDto.company

search_parser = api.parser()
search_parser.add_argument("name", type=str, location="args", required=False)
@api.route('/search')
@api.response(404, 'Company not found.')
class CompanyFind(Resource):
    @api.doc('Find list companies by name')
    @api.expect(search_parser)
    def get(self):
        '''get list companies by name'''
        name = request.args.get('name')
        page = request.args.get('page', 1, type=int)

        companies, has_next = get_a_company_by_name(name, page)

        if not companies:
            return response_object()
        else:
            return response_object(200, "Success|Thành công.", data=[company.to_json() for company in companies], pagination={"has_next": has_next})


@api.route('')
class Company(Resource):
    @api.doc('add a new company')
    @HR_only
    def post(self):
        files = request.files
        data = request.form

        remove_temp_files('temp/*')

        logo = files.get("logo", None)
        background = files.get("background", None)

        logo_file = background_file = None

        if logo:
            logo_file = os.path.join("temp", "{}_{}_logo.png").format(data['name'], str(uuid.uuid4().hex))
            logo.save(logo_file)

        if background:
            background_file = os.path.join("temp", "{}_{}_background.png").format(data['name'], str(uuid.uuid4().hex)) 
            background.save(background_file)

        identity = get_jwt_identity()
        email = identity['email']

        return add_new_company(data, logo_file, background_file, email)


@api.route('/<int:id>/update')
class CompanyUpdate(Resource):
    @api.doc("update HR company")
    @HR_only
    def put(self, id):
        identity = get_jwt_identity()
        email = identity['email']
        
        return update_company(id, email)