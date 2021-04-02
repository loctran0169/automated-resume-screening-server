import os

# uncomment the line below for postgres database url from environment variable
# postgres_local_base = os.environ['DATABASE_URL']

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    BASE_URL_FE = "http://localhost:3000/"

    #main
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious_secret_key')
    SSL_DISABLE = False
    DEBUG = False

    # mail settings
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    # # gmail authentication
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'locyasuo001@gmail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'Buffaloc1999')

    # mail accounts
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin locyasuo001@gmail.com'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER','locyasuo001@gmail.com')

    DEFAULT_PAGE_SIZE = 10
    DEFAULT_PAGE = 1


class DevelopmentConfig(Config):
    # uncomment the line below to use postgres
    # SQLALCHEMY_DATABASE_URI = postgres_local_base
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://thesis:123123@localhost/thesis" # os.getenv('DATABASE_URL')
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://loctran0169:angel1999@13.67.105.72/resume-screening"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    DEBUG = False
    # uncomment the line below to use postgres
    # SQLALCHEMY_DATABASE_URI = postgres_local_base


config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)

key = Config.SECRET_KEY