from app.main.model.job_post_model import JobPostModel
from app.main.model.resume_model import ResumeModel
from .. import db
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy import funcfilter
from sqlalchemy import func


class JobResumeSubmissionModel(db.Model):
    __tablename__ = "job_resume_submissions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    resume_id = db.Column(db.Integer, db.ForeignKey(ResumeModel.id), nullable=False)

    job_post_id = db.Column(db.Integer, db.ForeignKey(JobPostModel.id), nullable=False)

    submit_date = db.Column(db.DateTime, default=datetime.now)
    score = db.Column(db.Float, nullable=True)

    note = db.Column(db.Text, nullable=True)

    process_status = db.Column(db.Boolean, nullable=True)
    score_array = db.Column(db.String(100), nullable=True)
    score_explanation_array = db.Column(db.String(100), nullable=True)

    is_calculating = db.Column(db.Boolean, default=False)

    def to_json(self):
        return {
            "id": int(self.id),
            "resume_id": int(self.resume_id),
            "job_post_id": int(self.job_post_id),
            "submit_date": str(self.submit_date),
            "note": self.note
        }

    @hybrid_property
    def score_dict(self):
        exps = self.score_explanation_array.split('|')
        scores = self.score_array.split('|')
        d = dict()
        for i, v in enumerate(exps):
            d[v] = round(float(scores[i]), 3)
        return d

    @hybrid_method
    def avg_score(self, domain_weight, general_weight, soft_weight):
        exps = self.score_explanation_array.split('|')
        scores = self.score_array.split('|')
        total = 0
        for i, v in enumerate(exps):
            weight = 0
            if v == 'general_score': weight = general_weight
            if v == 'domain_score': weight = domain_weight
            if v == 'softskill_score': weight = soft_weight
            total += float(scores[i]) * weight
        return round(total, 3)