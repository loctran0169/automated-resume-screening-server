from flask_restx import abort
from app.main.model.candidate_model import CandidateModel
from app.main.model.job_domain_model import JobDomainModel


def match_domains_with_cand_skills(email,data):
    cand = CandidateModel.query.filter_by(email=email).first()
    if cand is None:
        abort(400)
    if len(cand.resumes) == 0:
        return None, {
            'total': 0,
            'page': 0
        }
    technical_skills = cand.resumes[0].technical_skills.replace("|", " | ")

    domains = JobDomainModel.query.all()
    if not domains or len(domains) == 0:
        return None, {
            'total': 0,
            'page': 0
        }

    results = []

    for domain in domains:

        # query = JobPostModel.query.filter(JobPostModel.closed_in is not None).filter(
        # JobPostModel.deadline > datetime.now(), JobPostModel.job_domain_id == domain_id)
        # print(str(len(domain.job_posts)))
        max_job = len(domain.job_posts)
        max_salary = 0
        min_salary = 0
        if domain.job_posts and len(domain.job_posts) > 0:
            max_salary = max(domain.job_posts,
                             key=lambda x: x.max_salary or 0).max_salary or 0
            min_salary = min(domain.job_posts,
                             key=lambda x: x.min_salary or 0).min_salary or 0
        print(str(len(domain.skills)))
        # max_salary = db.session.query(func.max(
        #     JobPostModel.max_salary)).filter(JobPostModel.job_domain_id == domain_id).scalar()

        # min_salary = db.session.query(func.max(
        #     JobPostModel.min_salary)).filter(JobPostModel.job_domain_id == domain_id).scalar()
        results.append({
            "domain" : domain.to_json(),
            "totalCount": max_job,
            "salary": {
                "max": max_salary,
                "min": min_salary
            }
        })
    return results
