from operator import truediv
import re
from sys import exec_prefix

from flask_restx.fields import DateTime
from app.main.service.candidate_service import get_a_account_candidate_by_email
from app.main import send_email
from app.main.service.recruiter_service import delete_a_recruiter_by_email, get_a_account_recruiter_by_email, set_token_recruiter, \
    insert_new_account_recruiter, verify_account_recruiter, alter_save_resume, get_saved_resumes
from app.main.service.account_service import create_token, get_url_verify_email
from flask_jwt_extended.utils import get_jwt_identity
from flask_jwt_extended import decode_token
import pymysql
import datetime

from flask import request, jsonify, url_for, render_template
from flask_restx import Resource, inputs
from app.main.util.dto import RecruiterDto
from app.main.util.response import response_object
from app.main.util.custom_jwt import HR_only

apiRecruiter = RecruiterDto.api
_recruiter = RecruiterDto.recruiter
_accountRecruiter = RecruiterDto.account

@apiRecruiter.route('/recruiter/register')
class RegisterrecruiterList(Resource):

    @apiRecruiter.response(200, 'account register successfully.')
    @apiRecruiter.doc('register a new account recruiter')
    @apiRecruiter.expect(_recruiter, validate=True)
    def post(self):
        '''register a new account candiadate '''
        data = request.json

        account = get_a_account_recruiter_by_email(data['email'])

        # if account with email not exist
        if not account:
            try:
               
                insert_new_account_recruiter(data)

                # if account insert successfully
                account_inserted = get_a_account_recruiter_by_email(data['email'])

                if account_inserted:
                    # send email here
                    try:
                        confirm_url = get_url_verify_email(account_inserted.access_token,"recruiter")
                        html = render_template('email.html', confirm_url = confirm_url)
                        subject = "Please confirm your email"
                        send_email(data['email'], subject, html)

                        return {
                            'status': 'success',
                            'message': 'Successfully registered. Please check your email to Verify account.|Đăng ký thành công. Vui lòng kiểm tra email để xác thực.',
                            'type':'recruiter'
                        }, 200

                    except Exception as e: # delete account if send email error
                        try:
                            delete_a_recruiter_by_email(data['email'])
                        except Exception as ex:
                            print(str(ex.args))
                        return {
                            'status': 'failure',
                            'message': 'Registation failed. Email not working.|Email thông tồn tại',
                            'type':'recruiter'
                        }, 501
                else:                    
                    return {
                        'status': 'failure',
                        'message': 'Registation failed. Server occur|Thất bại',
                        'type':'recruiter'
                    }, 409
            except Exception as e:
                
                return {
                    'status': 'failure',
                    'message': 'Registation failed. Server occur|Thất bại',
                    'type':'recruiter'
                }, 409
        else:            

            # if exist account and verified
            if account.confirmed:
                return {
                    'status': 'failure',
                    'message': 'Account already exists. Please Log in.|Tài khoản đã tồn tại',
                    'type': 'recruiter',
                }, 409
            else:
                # resend email if previously expired email
                jwt_data = decode_token(account.access_token)
                if datetime.datetime.now().timestamp() > jwt_data['exp']:
                    access_token = create_token(id = account.id,email=account.email)
                    set_token_recruiter(account.email, access_token)
                    try:
                        confirm_url = url_for('api.Recruiter_recruiter_verify',token=account.access_token, _external=True)
                        html = render_template('email.html', confirm_url = confirm_url)
                        subject = "Please confirm your email"
                        send_email(data['email'], subject, html)

                        return{
                            'status': 'success',
                            'message': 'Resend email successful.|Gửi thông tin xác thực thành công',
                            'type':'recruiter'
                        },200

                    except Exception as e: # delete account if send email error
                        return {
                            'status': 'failure',
                            'message': 'Resend email failure. Email not working.|Email không tồn tại. Thử lại sau',
                            'type':'recruiter'
                        }, 500
                return {
                    'status': 'failure',
                    'message': 'The account has been created but not verified, please check the email.|Vui lòng kiểm tra email để xác thực',
                    'type': 'recruiter'
                }, 201


@apiRecruiter.route('/recruiter/confirm/<token>')
@apiRecruiter.param('token', 'The token Verify')
class RecruiterVerify(Resource):
    @apiRecruiter.doc('Verify account account recruiter')
    def get(self, token):
        '''Verify account account'''
        try:
            # decode token to json
            jwt_data = decode_token(token) or None

            # check token valid or expired
            if jwt_data and ('identity' in jwt_data) and datetime.datetime.now().timestamp() < jwt_data['exp']:

                account = get_a_account_recruiter_by_email(jwt_data['identity']['email'])
                if account and (account.access_token == token):
                    if account.confirmed:
                        return{
                            'status': 'success',
                            'message': 'Account already confirmed. Please login.|Đã xác thực thành công',
                            'type':"recruiter"
                        }, 200
                    else:
                        verify_account_recruiter(account.email)
                        return{
                            'status': 'success',
                            'message': 'You have confirmed your account. Thanks!|Xác thực thành công',
                            'type':"recruiter"
                        }, 200
                else:
                    return {
                        'status': 'failure',
                        'message': 'The confirmation link is not found.|Xác thực thất bại',
                        'type':"recruiter"
                    }, 404
            else:
                return {
                    'status': 'failure',
                    'message': 'The confirmation link is invalid or has expired.|Đường dẫn hết hạn',
                    'type':"recruiter"
                }, 403
        except Exception:
            return{
                'status': 'failure|Thất bại',
                'message': 'Try again'
                ,'type':"recruiter"
            }, 420


@apiRecruiter.route('/recruiter/login')
@apiRecruiter.response(404, 'account not found.')
class RecruiterLogin(Resource):
    @apiRecruiter.doc('Login recuiter with email, password')
    @apiRecruiter.expect(_accountRecruiter, validate=True)
    def post(self):
        '''login account with recruiter'''
        data = request.json

        regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
        if not re.search(regex, data['email']):
            return {
                    'status': 'failure',
                    'message': 'Email wrong format|Email sai định dạng',
                    'type':'candidate'
                }, 400
        try:
            # find account with email
            account = get_a_account_recruiter_by_email(data['email'])

            # if  account not exist
            if not account:
                return {
                    'status': 'failure',
                    'message': 'Account not exist|Tài khoàn không tồn tại',
                    'type':'recruiter'
                }, 404

            # check password
            if account.check_password(data['password']):
                try:
                    # account have not been verified                    
                    if not account.confirmed:
                        # resend email if previously expired email
                        jwt_data = decode_token(account.access_token)
                        if datetime.datetime.now().timestamp() > jwt_data['exp']:
                            access_token = create_token(id = account.id,email=account.email, is_HR=True, company_id=account.company_id)
                            set_token_recruiter(account.email, access_token)
                            # send email here
                        return {
                            'status': 'failure',
                            'message': 'The account has been created but not verified, please check the email.|Tài khoàn chưa được xác thực',
                            'type':'recruiter'
                        }, 203
                    access_token = create_token(id = account.id, email=account.email, is_HR=True, company_id=account.company_id)

                    return {
                        'status': 'success',
                        'access_token': access_token,
                        'message': 'Login successfully|Đăng nhập thành công',
                        'type':'recruiter'
                    }, 200
                except Exception as e:
                    return{
                        'status': 'failure',
                        'message': 'Try again|Thất bại',
                        'type':'recruiter'
                    }, 500
            else:
                return {
                    'status': 'failure',
                    'message': 'Email or password invalid|Sai mật khẩu',
                    'type':'recruiter'
                }, 401
        except Exception as e:
            return{
                'status': 'failure',
                'message': 'Try again|Thất bại',
                'type':'recruiter'
            }, 500




###################
# Save Resumes
###################
save_res_parser = apiRecruiter.parser()
save_res_parser.add_argument('Authorization', location='headers', required=True)
save_res_parser.add_argument('resume_id', type=int, location='json', required=True)
save_res_parser.add_argument('status', type=int, location='json', required=True)

get_res_parser = apiRecruiter.parser()
get_res_parser.add_argument("Authorization", location="headers", required=False)
get_res_parser.add_argument("page", type=int, location="args", required=False, default=1)
get_res_parser.add_argument("page-size", type=int, location="args", required=False, default=10)
get_res_parser.add_argument("from-date", type=inputs.datetime_from_iso8601, location="args", required=False)
get_res_parser.add_argument("to-date", type=inputs.datetime_from_iso8601, location="args", required=False)

@apiRecruiter.route('/recruiter/save-resumes')
class SaveResume(Resource):
    @apiRecruiter.doc("Save resumes")
    @apiRecruiter.expect(save_res_parser)
    @HR_only
    def post(self):
        identity = get_jwt_identity()
        email = identity['email']
        args = save_res_parser.parse_args()
        data = alter_save_resume(email, args)
        return response_object(data=data)

    @apiRecruiter.doc("Get resumes")
    @apiRecruiter.expect(get_res_parser)
    @apiRecruiter.marshal_with(RecruiterDto.get_saved_resume_list_response, code=200)
    @HR_only
    def get(self):
        identity = get_jwt_identity()
        email = identity['email']
        args = get_res_parser.parse_args()
        (data, pagination) = get_saved_resumes(email, args)
        return response_object(data=data, pagination=pagination)