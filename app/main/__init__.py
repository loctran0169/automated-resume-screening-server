from flask import Flask
from flask_jwt_extended import JWTManager
from flask_jwt_extended.utils import get_raw_jwt
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
# import pyrebase

from app.main.process_data.classify_wrapper.classify_manager import ClassifyManager
import os

from .config import config_by_name

db = SQLAlchemy()
flask_bcrypt = Bcrypt()
mail = Mail()
app = Flask(__name__)
jwt = JWTManager(app)
blacklist = set()
classify_manager = ClassifyManager()


# Init Firebase
from firebase_admin import credentials, initialize_app
basedir = os.path.abspath(os.path.dirname(__file__))
cred = credentials.Certificate(os.path.join(basedir, "firebase_cert.json"))
initialize_app(cred, {'storageBucket': 'automated-resume-screeni-87d75.appspot.com'})


def create_app(config_name):
    app = Flask(__name__, static_folder='../../static', static_url_path='/')
    app.config.from_object(config_by_name[config_name])
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
    db.init_app(app)
    flask_bcrypt.init_app(app)
    jwt = JWTManager(app)
    @jwt.token_in_blacklist_loader
    def check_token_in_blacklist(token_dict: dict) -> bool:
        jti = token_dict['jti']
        return jti in blacklist
    return app


def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender='automated.resume.screening@gmail.com'
    )
    mail.send(msg)

# @jwt.token_in_blacklist_loader
# def check_if_token_in_blacklist(decrypted_token):
#     jti = decrypted_token['jti']
#     return jti in blacklist

def insert_token_to_backlist(token):
    blacklist.add(token)
