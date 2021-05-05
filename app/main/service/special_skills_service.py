from app.main.util.response import response_object
from app.main import db
from app.main.model.special_skills_model import SpecialSkillsModel


def get_all_company():
    return SpecialSkillsModel.query.all()

def get_a_skills_by_name(name, is_main_skill,page, page_size):
    if name == None:
        if is_main_skill:
            query = SpecialSkillsModel.query.filter(SpecialSkillsModel.is_main==True).paginate(page, page_size, error_out=False)
        else:
            query = SpecialSkillsModel.query.paginate(page, page_size, error_out=False)
    else:
        if is_main_skill:
            query = SpecialSkillsModel.query.filter(SpecialSkillsModel.name.contains(name),SpecialSkillsModel.is_main==True).paginate(page, page_size, error_out=False)
        else:
            query = SpecialSkillsModel.query.filter(SpecialSkillsModel.name.contains(name)).paginate(page, page_size, error_out=False)

    skills = [ com for com in query.items]
    
    return skills

def add_new_skill(name):    
    skill = SpecialSkillsModel(
        name=name
    )
    try:
        db.session.add(skill)
        db.session.commit()
        return response_object(200, "Thêm skill thành công", data=skill.to_json())
    except Exception as ex:
        return response_object(200, "Thêm skill thất bại", data=None)