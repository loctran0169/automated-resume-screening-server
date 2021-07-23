from app.main.util.response import response_object
from app.main import db
from app.main.model.special_skills_model import SpecialSkillsModel


def get_all_company():
    return SpecialSkillsModel.query.all()

def get_a_skills_by_name(name, is_main_skill):
    print(name)
    print(is_main_skill)
    if name == None or name.strip() == "":
        if is_main_skill == "true" or is_main_skill == "True":
            query = SpecialSkillsModel.query.filter(SpecialSkillsModel.is_main.isnot(None)).filter(SpecialSkillsModel.is_soft==False)
        else:
            query = SpecialSkillsModel.query.filter(SpecialSkillsModel.is_soft==False)
    else:
        if is_main_skill == "true" or is_main_skill == "True":
            query = SpecialSkillsModel.query.filter(SpecialSkillsModel.name.contains(name),SpecialSkillsModel.is_main.isnot(None)).filter(SpecialSkillsModel.is_soft==False)
        else:
            query = SpecialSkillsModel.query.filter(SpecialSkillsModel.name.contains(name)).filter(SpecialSkillsModel.is_soft==False)

    skills = [ com for com in query]
    
    return skills

def get_soft_skills_by_name(name):
    print('soft skill: '+ str(name))
    if name == None or name.strip() == "":
        query = SpecialSkillsModel.query.filter(SpecialSkillsModel.is_soft==True)
    else:
        query = SpecialSkillsModel.query.filter(SpecialSkillsModel.name.contains(name)).filter(SpecialSkillsModel.is_soft==True)

    skills = [ com for com in query]
    
    return skills

def add_new_skill(name):    
    skill = SpecialSkillsModel(
        name=name
    )
    try:
        db.session.add(skill)
        db.session.commit()
        return response_object(200, "Add skill success|Thêm skill thành công", data=skill.to_json())
    except Exception as ex:
        return response_object(200, "Add skill fail|Thêm skill thất bại", data=None)

def add_new_soft_skill(name):    
    skill = SpecialSkillsModel(
        name = name,
        is_soft = True
    )
    try:
        db.session.add(skill)
        db.session.commit()
        return response_object(200, "Add skill success|Thêm skill thành công", data=skill.to_json())
    except Exception as ex:
        return response_object(200, "Add skill fail|Thêm skill thất bại", data=None)