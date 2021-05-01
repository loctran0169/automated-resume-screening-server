
from sqlalchemy.orm import backref
from .. import db, flask_bcrypt


class CompanyModel(db.Model):
    """ company Model for storing account related details """
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80))
    location = db.Column(db.String(180))
    phone = db.Column(db.String(15))
    email = db.Column(db.String(255))
    logo = db.Column(db.String(255))
    background = db.Column(db.String(255))
    website = db.Column(db.String(255))
    description = db.Column(db.String(255))

    recruiters = db.relationship('RecruiterModel', backref=backref("company", lazy=True), lazy=True)

    def __repr__(self):
        return "<Company '{}'>".format(self.name)

    def to_json(self):
        return {
            "id": int(self.id),
            "name": self.name,
            "location": self.location,
            "phone": self.phone,
            "email": self.email,
            "logo": self.logo,
            "background": self.background,
            "website": self.website,
            "description": self.description,
        }
