from flask_restx.utils import default_id
from app.main.model.candidate_model import CandidateModel
from app.main.model.job_post_model import JobPostModel
from .. import db
from datetime import datetime

class CandidateJobSavesModel(db.Model):
    __tablename__ = "cand_job_saves"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cand_id = db.Column(db.Integer, db.ForeignKey(CandidateModel.id), nullable=False)
    job_post_id = db.Column(db.Integer, db.ForeignKey(JobPostModel.id), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.now)
    updated_on = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    note = db.Column(db.Text, nullable=True, default = None)

    def to_json(self):
        return {
            "id": int(self.id),
            "cand_id": int(self.cand_id),
            "job_post_id": int(self.job_post_id),
            "created_on": str(self.created_on),
            "updated_on": str(self.updated_on),
            "note": self.note
        }
