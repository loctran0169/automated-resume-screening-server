from app.main.util.response import response_object
from app.main.util.custom_jwt import HR_only
from flask import request

from ..dto.job_post_dto import JobPostDto
from flask_restx import Resource
from ..service.job_post_service import add_new_post, candidate_get_job_posts, get_hr_posts, apply_cv_to_jp

from app.main.config import Config as config

api = JobPostDto.api
_job_post = JobPostDto.job_post


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

        sort_values = { 'posted_in': posted_in, 'deadline': deadline, 'view': view, 'apply': apply, 'save': save }

        if is_hr:
            return get_hr_posts(page, page_size, sort_values)
        else:
            return candidate_get_job_posts()



apply_parser = api.parser()
apply_parser.add_argument("resume_id", type=int, location="json", required=True)

@api.route('/<int:jp_id>/apply')
class SubmitResumeForJD(Resource):
    @api.doc('Submit CV.')    
    @api.expect(apply_parser)
    def post(self, jp_id):
        args = apply_parser.parse_args()
        data = apply_cv_to_jp(jp_id, args)
        return response_object(data=data)
