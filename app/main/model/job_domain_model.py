from sqlalchemy.orm import backref
from .. import db

domain_skills = db.Table('domain_skills', db.Model.metadata,
    db.Column('domain_id', db.Integer, db.ForeignKey('job_domains.id'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skills.id'), primary_key=True)
)
class JobDomainModel(db.Model):
    __tablename__ = "job_domains"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    alternative_name = db.Column(db.String(255), nullable=False)

    job_posts = db.relationship("JobPostModel", backref=backref("job_domain", lazy="joined"), lazy=True)
    resumes = db.relationship("ResumeModel", backref=backref("job_domain", lazy="joined"), lazy=True)

    skills = db.relationship('SpecialSkillsModel', secondary=domain_skills, back_populates="domains")

    def __repr__(self):
        return "<Job domains: '{}'>".format(self.name)

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'alternative_name': self.alternative_name,
            'special_skills': [skill.to_json() for skill in self.skills]
        }