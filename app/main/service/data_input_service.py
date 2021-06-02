from app.main.util.firebase import Firebase
from app.main.model.company_model import CompanyModel
import re
from app.main.process_data.classify_wrapper.skill_paper import SkillPaper
from sqlalchemy.sql.expression import true
from app.main.model.recruiter_resume_save_model import RecruiterResumeSavesModel
from sys import float_info
import time as log_time
import datetime
import dateutil.parser
import requests
import json
import math
from app.main import db
from app.main.dto.job_post_dto import JobPostDto
from app.main.model.resume_model import ResumeModel
from app.main.model.job_post_model import JobPostModel
from app.main.model.recruiter_model import RecruiterModel
from app.main.model.candidate_model import CandidateModel
from app.main.model.job_resume_submissions_model import JobResumeSubmissionModel
from app.main.model.job_domain_model import JobDomainModel
from app.main.model.candidate_job_save_model import CandidateJobSavesModel
from app.main.model.candidate_education_model import CandidateEducationModel

from flask_jwt_extended.utils import get_jwt_identity
from app.main.util.custom_jwt import HR_only
from app.main.util.format_text import format_contract, format_education, format_salary
from app.main.util.response import json_serial, response_object
from app.main.util.data_processing import get_technical_skills, tree_matching_score_jd
from flask_restx import abort
from sqlalchemy import or_, func, and_
from app.main.util.data_processing import tree_matching_score
from app.main.util.thread_pool import ThreadPool

def email_company_name(s):
    s = re.sub('[áàảãạăắằẳẵặâấầẩẫậ]', 'a', s)
    s = re.sub('[ÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬ]', 'A', s)
    s = re.sub('[éèẻẽẹêếềểễệ]', 'e', s)
    s = re.sub('[ÉÈẺẼẸÊẾỀỂỄỆ]', 'E', s)
    s = re.sub('[óòỏõọôốồổỗộơớờởỡợ]', 'o', s)
    s = re.sub('[ÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢ]', 'O', s)
    s = re.sub('[íìỉĩị]', 'i', s)
    s = re.sub('[ÍÌỈĨỊ]', 'I', s)
    s = re.sub('[úùủũụưứừửữự]', 'u', s)
    s = re.sub('[ÚÙỦŨỤƯỨỪỬỮỰ]', 'U', s)
    s = re.sub('[ýỳỷỹỵ]', 'y', s)
    s = re.sub('[ÝỲỶỸỴ]', 'Y', s)
    s = re.sub('đ', 'd', s)
    s = re.sub('Đ', 'D', s)
    s = re.sub('[\W_]+', '', s)
    return s.lower()+"@gmail.com"

def no_accent_vietnamese(s):
    s = re.sub('[áàảãạăắằẳẵặâấầẩẫậ]', 'a', s)
    s = re.sub('[ÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬ]', 'A', s)
    s = re.sub('[éèẻẽẹêếềểễệ]', 'e', s)
    s = re.sub('[ÉÈẺẼẸÊẾỀỂỄỆ]', 'E', s)
    s = re.sub('[óòỏõọôốồổỗộơớờởỡợ]', 'o', s)
    s = re.sub('[ÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢ]', 'O', s)
    s = re.sub('[íìỉĩị]', 'i', s)
    s = re.sub('[ÍÌỈĨỊ]', 'I', s)
    s = re.sub('[úùủũụưứừửữự]', 'u', s)
    s = re.sub('[ÚÙỦŨỤƯỨỪỬỮỰ]', 'U', s)
    s = re.sub('[ýỳỷỹỵ]', 'y', s)
    s = re.sub('[ÝỲỶỸỴ]', 'Y', s)
    s = re.sub('đ', 'd', s)
    s = re.sub('Đ', 'D', s)
    return s.lower()
    
def insert_data(file, domain_id):
    job_domain = JobDomainModel.query.get(domain_id)
    if not job_domain:
        return {
            "code": 400,
            "message": "Không tìm thấy domain",
            "data": None
        }
    if file == None:
        return {
            "code": 400,
            "message": "Lổi file",
            "data": None
        }

    # load line in file
    file_input = open(file, 'r', encoding="utf-8")
    line = file_input.readlines()
    jsons = []
    for line in line:
        jsons.append(line.strip())
    file_input.close()

    if len(jsons)==0:
        return {
            "code": 400,
            "message": "File rổng",
            "data": None
        }
    provice = [ { "province_id": "92", "province_name": "Thành phố Cần Thơ", "province_type": "Thành phố Trung ương" }, { "province_id": "48", "province_name": "Thành phố Đà Nẵng", "province_type": "Thành phố Trung ương" }, { "province_id": "01", "province_name": "Thành phố Hà Nội", "province_type": "Thành phố Trung ương" }, { "province_id": "31", "province_name": "Thành phố Hải Phòng", "province_type": "Thành phố Trung ương" }, { "province_id": "79", "province_name": "Thành phố Hồ Chí Minh", "province_type": "Thành phố Trung ương" }, { "province_id": "89", "province_name": "Tỉnh An Giang", "province_type": "Tỉnh" }, { "province_id": "77", "province_name": "Tỉnh Bà Rịa - Vũng Tàu", "province_type": "Tỉnh" }, { "province_id": "95", "province_name": "Tỉnh Bạc Liêu", "province_type": "Tỉnh" }, { "province_id": "24", "province_name": "Tỉnh Bắc Giang", "province_type": "Tỉnh" }, { "province_id": "06", "province_name": "Tỉnh Bắc Kạn", "province_type": "Tỉnh" }, { "province_id": "27", "province_name": "Tỉnh Bắc Ninh", "province_type": "Tỉnh" }, { "province_id": "83", "province_name": "Tỉnh Bến Tre", "province_type": "Tỉnh" }, { "province_id": "74", "province_name": "Tỉnh Bình Dương", "province_type": "Tỉnh" }, { "province_id": "52", "province_name": "Tỉnh Bình Định", "province_type": "Tỉnh" }, { "province_id": "70", "province_name": "Tỉnh Bình Phước", "province_type": "Tỉnh" }, { "province_id": "60", "province_name": "Tỉnh Bình Thuận", "province_type": "Tỉnh" }, { "province_id": "96", "province_name": "Tỉnh Cà Mau", "province_type": "Tỉnh" }, { "province_id": "04", "province_name": "Tỉnh Cao Bằng", "province_type": "Tỉnh" }, { "province_id": "66", "province_name": "Tỉnh Đắk Lắk", "province_type": "Tỉnh" }, { "province_id": "67", "province_name": "Tỉnh Đắk Nông", "province_type": "Tỉnh" }, { "province_id": "11", "province_name": "Tỉnh Điện Biên", "province_type": "Tỉnh" }, { "province_id": "75", "province_name": "Tỉnh Đồng Nai", "province_type": "Tỉnh" }, { "province_id": "87", "province_name": "Tỉnh Đồng Tháp", "province_type": "Tỉnh" }, { "province_id": "64", "province_name": "Tỉnh Gia Lai", "province_type": "Tỉnh" }, { "province_id": "02", "province_name": "Tỉnh Hà Giang", "province_type": "Tỉnh" }, { "province_id": "35", "province_name": "Tỉnh Hà Nam", "province_type": "Tỉnh" }, { "province_id": "42", "province_name": "Tỉnh Hà Tĩnh", "province_type": "Tỉnh" }, { "province_id": "30", "province_name": "Tỉnh Hải Dương", "province_type": "Tỉnh" }, { "province_id": "93", "province_name": "Tỉnh Hậu Giang", "province_type": "Tỉnh" }, { "province_id": "17", "province_name": "Tỉnh Hoà Bình", "province_type": "Tỉnh" }, { "province_id": "33", "province_name": "Tỉnh Hưng Yên", "province_type": "Tỉnh" }, { "province_id": "56", "province_name": "Tỉnh Khánh Hòa", "province_type": "Tỉnh" }, { "province_id": "91", "province_name": "Tỉnh Kiên Giang", "province_type": "Tỉnh" }, { "province_id": "62", "province_name": "Tỉnh Kon Tum", "province_type": "Tỉnh" }, { "province_id": "12", "province_name": "Tỉnh Lai Châu", "province_type": "Tỉnh" }, { "province_id": "20", "province_name": "Tỉnh Lạng Sơn", "province_type": "Tỉnh" }, { "province_id": "10", "province_name": "Tỉnh Lào Cai", "province_type": "Tỉnh" }, { "province_id": "68", "province_name": "Tỉnh Lâm Đồng", "province_type": "Tỉnh" }, { "province_id": "80", "province_name": "Tỉnh Long An", "province_type": "Tỉnh" }, { "province_id": "36", "province_name": "Tỉnh Nam Định", "province_type": "Tỉnh" }, { "province_id": "40", "province_name": "Tỉnh Nghệ An", "province_type": "Tỉnh" }, { "province_id": "37", "province_name": "Tỉnh Ninh Bình", "province_type": "Tỉnh" }, { "province_id": "58", "province_name": "Tỉnh Ninh Thuận", "province_type": "Tỉnh" }, { "province_id": "25", "province_name": "Tỉnh Phú Thọ", "province_type": "Tỉnh" }, { "province_id": "54", "province_name": "Tỉnh Phú Yên", "province_type": "Tỉnh" }, { "province_id": "44", "province_name": "Tỉnh Quảng Bình", "province_type": "Tỉnh" }, { "province_id": "49", "province_name": "Tỉnh Quảng Nam", "province_type": "Tỉnh" }, { "province_id": "51", "province_name": "Tỉnh Quảng Ngãi", "province_type": "Tỉnh" }, { "province_id": "22", "province_name": "Tỉnh Quảng Ninh", "province_type": "Tỉnh" }, { "province_id": "45", "province_name": "Tỉnh Quảng Trị", "province_type": "Tỉnh" }, { "province_id": "94", "province_name": "Tỉnh Sóc Trăng", "province_type": "Tỉnh" }, { "province_id": "14", "province_name": "Tỉnh Sơn La", "province_type": "Tỉnh" }, { "province_id": "72", "province_name": "Tỉnh Tây Ninh", "province_type": "Tỉnh" }, { "province_id": "34", "province_name": "Tỉnh Thái Bình", "province_type": "Tỉnh" }, { "province_id": "19", "province_name": "Tỉnh Thái Nguyên", "province_type": "Tỉnh" }, { "province_id": "38", "province_name": "Tỉnh Thanh Hóa", "province_type": "Tỉnh" }, { "province_id": "46", "province_name": "Tỉnh Thừa Thiên Huế", "province_type": "Tỉnh" }, { "province_id": "82", "province_name": "Tỉnh Tiền Giang", "province_type": "Tỉnh" }, { "province_id": "84", "province_name": "Tỉnh Trà Vinh", "province_type": "Tỉnh" }, { "province_id": "08", "province_name": "Tỉnh Tuyên Quang", "province_type": "Tỉnh" }, { "province_id": "86", "province_name": "Tỉnh Vĩnh Long", "province_type": "Tỉnh" }, { "province_id": "26", "province_name": "Tỉnh Vĩnh Phúc", "province_type": "Tỉnh" }, { "province_id": "15", "province_name": "Tỉnh Yên Bái", "province_type": "Tỉnh" } ]
    for json_str in jsons:
        data = json.loads(json_str)
        #add jobs to db
        try:
            firstJob = ""
            provice_ids = []
            for provice_text in data['jobLocation']:
                for pro in provice:
                    if str(provice_text['address']['addressRegion']).lower() in no_accent_vietnamese(pro['province_name']):
                        provice_ids.append(pro['province_id'])
                    if firstJob =="":
                        firstJob = str(provice_text['address']['addressRegion'])
            if len(provice_ids) == 0:
                provice_ids = ["79"]

            dealine = data['validThrough'] + "T23:59:03.163Z"
            parse_deadline = dateutil.parser.isoparse(dealine)
            
            company_name = data['hiringOrganization']['name']
            email_genreral = email_company_name(company_name)

            recruiter = RecruiterModel.query.filter_by(email = email_genreral).first()
            print(email_genreral)

            new_account = None
            if not recruiter:
                print("insert new recuiter: "+str(email_genreral))
                new_account = RecruiterModel(
                    email=email_genreral,
                    password="angel1999",
                    phone = None,
                    full_name = company_name,
                    gender = True,
                    access_token=True,
                    registered_on=datetime.datetime.utcnow(),
                    confirmed = True,
                    confirmed_on = datetime.datetime.utcnow()
                )

                response = requests.get(data['hiringOrganization']['logo'])
                
                logo_path = "temp/"+company_name+".png"
                file = open(logo_path, "wb")
                file.write(response.content)
                file.close()

                executor = ThreadPool.instance().executor
                logo_url  = None
                logo = executor.submit(Firebase().upload, logo_path)
                logo_url = logo.result()

                company_news = CompanyModel(
                    name=company_name, 
                    location=firstJob,
                    phone=None,
                    email=email_genreral,
                    website=None,
                    description=data['hiringOrganization']['description'],
                    logo=logo_url.public_url,
                    background=None
                )
                db.session.add(company_news)
                db.session.commit()
                
                # company_search = CompanyModel.query.filter_by(name=company_name).first()
                # recruiter.company_id = company_search.id

                new_account.company_id = company_news.id
                db.session.add(new_account)
                db.session.commit()
                recruiter = new_account


            if new_account ==None and not recruiter:
                continue
            
            txt = " ".join([data['experienceRequirements'],data['description']])

            executor = ThreadPool.instance().executor
            domain_skills_res = executor.submit(
                get_technical_skills, job_domain.alternative_name, txt)
            general_skills_res = executor.submit(get_technical_skills, "general", txt)
            soft_skills_res = executor.submit(get_technical_skills, "softskill", txt)

            (domain_skills, _) = domain_skills_res.result()
            (general_skills, _) = general_skills_res.result()
            (soft_skills, _) = soft_skills_res.result()
            
            new_post = JobPostModel(
                recruiter_id = recruiter.id,
                job_domain_id=domain_id,
                description_text=data['description'],
                requirement_text=data['experienceRequirements'],
                benefit_text=data['jobBenefits'],
                job_title=data['title'],
                contract_type=0,
                min_salary=data['min_salary'],
                max_salary=data['max_salary'],
                amount=0,
                education_level= 0,
                province_id= ",".join(provice_ids),
                domain_skills='|'.join(domain_skills).replace("|True|","").replace("True|","").replace("|True","").replace("True",""),
                general_skills='|'.join(general_skills).replace("|True|","").replace("True|","").replace("|True","").replace("True",""),
                soft_skills='|'.join(soft_skills).replace("|True|","").replace("True|","").replace("|True","").replace("True",""),
                deadline=parse_deadline
            )

            # recruiter.job_posts.append(new_post)
            # job_domain.job_posts.append(new_post)
            # db.session.add(recruiter)
            # log_time.sleep(3)
            db.session.add(new_post)
            db.session.commit()
            # log_time.sleep(3)

            print("### insert one job")
        except Exception as ex:
            print(str(ex.args))
