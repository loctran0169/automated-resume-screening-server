from app.main.util.custom_fields import NullableFloat
from flask_restx import Namespace, fields, Model
from app.main.dto.base_dto import base
from app.main.util.format_text import format_contract, format_education, format_provinces, format_salary

class CareerDto:
    api = Namespace('Career', description='career related operation')

    