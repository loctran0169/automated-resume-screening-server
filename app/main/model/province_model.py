from operator import truediv
from sqlalchemy.orm import backref
from .. import db, flask_bcrypt


class ProvinceModel(db.Model):
    """ Province Model for storing account related details """
    __tablename__ = "provinces"

    province_id = db.Column(db.String(80), primary_key=True)
    province_name = db.Column(db.String(80))
    province_name_en = db.Column(db.String(80))
    province_type = db.Column(db.String(80))

    def __repr__(self):
        return "<Province '{}'>".format(self.name)

    def to_json(self):
        return {
            "province_id": self.province_id,
            "province_name": self.province_name,
            "province_name_en": self.province_name_en,
            "province_type": self.province_type,
        }
