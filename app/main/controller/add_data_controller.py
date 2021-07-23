from requests.sessions import default_headers
from app.main.service.data_input_service import insert_data, re_extract_skill
import os
import uuid

from flask_restx.fields import String
from werkzeug.datastructures import FileStorage
from app.main.util.resume_extractor import remove_temp_files
from flask_jwt_extended.utils import get_jwt_identity
from app.main.util.response import response_object
from app.main.util.custom_jwt import HR_only
from flask.globals import request
from flask_restx import Resource
from ..util.dto import DataDto

api = DataDto.api

input_data_parser = api.parser()
input_data_parser.add_argument("file_jd", type=FileStorage, location="files", required=True, default = None)
input_data_parser.add_argument("domain_id", type=int, location="args", required=True)


@api.route('/input-jd')
class DataInput(Resource):
    @api.doc('input data')
    @api.expect(input_data_parser)
    def post(self):
        '''in put data by domain'''
        domain_id = request.args.get("domain_id", None)
        file_jd = request.files.get("file_jd", None)

        file_jd_local = None
        if file_jd:
            try:
                file_jd_local = os.path.join("temp", "{}_{}_data_input.txt").format(
                    str(domain_id), str(uuid.uuid4().hex))
                file_jd.save(file_jd_local)
            except Exception as ex:
                print('save file lổi')
        return insert_data(file_jd_local, domain_id)

re_data_parser = api.parser()
re_data_parser.add_argument("password", type=int, location="args", required=True)
@api.route('/re-extract-skills')
class ReextractDataInput(Resource):
    @api.doc('ReextractDataInput')
    @api.expect(re_data_parser)
    def post(self):
        '''ReextractDataInput'''

        password = request.args.get("password")

        if password != "1999":
            return "Wrong password"
        return re_extract_skill()
