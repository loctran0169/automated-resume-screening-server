from sqlalchemy.sql.expression import and_
from app.main.util.data_processing import tree_matching_score_jd
from app.main.model.recruiter_model import RecruiterModel
from sqlalchemy.orm import backref, defaultload
from app.main.util.response import json_serial
from flask import json
from app.main.model.job_domain_model import JobDomainModel
from .. import db
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import func
from bs4 import BeautifulSoup
from app.main.config import Config as config

class JobPostModel(db.Model):
    __tablename__ = "job_posts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey(RecruiterModel.id), nullable=False)
    job_domain_id = db.Column(db.Integer, db.ForeignKey(JobDomainModel.id), nullable=False)

    description_text = db.Column(db.Text, nullable=False)
    requirement_text = db.Column(db.Text, nullable=False)
    benefit_text = db.Column(db.Text, nullable=False)

    domain_skills = db.Column(db.Text, nullable=False, default="")
    soft_skills = db.Column(db.Text, nullable=False, default="")
    general_skills = db.Column(db.Text, nullable=False, default="")

    job_title = db.Column(db.String(200), nullable=False)
    contract_type = db.Column(db.Integer, nullable=False)
    province_id = db.Column(db.String(100), nullable=True)

    min_salary = db.Column(db.Float, nullable=True)
    max_salary = db.Column(db.Float, nullable=True)

    education_level = db.Column(db.Integer, nullable=False)

    amount = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    deadline = db.Column(db.DateTime, nullable=False)
    posted_in = db.Column(db.DateTime, nullable=False, default=datetime.now)
    last_edit = db.Column(db.DateTime, nullable=False, default=datetime.now)
    closed_in = db.Column(db.DateTime, nullable=True)

    total_views = db.Column(db.Integer, default=0)
    total_saves = db.Column(db.Integer, default=0)
    total_applies = db.Column(db.Integer, default=0)

    skill_graph = db.Column(db.Text, nullable=True)
    domain_skill_graph = db.Column(db.Text, nullable=True)
    soft_skill_graph = db.Column(db.Text, nullable=True)

    job_resume_submissions = db.relationship('JobResumeSubmissionModel', backref="job_post", lazy=True)

    def __repr__(self):
        return "<Job post: '{}'>".format(self.id)

    def to_json(self):
        return {
            'title': self.job_title,
            'recruiter': self.recruiter_id,
            'job_domain': self.job_domain_id,
            'description': self.description_text,
            'requirement': self.requirement_text,
            'benefit': self.benefit_text,
            'contract': self.contract_type,
            'min_salary': self.min_salary,
            'max_salary': self.max_salary,
            'domain_skills': self.domain_skills,
            'soft_skills': self.soft_skills,
            'general_skills': self.general_skills,
            'amount': self.amount,  
            'is_active': self.is_active,  
            'deadline': json.dumps(self.deadline, default=json_serial),
            'posted_in': json.dumps(self.posted_in, default=json_serial),
            'last_edit': json.dumps(self.last_edit, default=json_serial),
            'closed_in': json.dumps(self.closed_in, default=json_serial),
        }

    def get_salary(self):
        if not self.min_salary and not self.max_salary:
            return "Enjoy"
        if self.min_salary and self.max_salary:
            return str(int(self.min_salary))+"$-"+str(int(self.max_salary))+"$"
        if self.min_salary:
            return ">="+str(int(self.min_salary))+"$"
        if self.max_salary:
            return "Up to "+str(int(self.max_salary))+"$"
    
    def get_short_description(self):
        soup = BeautifulSoup('<div>'+self.description_text+'</div>')
        return soup.text[:130]+"..."
    
    def get_url_detail(self):
     return config.BASE_URL_FE + "job-detail/"+ str(self.id)