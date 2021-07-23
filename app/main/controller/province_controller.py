from app.main.service.province_service import get_all_provinces
from app.main.util.dto import ProvinceDto
from flask_restx import Resource

api = ProvinceDto.api

@api.route('')
class ProvinceList(Resource):
    @api.doc('list province')
    def get(self):
        provinces = get_all_provinces()
        return provinces