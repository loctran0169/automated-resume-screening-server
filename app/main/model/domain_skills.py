from app.main.model.job_domain_model import JobDomainModel
from app.main.model.special_skills_model import SpecialSkillsModel
from sqlalchemy.orm import backref
from .. import db



class DomainSkillsModel(db.Model):
    __tablename__ = "domain_skills"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    resume_id = db.Column(db.Integer, db.ForeignKey(JobDomainModel.id), nullable=False)

    job_post_id = db.Column(db.Integer, db.ForeignKey(SpecialSkillsModel.id), nullable=False)

    # job_posts = db.relationship("JobPostModel", backref=backref("job_domain", lazy="joined"), lazy=True)
    
    def __repr__(self):
        return "<skills: '{}'>".format(self.name)

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name
        }