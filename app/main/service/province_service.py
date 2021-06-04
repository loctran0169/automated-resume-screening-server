from app.main.model.province_model import ProvinceModel
from flask import json
from app.main import db

def get_all_provinces():
    try:
        return ProvinceModel.query.all()
    except Exception as ex:
        return []