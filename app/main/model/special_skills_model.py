from sqlalchemy.orm import backref
from app.main.model.job_domain_model import domain_skills
from .. import db

class SpecialSkillsModel(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)

    is_main = db.Column(db.String(255), nullable = True)
    is_soft = db.Column(db.Boolean, nullable=True, default=False)

    domains = db.relationship('JobDomainModel', secondary= domain_skills, back_populates="skills")

    # job_posts = db.relationship("JobPostModel", backref=backref("job_domain", lazy="joined"), lazy=True)
    
    def __repr__(self):
        return "<skills: '{}'>".format(self.name)

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name        
        }