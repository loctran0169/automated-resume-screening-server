from sqlalchemy.orm import backref
from app.main.model.job_domain_model import JobDomainModel
from .. import db


class DomainTasksModel(db.Model):
    __tablename__ = "domain_tasks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(512), nullable=False)

    job_domain_id = db.Column(db.Integer, db.ForeignKey(JobDomainModel.id), nullable=False)

    def __repr__(self):
        return "<Task: '{}'>".format(self.name)

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'job_domain_id': self.job_domain_id
        }
