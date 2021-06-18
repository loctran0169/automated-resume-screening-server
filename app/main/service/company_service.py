from app.main.util.firebase import Firebase
from app.main.util.thread_pool import ThreadPool
from app.main.service.account_service import create_token
from os import name
from app.main import db
from app.main.util.response import response_object
from app.main.model.company_model import CompanyModel
from app.main.model.recruiter_model import RecruiterModel


def get_all_company():
    return CompanyModel.query.all()

def get_a_company_by_name(name, page, page_size=5):
    if name == None:
        query = CompanyModel.query.paginate(page, page_size, error_out=False)
    else:
        query = CompanyModel.query.filter(CompanyModel.name.contains(name)).paginate(page, page_size, error_out=False)

    companies = [ com for com in query.items ]
    has_next = query.has_next

    return companies, has_next


def add_new_company(data, logo_file, background_file, email):
    executor = ThreadPool.instance().executor
    logo_url = background_url = None

    if logo_file:
        logo = executor.submit(Firebase().upload, logo_file)
        logo_url = logo.result()

    if background_file:
        background = executor.submit(Firebase().upload, background_file)
        background_url = background.result()

    company = CompanyModel(
        name=data['name'], 
        location=data['location'],
        phone=data['phone'],
        email=data['email'],
        website=data['website'],
        description=data['description'],
        logo=logo_url.public_url,
        background=background_url.public_url
    )

    recruiter = RecruiterModel.query.filter_by(email=email).first()
    company.recruiters.append(recruiter)

    db.session.add(company)
    db.session.commit()

    token = create_token(id =recruiter.id ,email=email, is_HR=True, company_id=recruiter.company_id)
    
    return response_object(200, "Cập nhật thông tin công ty thành công", data=token)

def update_company(id, email):
    company = CompanyModel.query.get(id)

    if not company:
        return response_object(400, "Compay not found|Không tìm thấy công ty")

    recruiter = RecruiterModel.query.filter_by(email=email).first()

    company.recruiters.append(recruiter)

    db.session.commit()

    token = create_token(id=recruiter.id, email=email, is_HR=True, company_id=recruiter.company_id)

    return response_object(200, "Update company success|Cập nhật thông tin công ty thành công", data=token)
