import re
from app.main.util.response import response_object
from app.main.util.custom_jwt import Candidate_only, HR_only
from flask_jwt_extended.utils import get_jwt_identity
from app.main.util.custom_jwt import Candidate_only
from app.main.service.recruiter_service import get_a_account_recruiter_by_email
from app.main import send_email
from app.main.service.candidate_service import create_candidate_document, delete_a_candidate_by_email, delete_document, get_document, set_token_candidate, get_a_account_candidate_by_email, insert_new_account_candidate, update_candidate_profile, update_document, verify_account_candidate
from app.main.service.account_service import create_token, get_url_verify_email
from flask_jwt_extended import decode_token
import datetime
from werkzeug.datastructures import FileStorage
from app.main.service.candidate_service import get_candidate_by_id, get_candidate_resumes, set_token_candidate, \
    get_a_account_candidate_by_email, insert_new_account_candidate, verify_account_candidate, \
    get_candidate_by_id, alter_save_job, get_saved_job_posts, get_applied_job_posts
import os
import uuid
from flask import request, jsonify, url_for, render_template
from flask_restx import Resource, inputs
from app.main.util.dto import CandidateDto
from app.main.util.custom_jwt import get_jwt_identity

apiCandidate = CandidateDto.api
_candidate = CandidateDto.candidate
_candidateUpdateProfile = CandidateDto.profile_update
_candidateAccount = CandidateDto.account
@apiCandidate.route('/candidate/register')
class RegisterCandidateList(Resource):

    @apiCandidate.response(200, 'account register successfully.')
    @apiCandidate.doc('register a new account candidate')
    @apiCandidate.expect(_candidate, validate=True)
    def post(self):
        '''register a new account candiadate '''
        data = request.json

        regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'

        if not re.search(regex, data['email']):
            return {
                    'status': 'failure',
                    'message': 'Email wrong format|Email sai định dạng',
                    'type':'candidate'
                }, 400
        account = get_a_account_candidate_by_email(data['email'])

        # if account with email not exist
        if not account:
            try:
               
                insert_new_account_candidate(data)

                # if account insert successfully
                account_inserted = get_a_account_candidate_by_email(data['email'])

                if account_inserted:
                    # send email here
                    try:
                        confirm_url = get_url_verify_email(account_inserted.access_token,"candidate")
                        html = render_template('email.html', confirm_url = confirm_url)
                        subject = "Please confirm your email"
                        send_email(data['email'], subject, html)
                        return {
                            'status': 'success',
                            'message': 'Register success|Đăng ký tài khoản thành công',
                            'type':'candidate'
                        }, 200

                    except Exception as e: # delete account if send email error
                        try:
                            delete_a_candidate_by_email(data['email'])
                        except Exception as ex:
                            print(str(ex.args))
                        return {
                            'status': 'failure',
                            'message': 'Register fail. Email not exist.|Đăng ký thất bại. Email không tồn tại',
                            'type':'candidate'
                        }, 501
                else:
                    print("chổ else")                    
                    return {
                        'status': 'failure',
                        'message': 'Register fail|Đăng ký không thành công',
                        'type':'candidate'
                    }, 409
            except Exception as e:
                print(e.args)
                return {
                    'status': 'failure',
                    'message': 'Register fail|Đăng ký không thành công',
                    'type':'candidate'
                }, 409
        else:
            # if exist account and verified
            if account.confirmed:
                return {
                    'status': 'failure',
                    'message': 'Account already exist.|Tài khoản đã tồn tại. Vui lòng đăng nhập',
                    'type': 'candidate',
                }, 409
            else:
                # resend email if previously expired email
                jwt_data = None
                try:
                    jwt_data = decode_token(account.access_token)
                except Exception as ex:
                    jwt_data = None
                if jwt_data == None or datetime.datetime.now().timestamp() > jwt_data['exp']:
                    access_token = create_token(id = account.id ,email=account.email)
                    set_token_candidate(account.email, access_token)
                    try:
                        confirm_url = url_for('api.Candidate_candidate_verify',token=account.access_token, _external=True)
                        html = render_template('email.html', confirm_url = confirm_url)
                        subject = "Please confirm your email"
                        send_email(data['email'], subject, html)

                        return{
                            'status': 'success',
                            'message': 'Send email success|Gửi lại email thành công',
                            'type':'candidate'
                        },200

                    except Exception as e: # delete account if send email error
                        return {
                            'status': 'failure',
                            'message': 'Email not exist|Gửi lại email không thành công. Email không tồn tại',
                            'type':'candidate'
                        }, 500
                return {
                    'status': 'failure',
                    'message': 'Account already existed. Please check your email.|Tài khoản đã đăng ký thành công nhưng chưa được xác thực. Vui lòng kiểm tra email để xác thực tài khoản',
                    'type': 'candidate'
                }, 201

@apiCandidate.route('/candidate/confirm/<token>')
@apiCandidate.param('token', 'The token Verify')
class CandidateVerify(Resource):
    @apiCandidate.doc('Verify account account candidate')
    def get(self, token):
        '''Verify account account'''
        try:
            # decode token to json
            jwt_data = decode_token(token) or None

            # check token valid or expired
            if jwt_data and ('identity' in jwt_data) and datetime.datetime.now().timestamp() < jwt_data['exp']:

                account = get_a_account_candidate_by_email(jwt_data['identity']['email'])
                if account and (account.access_token == token):
                    if account.confirmed:
                        return{
                            'status': 'success',
                            'message': 'Account confirmed|Tài khoản đã xác thực. Vui lòng đăng nhập.',
                            'type':"candidate"
                        }, 200
                    else:
                        verify_account_candidate(account.email)
                        return{
                            'status': 'success',
                            'message': 'Account verify success|Xác thực tài khoản thành công!',
                            'type':"candidate"
                        }, 200
                else:
                    return {
                        'status': 'failure',
                        'message': 'Something when wrong|Đường dẫn không tồn tại',
                        'type':"candidate"
                    }, 404
            else:
                return {
                    'status': 'failure',
                    'message': 'Something when wrong|Đường dẫn không tồn tại hoặc đã hết hạn',
                    'type':"candidate"
                }, 403
        except Exception:
            return{
                'status': 'failure',
                'message': 'Try again|Vui lòng thử lại'
                ,'type':"candidate"
            }, 420

@apiCandidate.route('/candidate/login')
@apiCandidate.response(404, 'account not found.')
@apiCandidate.expect(_candidateAccount, validate=True)
class AccountLogin(Resource):
    @apiCandidate.doc('Login candidate with email, password')
    @apiCandidate.expect(_candidateAccount, validate=True)
    def post(self):
        '''get a account given its identifier'''
        data = request.json
        try:
            # find account with email
            account = get_a_account_candidate_by_email(data['email'])

            # if  account not exist
            if not account:
                return {
                    'status': 'failure',
                    'message': 'Account not exist|Tài khoản không tồn tại',
                    'type':'candidate'
                }, 404

            # check password
            if account.check_password(data['password']):

                try:
                    # account have not been verified
                    if not account.confirmed:

                        # resend email if previously expired email
                        jwt_data = decode_token(account.access_token)
                        if datetime.datetime.now().timestamp() > jwt_data['exp']:
                            access_token = create_token(id = account.id ,email=account.email)
                            set_token_candidate(account.email, access_token)
                            # send email here
                        return {
                            'status': 'failure',
                            'message': 'Account not verify email|Tài khoản đã đăng ký thành công nhưng chưa được xác thực. Vui lòng kiểm tra email để xác thực tài khoản',
                            'type':'candidate'
                        }, 403

                    access_token = create_token(id = account.id ,email=account.email)
                    return {
                        'status': 'success',
                        'access_token': access_token,
                        'message': 'Login success|Đăng nhập thành công',
                        'type':'candidate'
                    }, 200
                except Exception as e:
                    return{
                        'status': 'failure',
                        'message': 'Some thing when wrong|Vui lòng thử lại',
                        'type':'candidate'
                    }, 500
            else:
                return {
                    'status': 'failure',
                    'message': 'Email hoặc mật khẩu không chính xác',
                    'type':'candidate'
                }, 404
        except Exception as e:
            return{
                'status': 'failure',
                'message': 'Some thing when wrong|Vui lòng thử lại',
                'type':'candidate'
            }, 500

candidate_profile_header = apiCandidate.parser()
candidate_profile_header.add_argument("Authorization", location="headers", required=True)
@apiCandidate.route('/candidate/profile')
@apiCandidate.response(404, 'Profile not found.')
class CandidateFindProfile(Resource):
    @apiCandidate.doc('Find list companies')
    @apiCandidate.marshal_with(CandidateDto.candidate_profile, code=200)
    @apiCandidate.expect(candidate_profile_header)
    @Candidate_only
    def get(self):
        '''get profile by token'''
        identity = get_jwt_identity() 
        email = identity['email']

        profile = get_a_account_candidate_by_email(email)

        if not profile:
            return {
                'status': 'failure',
                'message': 'Account not exist|Tài khoản không tồn tại',
                'type' : 'candidate'
            },400
        else:
            return response_object(data=profile)
            
candidate_update_profile = apiCandidate.parser()
candidate_update_profile.add_argument("Authorization", location="headers", required=True)
@apiCandidate.route('/candidate/profile/update')
@apiCandidate.response(404, 'Profile not found.')
class CandidateUpdateProfile(Resource):

    # @apiCandidate.response(200, 'update profile successfully.')
    @apiCandidate.doc('update a profile candidate')
    @apiCandidate.expect(candidate_update_profile,CandidateDto.profile_update, validate=True)
    @Candidate_only
    def post(self):
        '''update a new profile candiadate '''
        data = request.json

        identity = get_jwt_identity()
        email_in_token = identity['email']

        # if email_in_token != data['email']:
        #     return {
        #         'status': 'failure',
        #         'message': 'Email does not match to data body email',
        #         'type' : 'candidate'
        #     }, 200

        profile = get_a_account_candidate_by_email(email_in_token)

        if not profile:
            return {
                'status': 'failure',
                'message': 'Profile not found|Thông tin không tồn tại',
                'type' : 'candidate'
            },400

        try:
            update_candidate_profile(profile.id,data)

            return {
                'status': 'success',
                'message': 'Update profile successfully|Cập nhật thông tin thành công',
                'data' :{
                    'profile':get_a_account_candidate_by_email(email_in_token).to_json()
                },
                "error": None,
                'type' : 'candidate'
            },200
        except Exception as e:
            print(e.args)
            return {
                'status': 'failure',
                'message': 'Update profile failure|Cập nhật thông tin thất bại',
                'type' : 'candidate'
            },400 


#################################
#
# Query candidates by id
#
#################################
candidates_by_id_parser = apiCandidate.parser()
candidates_by_id_parser.add_argument("Authorization", location="headers", required=True)
candidates_by_id_parser.add_argument("resume_id", location="args", required=False)
@apiCandidate.route("/candidates/<int:id>")
class QueryCandidates(Resource):
    @apiCandidate.doc("Get candidate by id")
    @apiCandidate.marshal_with(CandidateDto.candidate_detail_response, code=200)
    @apiCandidate.expect(candidates_by_id_parser)
    @HR_only
    def get(self, id): 
        identity = get_jwt_identity()
        rec_email = identity['email']
        args = candidates_by_id_parser.parse_args()
        resume_id = args.get("resume_id")
        data = get_candidate_by_id(id, rec_email, resume_id)
        return response_object(data=data)



###################
# Save Job Post
###################
save_res_parser = apiCandidate.parser()
save_res_parser.add_argument('Authorization', location='headers', required=True)
save_res_parser.add_argument('job_post_id', type=int, location='json', required=True)
save_res_parser.add_argument('status', type=int, location='json', required=True)

get_res_parser = apiCandidate.parser()
get_res_parser.add_argument("Authorization", location="headers", required=True)
get_res_parser.add_argument("page", type=int, location="args", required=False, default=1)
get_res_parser.add_argument("page-size", type=int, location="args", required=False, default=10)
get_res_parser.add_argument("from-date", type=inputs.datetime_from_iso8601, location="args", required=False)
get_res_parser.add_argument("to-date", type=inputs.datetime_from_iso8601, location="args", required=False)

@apiCandidate.route('/job-posts/save')
class SaveResume(Resource):
    @apiCandidate.doc("Save job post")
    @apiCandidate.expect(save_res_parser)
    @Candidate_only
    def post(self):
        identity = get_jwt_identity()
        email = identity['email']
        args = save_res_parser.parse_args()
        data = alter_save_job(email, args)
        return response_object(data=data)

    @apiCandidate.doc("Get saved job posts")
    @apiCandidate.expect(get_res_parser)
    @apiCandidate.marshal_with(CandidateDto.get_saved_job_post_list_response, code=200)
    @Candidate_only
    def get(self):
        identity = get_jwt_identity()
        email = identity['email']
        args = get_res_parser.parse_args()
        (data, pagination) = get_saved_job_posts(email, args)
        return response_object(data=data, pagination=pagination)



get_applied_jobs = apiCandidate.parser()
get_applied_jobs.add_argument("Authorization", location="headers", required=False)
get_applied_jobs.add_argument("page", type=int, location="args", required=False, default=1)
get_applied_jobs.add_argument("page-size", type=int, location="args", required=False, default=10)
get_applied_jobs.add_argument("from-date", type=inputs.datetime_from_iso8601, location="args", required=False)
get_applied_jobs.add_argument("to-date", type=inputs.datetime_from_iso8601, location="args", required=False)
# get_applied_jobs.add_argument("to-date", type=int, location="args", required=True)
@apiCandidate.route('/job-posts/apply')
class GetAppliedJobs(Resource):
    @apiCandidate.doc("Get applied job posts")
    @apiCandidate.expect(get_applied_jobs)
    @apiCandidate.marshal_with(CandidateDto.get_applied_job_post_list_response, code=200)
    @Candidate_only
    def get(self):
        identity = get_jwt_identity()
        email = identity['email']
        args = get_res_parser.parse_args()
        (data, pagination) = get_applied_job_posts(email, args)
        return response_object(data=data, pagination=pagination)


@apiCandidate.route('/candidates/resumes')
class CandidateResumes(Resource):
    @apiCandidate.doc("Get uploaded resumes")
    @apiCandidate.marshal_with(CandidateDto.resume_list, code=200)
    @Candidate_only
    def get(self):
        identity = get_jwt_identity()
        email = identity['email']

        data = get_candidate_resumes(email)
        return response_object(data=data)


get_document_parser = apiCandidate.parser()
get_document_parser.add_argument("Authorization", location="headers", required=True)

create_document_parser = apiCandidate.parser()
create_document_parser.add_argument("file", type= FileStorage, location="files", required=True)
# create_document_parser.add_argument("name", type= str, location="form", required=True)
create_document_parser.add_argument("Authorization", location="headers", required=True)

update_document_parser = apiCandidate.parser()
update_document_parser.add_argument("document_id", type= int, location="args", required=True)
update_document_parser.add_argument("name", type= str, location="args", required=True)
update_document_parser.add_argument("Authorization", location="headers", required=True)

delete_document_parser = apiCandidate.parser()
delete_document_parser.add_argument("document_id", type= int, location="args", required=True)
delete_document_parser.add_argument("Authorization", location="headers", required=True)
@apiCandidate.route('/candidates/document')
class CandidateDocument(Resource):

    @apiCandidate.doc("get documents for candidate")
    @apiCandidate.expect(get_document_parser)
    @Candidate_only
    def get(self):
        '''get document candiadate '''
        identity = get_jwt_identity()
        cand_id = identity['id']

        return get_document(cand_id)

    @apiCandidate.doc("uploaded document")
    @apiCandidate.expect(create_document_parser)
    @Candidate_only
    def post(self):
        '''Upload new document candiadate '''
        identity = get_jwt_identity()
        cand_id = identity['id']
        args = create_document_parser.parse_args()

        filepath = None
        try:
            file = args["file"]
            file_ext = file.filename.split('.')[-1]
            filename = file.filename.replace(".{}".format(file_ext), "")

            filepath = os.path.join("temp_pdf", "{name}_{uid}.{ext}".format(name=filename, uid=str(uuid.uuid4().hex), ext=file_ext))
            file.save(filepath)
        except Exception as ex:
            filepath = None

        return create_candidate_document(cand_id, filepath, file.filename, file_ext)
        # return create_candidate_document(cand_id, filepath, args['name'], file_ext)

    @apiCandidate.doc("update document")
    @apiCandidate.expect(update_document_parser)
    @Candidate_only
    def put(self):
        '''update document name candiadate '''
        identity = get_jwt_identity()
        cand_id = identity['id']
        args = update_document_parser.parse_args()

        return update_document(cand_id, args['document_id'], args['name'])

    @apiCandidate.doc("delete document")
    @apiCandidate.expect(delete_document_parser)
    @Candidate_only
    def delete(self):
        '''delete document candiadate '''
        identity = get_jwt_identity()
        cand_id = identity['id']
        args = delete_document_parser.parse_args()

        return delete_document(cand_id, args['document_id'])
