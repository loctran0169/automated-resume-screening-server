from datetime import datetime

from flask.wrappers import Response
from flask_restx.inputs import datetime_from_iso8601
from numpy.core.numeric import identity
from app.main.util.response import response_object
from app.main.util.custom_jwt import Candidate_only, HR_only
from flask_jwt_extended.utils import get_jwt_identity
from flask import request

from ..dto.job_post_dto import JobPostDto
from flask_restx import Resource
from ..service.job_post_service import add_new_post, count_jobs, \
        delete_job_post, get_hr_posts, get_similar_job_post_with_id, get_suggested_job_posts, hr_get_detail, apply_cv_to_jp,\
        get_job_post_for_candidate, search_jd_for_cand, \
        update_jp, close_jp, proceed_resume, get_matched_cand_info_with_job_post, \
        get_matched_list_cand_info_with_job_post


from app.main.config import Config as config
import jwt

api = JobPostDto.api
_job_post = JobPostDto.job_post
_job_post_update = JobPostDto.job_post_update



#################################
#
# Job Posts: GET, PUT, DELETE
#
#################################
delete_parser = api.parser()
delete_parser.add_argument("ids", type=int, action="split", location="args", required=True)
@api.route('')
class JobPost(Resource):
    @api.doc('add a new job post')
    @api.expect(_job_post, validate=True)
    @HR_only
    def post(self):
        data = request.json
        return add_new_post(data)

    @api.doc('get list of job post')
    def get(self):
        is_hr = request.args.get('is_hr') == 'true'

        page = request.args.get('page', config.DEFAULT_PAGE, type=int)
        page_size = request.args.get('page-size', config.DEFAULT_PAGE_SIZE, type=int)
        posted_in = request.args.get('posted_in', 0, type=int)
        deadline = request.args.get('deadline', 0, type=int)
        view = request.args.get('view', 0, type=int)
        apply = request.args.get('apply', 0, type=int)
        save = request.args.get('save', 0, type=int)

        is_showing = request.args.get('is_showing') == 'true'

        sort_values = { 'posted_in': posted_in, 'deadline': deadline, 'view': view, 'apply': apply, 'save': save }

        if is_hr:
            return get_hr_posts(page, page_size, sort_values, is_showing)
        
        api.abort(400)

    

    @api.doc('delete job list with given id')
    @api.expect(delete_parser)
    @HR_only
    def delete(self):
        args = delete_parser.parse_args()
        ids = args['ids']
        return delete_job_post(ids)




@api.route('/count')
class JobPostCount(Resource):
    @api.doc('get count of job post is closed or not')
    @HR_only
    def get(self):
        return count_jobs()



#################################
#
# Job Post Detail: GET, PUT
#
#################################
update_JP_parser = api.parser()
update_JP_parser.add_argument("Authorization", location="headers", required=True)
update_JP_parser.add_argument("job_domain_id", type=int, location="json")
update_JP_parser.add_argument("description_text", location="json")
update_JP_parser.add_argument("requirement_text", location="json")
update_JP_parser.add_argument("benefit_text", location="json")
update_JP_parser.add_argument("job_title", location="json")
update_JP_parser.add_argument("contract_type", type=int, location="json")
update_JP_parser.add_argument("min_salary", type=float, location="json")
update_JP_parser.add_argument("max_salary", type=float, location="json")
update_JP_parser.add_argument("amount", type=int, location="json")
update_JP_parser.add_argument("is_active", type=bool, location="json")
update_JP_parser.add_argument("deadline", type=str, location="json")
update_JP_parser.add_argument("province_id", type=str, location="json")
@api.route('/<int:id>')
class JobPostDetail(Resource):
    @api.doc('get detail of job post')
    @api.marshal_with(JobPostDto.response_jp_for_edit, code=200)
    def get(self, id):

        data = hr_get_detail(id)

        return response_object(data=data)

    @api.doc('Update job post details.')
    @api.marshal_with(JobPostDto.response_for_update_job_post_from_hr, code=200)
    @api.expect(update_JP_parser, validate=True)
    @HR_only
    def put(self, id):
        args = update_JP_parser.parse_args()
        identity = get_jwt_identity()
        recruiter_email = identity['email']
        data = update_jp(id, recruiter_email, args)
        return response_object(data=data)



#################################
#
# Close Job Post
#
#################################
@api.route('/<int:id>/close')
class CloseJobPost(Resource):
    @api.doc('Update job post details.')
    @api.marshal_with(JobPostDto.response_for_update_job_post_from_hr, code=200)
    @HR_only
    def post(self, id):
        identity = get_jwt_identity()
        recruiter_email = identity['email']
        data = close_jp(id, recruiter_email)
        return response_object(data=data)



#################################
#
# Apply CV
#
#################################
@api.route('/<int:jp_id>/apply')
class SubmitResumeForJD(Resource):
    apply_parser = api.parser()
    apply_parser.add_argument("resume_id", type=int, location="json", required=True)
    apply_parser.add_argument("Authorization", location="headers", required=True)
    @api.doc('Submit CV.')    
    @api.expect(apply_parser)
    # @Candidate_only
    def post(self, jp_id):
        args = self.apply_parser.parse_args()
        data = apply_cv_to_jp(jp_id, args)

        if data == 409:
            return response_object(
                code=409,
                message="CV này đã gửi vào tin đăng này."
            ), 409

        return response_object(data=data), 200



#################################
#
# Get job post detail for candidate
#
#################################
cand_get_job_detail_parser = api.parser() 
cand_get_job_detail_parser.add_argument("Authorization", location="headers", required=False)
@api.route('/<int:jp_id>/cand')
class CandidateJP(Resource):
    @api.doc('Get job post by id for candidate.')
    @api.marshal_with(JobPostDto.job_post_for_cand, code=200)
    @api.expect(cand_get_job_detail_parser)
    def get(self, jp_id):
        args = cand_get_job_detail_parser.parse_args()
        token = args["Authorization"]
        identity = None
        if token:
            token = token[7:]
            decoded = jwt.decode(token, options={"verify_signature": False})
            identity = decoded['identity']

        cand_email = None

        if identity is not None:
            cand_email = identity.get('email')

        data = get_job_post_for_candidate(jp_id, cand_email)
        return response_object(data=data)



#################################
#
# Search job post for candidate
#
#################################
cand_search_jp_parser = api.parser() 
cand_search_jp_parser.add_argument("posted_date", type=int, location="args", required=False) # Today, 3 days, 7 days, ...
cand_search_jp_parser.add_argument("contract_type", type=int, location="args", required=False) # fulltime (0), parttime (1), internship (2)
cand_search_jp_parser.add_argument("max_salary", type=float, location="args", required=False)
cand_search_jp_parser.add_argument("min_salary", type=float, location="args", required=False)
cand_search_jp_parser.add_argument("page", type=int, location="args", required=False, default=1)
cand_search_jp_parser.add_argument("page-size", type=int, location="args", required=False, default=10)
cand_search_jp_parser.add_argument("q", location="args", required=False)
cand_search_jp_parser.add_argument("province_id", type=str, location="args", required=False)
cand_search_jp_parser.add_argument("job_domain_id", type=int, location="args", required=False)
@api.route('/cand')
class JobPostForCand(Resource):
    @api.doc('Get job post by id for candidate.')
    @api.expect(cand_search_jp_parser)
    @api.marshal_with(JobPostDto.job_post_in_search_cand_response, code=200)
    def post(self):
        args = cand_search_jp_parser.parse_args()
        (data, pagination) = search_jd_for_cand(args)
        return response_object(data=data, pagination=pagination)




#################################
#
# Reject/Approve CV
#
#################################
proceed_resume_parser = api.parser()
proceed_resume_parser.add_argument('status', type=int, required=True)
proceed_resume_parser.add_argument('submission_id', type=int, required=True)
@api.route('/<int:jp_id>/update')
class ProceedResume(Resource):
    @api.doc('Get job post by id for candidate.')
    @api.expect(proceed_resume_parser)
    @HR_only
    def post(self, jp_id):
        args = proceed_resume_parser.parse_args()
        identity = get_jwt_identity()
        recruiter_email = identity['email']        
        data = proceed_resume(jp_id, recruiter_email, args)
        return response_object(data=data)



#################################################
#
# Get candidate info according to job post by id
#
#################################################
get_cand_info_parser = api.parser()
get_cand_info_parser.add_argument('Authorization', location='headers', required=True)
@api.route('/<int:job_id>/candidates/<int:resume_id>')
class GetCandInfoForJobPostById(Resource):
    @api.doc('Get applied candidate info by id.')
    @api.expect(get_cand_info_parser)
    @api.marshal_with(JobPostDto.get_cand_info_with_matched_job_post_response, code=200)
    @HR_only
    def get(self, job_id, resume_id):
        identity = get_jwt_identity()
        recruiter_email = identity['email']        
        data = get_matched_cand_info_with_job_post(recruiter_email, job_id, resume_id)
        print(resume_id)
        return response_object(data=data)


#################################################
#
# Get candidates info according to job post
#
#################################################
get_list_cand_info_parser = api.parser()
get_list_cand_info_parser.add_argument('Authorization', location='headers', required=True)
get_list_cand_info_parser.add_argument("page", type=int, location="args", required=False, default=1)
get_list_cand_info_parser.add_argument("page-size", type=int, location="args", required=False, default=20)
get_list_cand_info_parser.add_argument("domain_weight", type=int, location="args", required=True)
get_list_cand_info_parser.add_argument("general_weight", type=int, location="args", required=True)
get_list_cand_info_parser.add_argument("soft_weight", type=int, location="args", required=True)
@api.route('/<int:job_id>/candidates')
class GetListCandInfoForJobPost(Resource):
    @api.doc('Get list applied candidate info by id.')
    @api.expect(get_list_cand_info_parser)
    @api.marshal_with(JobPostDto.applied_cand_list_response, code=200)    
    @HR_only
    def get(self, job_id):
        args = get_list_cand_info_parser.parse_args()
        identity = get_jwt_identity()
        recruiter_email = identity['email']        
        (data, pagination, stats) = get_matched_list_cand_info_with_job_post(recruiter_email, job_id, args)
        return {
            'code': 200,
            'message': "Thành công",
            'data': data,
            'pagination': pagination,
            'statistics': stats
        }

#################################################
#
# Get job post simalar
#
#################################################
get_list_jp_similar_parser = api.parser()
get_list_jp_similar_parser.add_argument("job_post_id", type=int, location="args", required=True)
@api.route('/similar')
class GetListJobPostSimilar(Resource):
    @api.doc('Get job post simalar by id.')
    @api.expect(get_list_jp_similar_parser)
    @api.marshal_with(JobPostDto.job_post_similar_in_search_cand_response, code=200)    
    # @HR_only
    def get(self):
        args = get_list_jp_similar_parser.parse_args()
        data = get_similar_job_post_with_id(args['job_post_id'])
        return {
            'code': 200,
            'message': "Thành công",
            'data': data
        }



get_suggest_job = api.parser()
get_suggest_job.add_argument("Authorization", location="headers", required=True)
get_suggest_job.add_argument("domain_id", type=int, location="args", required=True)
get_suggest_job.add_argument("province_id", type=int, location="args", required=True)
get_suggest_job.add_argument("page", type=int, location="args", required=False, default=1)
get_suggest_job.add_argument("page_size", type=int, location="args", required=False, default=10)
@api.route('/suggest')
class SuggestJob(Resource):
    @api.doc("Get list suggest job posts")
    @api.expect(get_suggest_job)
    @api.marshal_with(JobPostDto.suggest_list, code=200) 
    @Candidate_only
    def get(self):
        identity = get_jwt_identity()
        email = identity['email']
        args = get_suggest_job.parse_args()
        data,pagination = get_suggested_job_posts(email,args)
        return response_object(data=data, pagination=pagination)