from seeds.seed import seed_data
from app.main.service.account_service import get_url_verify_email
import os
import unittest

from flask_cors import CORS
from flask_jwt_extended.jwt_manager import JWTManager
from flask_mail import Mail, Message
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
import jwt

from app.main.model import candidate_education_model, candidate_job_save_model, candidate_model, company_model, filter_candidates, job_domain_model, job_post_model, job_resume_submissions_model, recruiter_model, recruiter_resume_save_model, resume_model

from app import blueprint
from app.main import create_app, db

app = create_app(os.getenv('BOILERPLATE_ENV') or 'dev')
app.register_blueprint(blueprint)
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SQLALCHEMY_POOL_SIZE'] = 100
app.config['SQLALCHEMY_POOL_RECYCLE'] = 280
app.app_context().push()

mail = Mail(app)
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
CORS(app, resources={r"/api/*": { "origins": ["http://localhost:3000","http://23.98.70.192:3000"] }})

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.errorhandler(404)
def not_found(e):
    return app.send_static_file('index.html')


@app.errorhandler(400)
def bad_request():
    return { 'message': 'Thao tác không hợp lệ' }

@manager.command
def run():
    seed_data(db)
    # app.run(debug=True, host='0.0.0.0', use_reloader=False)
    app.run(debug=True, host='0.0.0.0')


@manager.command
def test():
    """Runs the unit tests."""
    tests = unittest.TestLoader().discover('app/test', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


if __name__ == '__main__':
    manager.run()