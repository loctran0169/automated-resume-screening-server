from app.main.util.response import response_object
from app.main.service.account_service import create_token
from sys import stdout

from flask import request, jsonify, url_for, render_template
from flask.wrappers import Response
from flask_restx import Resource

from app.main import insert_token_to_backlist, send_email
from app.main.resource.parser import register_parser, login_parser
from flask_jwt_extended import (
    jwt_required,  get_raw_jwt)
from ..util.dto import AccountDto

api = AccountDto.api
_account = AccountDto.account
_account_login = AccountDto.account_login

@ api.route('/logout')
@ api.expect(_account_login)
class AccountLogout(Resource):
    @ api.doc('Logout this session')
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        insert_token_to_backlist(jti)
        return response_object(message="Successfully logged out|Đăng xuất thành công",data=None)
