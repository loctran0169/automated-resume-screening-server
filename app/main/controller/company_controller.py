import os
import uuid

from flask_restx.fields import String
from app.main.util.resume_extractor import remove_temp_files
from flask_jwt_extended.utils import get_jwt_identity
from app.main.util.response import response_object
from app.main.util.custom_jwt import HR_only
from flask.globals import request
from app.main.service.company_service import add_new_company, get_a_company_by_name, update_company
from flask_restx import Resource
from ..util.dto import CompanyDto
from app.main.util.data_processing import tree_matching_score_jd

api = CompanyDto.api
_company = CompanyDto.company

search_parser = api.parser()
search_parser.add_argument("name", type=str, location="args", required=False)
@api.route('/search')
@api.response(404, 'Company not found.')
class CompanyFind(Resource):
    @api.doc('Find list companies by name')
    @api.expect(search_parser)
    def get(self):
        '''get list companies by name'''
        name = request.args.get('name')
        page = request.args.get('page', 1, type=int)
        ##
        post_text = "Roles and Responsibilities :- Lead software development by closely working with software engineers and stakeholders.- Design and architecture to enable secure, scalable and maintainable software- Ensure software products delivered to the customers meet the specified Quality Goals- Work with cross-functional teams to ensure quality throughout the software development lifecycle (SDLC)- Interpret and translate business needs to technical requirements and accurate estimates- Apply deep technical expertise to resolve challenging programming and design problems- Ensure high quality software is delivered by following engineering practices like peer code reviews, code standards, and unit testing- Contribute to technical roadmap and technical debt elimination, balancing time, resource, and quality constraints to achieve business and strategic goals- Evaluate and recommend tools, technologies and processes to ensure the highest quality and performance is achievedDesired Candidate Profile 5+ years of overall industry experience in the designing and developing software applications2+ years of experience in leading, mentoring and managing development teamsExcellent communication skills, ability to state complex subjects simply for a variety of audiencesShould be a self-starter who can come up to speed quickly and identify the problems that needs to be solvedExperience and well-verse in leading in an Agile development environment.Knowledge and experience with web technology stack, cloud computing and database technologiesDeep understanding of .Net and Angular application architectures and technology stacksAbility to learn new technical skills quicklyHigh level of attention to detail, creative problem solving, and capacity to drive the team Positive, collaborative team leader with excellent verbal and written communication skillsShould have experience in team handling"
        post_text2 = "Job DescriptionPlay the role of Project Manager for the embedded projects like platform software components and Test developments projectsTo aware and track complete contract ,scope of deliveries, Time line for all Supplier deliverablesParticipate in regular calls ( Bug scrubs calls, work package calls , Management calls) with suppliers in different time zones push the suppliers to get the deliverables on time.Responsible for people management,Project managementBenchmarking performance,quality matrices, and take initiatives to improve the sameShall be able to interact with all stake holders with excellent communications skills and Escalate to concerned stake holders on need basisRequired Candidate profileQualificationsBE/B.Tech or ME/M Tech in electronics or Computer Science/EEE with 6 to 12 years of Software industry experience with aspiration to grow in Project Management Work Experience on Embedded Linux,Android and Project management experience in handling platform projects is added advantageProject Management skills, Experience in handling team sizes of bigger capacity is added advantage"
        resume_text = "Bình N. WEBSITE FULLSTACK DEVELOPER Website, Backend Developments PHP Ruby Ruby On Rails, Django Python, Go lang VueJs 2.0, React JS MYSQL Javascript Basic, Jquery, HTML5, CSS Laravel, Codeigniter, Zend, Cake, Yii, Bootsrap Unix, Linux Git Agile && Scrum C/C++, Java SE/EE NỀN TẢNG TUYỂN DỤNG NHÂN SỰ HÀNG ĐẦU VIỆT NAM Ứng viên Bình N. | Nguồn tuyendung.topcv.vn Contact information Date of birth 27/09/1992 Gender Male Phone [protected data] Email protected@topcv.vn Address Hanoi, Vietnam Website [protected data] Skills Education University of Engineering and Technology Major: Software Engineer GPA: 2.78/4.0 - Algorithms and algorithms - Security mechanism and role management Oct 2010 - 2014 Employment History Rikkeisoft Inc Fullstack developer Rikkeisoft is a great company on outsourcing for japan software market, i work on Global division at Senior developer.Projest that i work on is Ricode platform. 1) Ricode is open programing platform with website interactive with student and who love programing. URL: https://ricode.rikkei.org/ 2) Senior backend developer, write backend system for application, projects are outsource project for Japan and Viet Nam. - Position: Technical leader and project manager - Tech: Docker , RoR, Django, Mysql - Tools: Sublime text, Docker tools My work is build an compiler tool and tracking project progress, maintain task and basic design. 2019 - 2020 Wefit Fullstack developer Wefit is a great startup where I have learned about expertise and soft skills - Position: Fullstack developer . - Task: 1 ) Integrate payment payment with Napas payment. 2 ) Blog website introduces and advertises news and fashion trends among young people. 2018 - March 2019 Docker - AWS Services Honors & Awards - Certificate of Center For Cooperating And Transferring Knowledge 2014 - With Assignment in university we receive Consolation prize written android app to help kids learning math 2013-2014 - App on top of shopify for more than haft year Sales Pop https://apps.shopify.com/sales-pop 2016 - Tech:- Ruby on rails, Ruby, Laravel, Docker, Kubernetes, Postgree SQL - Tools: Sublime text, Docker, kubernetes, google cloud VTD, DCV jsc Fullstack developer I working at here like a full stack developer and on site partner developer at panasonic and Innovatube. Projects: 1) Write plugins and maintain source code for project. Specifically plugins for redmine at Panasonic inc. 2) Write backend side on a project about construction engineers and management contractors at Innovatube inc. - Position: Senior Dev PHP, Rails - Tech: Rails plugins, PHP, Laravel, MySQL, HTML, JS - Tools: Sublime text, July 2017 - June 2018 Free lancer job Software Developer - I was a freelancer at that time working at home and work at company - Develop and Build website for product: izziedu.vn, Cenports Inc, pentalog, ototreem.vn, property.starktech.jp - Some product about writing and maintain code: izziedu,, Video sharing for learning. - Position: Freelancer - Technology: + E-Learning and Web streaming + Languages: PHP, Git Commit, Mysql, Ruby On Rails - Framework: Laravel, Zend, CodeIgniter, Symfony - Tools: Sublimetext, visual, PHP Storm Jan 2017 - June 2017 Beeketing Software Developer - Task : Develop and Build web app extension for shopify partner - Working with high perfective and focus to deliver best app to user.My work is reading requirement and learning to be a full stack developer, understand about how shopify working with ecommerce skills set - Technology: + Languages: PHP, JSON, Git Commit + Framework: Symfony, Vue.js - My app was created at here :Sales Pop at Shopify: https://apps.shopify.com/sales-pop. This app is one of lucky app when become a top one free app for 2017 August 2016 - Jan 2017 Altplus Inc Software Developer 1) Develop and Build the Server side for Livmo app - Grab content, news from websites to building RSS index server - Impressive and design back to requirements - Technology: + Languages: Ruby, SQL + Framework: Ruby On Rails 2015 - August 2016 + Tools: Git, MySQL Workbench 2) Develop and Build the Server side for game Derby Road: Logic process game about Horse racing, help to response request to client - Working with client, receive requirements and design back. - Technology: +Languages: PHP, JSON, Git Commit +Framework: Restful . Laravel SmartOsc Intership - Develop the Ecommerce Website using Code-igniter 2.0 - Create extensions for Magento websites, sample extension cover business activities about ecommerce website. - Technology: + Language: PHP, Javascript, CSS, SQL + Framework : Code Igniter, Laravel, Magento June 2014 - 2014 Activities SmartOsc Intership Become a fresher class learning and working to create ecomerce website by CodeIgniter and Magento. - Develop the Ecommerce Website using Code-igniter 2.0 - Create extensions for Magento websites, sample extension cover business activities about ecommerce website. Technology: + Language: PHP, Javascript, CSS, SQL + Framework : Magento, Code Igniter, Laravel 2014 - 2014 Go backpacking Team member One of my favorites hobbies is to go sightseeing and keep balance in life Ha noi Kendo && Ha noi Tai chi club Team member I do Martial arts for keep balance between healthy and works Library club for students Volunteer I like reading book, listen music and cultures of region in the worlds. Meeting people and travel. CID: 1a773efcfa3991b7aaa48a33839eb7af TopCV - Nền tảng tuyển dụng nhân sự hàng đầu Việt Nam - ©tuyetnodpucngv.t.ovpncv.vn"

        domain_dict = tree_matching_score_jd(post_text, post_text2, 'pm')
        # print(domain_dict['post1_skills'])
        # print(domain_dict['post2_skills'])
        print(domain_dict['score'])
        ##
        companies, has_next = get_a_company_by_name(name, page)

        if not companies:
            return response_object()
        else:
            return response_object(200, "Thành công.", data=[company.to_json() for company in companies], pagination={"has_next": has_next})


@api.route('')
class Company(Resource):
    @api.doc('add a new company')
    @HR_only
    def post(self):
        files = request.files
        data = request.form

        remove_temp_files('temp/*')

        logo = files.get("logo", None)
        background = files.get("background", None)

        logo_file = background_file = None

        if logo:
            logo_file = os.path.join("temp", "{}_{}_logo.png").format(data['name'], str(uuid.uuid4().hex))
            logo.save(logo_file)

        if background:
            background_file = os.path.join("temp", "{}_{}_background.png").format(data['name'], str(uuid.uuid4().hex)) 
            background.save(background_file)

        identity = get_jwt_identity()
        email = identity['email']

        return add_new_company(data, logo_file, background_file, email)


@api.route('/<int:id>/update')
class CompanyUpdate(Resource):
    @api.doc("update HR company")
    @HR_only
    def put(self, id):
        identity = get_jwt_identity()
        email = identity['email']
        
        return update_company(id, email)