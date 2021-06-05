from app.main.model.job_domain_model import JobDomainModel
from app.main.model.candidate_model import CandidateModel
from operator import truediv
from sqlalchemy.orm import backref
from .. import db
from datetime import datetime

# type: 0 daily, 1: week 
# statis: 0: inactive, 1: active
#  
#
class SubcribeModel(db.Model):
    """ Province Model for storing account related details """
    __tablename__ = "subcribes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cand_id = db.Column(db.Integer, db.ForeignKey(CandidateModel.id), nullable=False)

    topic = db.Column(db.String(100), nullable=True)
    province_id = db.Column(db.String(100), nullable=True, default = None)

    type = db.Column(db.Integer, nullable=False, default = 0)
    subcribe_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    status = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return "<Subcribe '{}'>".format(self.topic)

    def to_json(self):
        return {
            "id": self.id,
            "cand_id": self.cand_id,
            "topic": self.topic,
            "province_id": self.province_id,
            "type": self.type,
            "subcribe_date": str(self.subcribe_date),
            "status": self.status,
        }