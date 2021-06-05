from datetime import datetime
from enum import auto
from flask_restx.fields import Date, DateTime, String
from sqlalchemy.orm import backref
from .. import db, flask_bcrypt
from app.main.util.response import json_serial
from flask import json

class CandidateModel(db.Model):
    """ Candidate Model for storing account related details """
    __tablename__ = "candidates"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    phone = db.Column(db.String(15), nullable=True) 
    full_name = db.Column(db.String(80), nullable=True)
    gender = db.Column(db.Boolean, nullable=False, default=False)
    date_of_birth = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Integer, nullable=True,default=1)
    province_id = db.Column(db.String(100), nullable=True)
    
    access_token = db.Column(db.String(512), nullable=True)
    registered_on = db.Column(db.DateTime, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)

    resumes = db.relationship('ResumeModel', backref=backref("candidate", lazy="joined"), lazy=True)
    saved_job_posts = db.relationship('CandidateJobSavesModel', uselist=True, backref="candidate")
    subcribe = db.relationship('SubcribeModel', backref="candidate", uselist=False)
    
    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = flask_bcrypt.generate_password_hash(
            password).decode('utf-8')

    def check_password(self, password):
        return flask_bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<Candidate '{}'>".format(self.email)
    
    def to_json(self):
        return {
            'id': int(self.id),
            'email': self.email,
            'phone': self.phone,
            'fullName': self.full_name,
            'dateOfBirth': str(self.date_of_birth),
            'gender': self.gender,
            'status': self.status,
            'provinceId': self.province_id,
            'registeredOn': str(self.registered_on)
        }
