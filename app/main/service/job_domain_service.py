from app.main.model.special_skills_model import SpecialSkillsModel
from app.main.util.response import response_object
from app.main.model.job_domain_model import JobDomainModel
from app.main import db

def get_all_domain():
    domains = JobDomainModel.query.all()
    domains = [ d.to_json() for d in domains ]

    return response_object(code=200, message="Lấy danh sách domain thành công", data=domains)

def add_new_skill_to_domain(data):  
    domain =  JobDomainModel.query.get(data['domain_id'])
    if not domain:
        return response_object(200, "Domain không tồn tại", data=None)

    skill =   SpecialSkillsModel.query.get(data['skill_id'])
    if not skill:
        return response_object(200, "Skill không tồn tại", data=None)

    try:
        domain.skills.append(skill)
        db.session.add(domain)
        db.session.commit()
        return response_object(200, "Thêm skill thành công", data=skill.to_json())
    except Exception as ex:
        return response_object(200, "Thêm skill thất bại", data=None)