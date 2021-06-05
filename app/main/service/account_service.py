import datetime
from flask_jwt_extended import (create_access_token)
from app.main.config import Config as config

def create_token(id,email, is_HR = False, company_id = None, day=7):
    expires = datetime.timedelta(day)
    return create_access_token(identity={'id': id, 'email': email, 'is_HR': is_HR, 'company_id': company_id }, expires_delta=expires)

def get_url_verify_email(token,type):
    return config.BASE_URL_FE + "confirm-mail/?token="+ token+"&type="+type
