from app.main.model.job_post_model import JobPostModel
from app.main.model.candidate_model import CandidateModel
from sqlalchemy.orm import backref
from .. import db
from datetime import datetime


class JobNoteModel(db.Model):
    __tablename__ = "job_notes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cand_id = db.Column(db.Integer, db.ForeignKey(CandidateModel.id), nullable=False)
    job_post_id = db.Column(db.Integer, db.ForeignKey(JobPostModel.id), nullable=False)

    note_date = db.Column(db.DateTime, nullable=False, default=datetime.now)

    note = db.Column(db.Text, nullable=True, default = None)
    
    def __repr__(self):
        return "<Job Note: '{}'>".format(self.note)

    def to_json(self):
        return {
            'id': int(self.id),
            'cand_id': int(self.cand_id),
            'job_post_id': int(self.job_post_id),
            'note_date': str(self.note_date),
            'note': self.note,
        }