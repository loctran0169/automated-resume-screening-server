import codecs
import pickle
import cv2
from nltk.corpus.reader import twitter
from pdf2image import convert_from_path
import pytesseract
import os
import glob
import re
from nltk import word_tokenize
from nltk.corpus import stopwords
import json
from app.main.util.data_processing import generate_graph_tree_with, get_technical_skills
from app.main.util.regex_helper import RegexHelper
import cloudmersive_convert_api_client as convert
from cloudmersive_convert_api_client.rest import ApiException
import base64

stop_words = set(stopwords.words('english'))

cue_words = open("preprocess/cue_word.txt", "r").readlines()
cue_words = [re.sub(r"\n", "", c) for c in cue_words]
cue_words = set(cue_words)

cue_phrases = open("preprocess/cue_phrases.txt", "r").readlines()
cue_phrases = [re.sub(r"\n", "", c) for c in cue_phrases]

configuration = convert.Configuration()
configuration.api_key['Apikey'] = '5cede973-e1ef-437c-a881-e72c52542b78'

pytesseract.pytesseract.tesseract_cmd = 'C:/Users/LQTPL/AppData/Local/Tesseract-OCR/tesseract.exe'

class ResumeExtractor:

    resume_local_path = None
    result_dict = None 

    def __init__(self, resume_local_path, is_pdf):
        self.resume_local_path = resume_local_path
        self.is_pdf = is_pdf
        self.resultDict = dict()


    def extract(self):
        """
        Return: the dictionary of result.
        'experiences', 'educations', 'skills'
        """

        self.result_dict = cv_segmentation(self.resume_local_path, self.is_pdf)
        return self.result_dict


def pre_processing(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    threshold_img = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    return threshold_img

def parse_text(threshold_img):
    tesseract_config = r'--oem 3 --psm 1'
    details = pytesseract.image_to_data(threshold_img, output_type=pytesseract.Output.DICT, config=tesseract_config, lang="eng")

    return details

def remove_temp_files(directory):
    files = glob.glob(directory)
    for f in files:
        os.remove(f)

def format_text(details):
    parse_text = []
    word_list = []
    last_word = ''
    for word in details['text']:
        if word != '':
            word_list.append(word)
            last_word = word
        if (last_word != '' and word == '') or (word == details['text'][-1]):
            parse_text.append(word_list)
            word_list = []

    return parse_text

def convert_pdf_to_jpg(filename):
    remove_temp_files('temp/*')


    # TODO - ERROR: Remove for running on window
    images = convert_from_path(filename)
    # images = convert_from_path(filename, poppler_path="D:\KLTN\libs\poppler-21.03.0\Library\bin")

    for img in images:
        index = images.index(img)

        img.save('temp/CV_{}.jpg'.format(index), 'JPEG')

def convert_word_to_jpg(filename):
    remove_temp_files('temp/*')

    api_instance = convert.ConvertDocumentApi(convert.ApiClient(configuration))

    try:
        api_response = api_instance.convert_document_docx_to_jpg(filename)

        images = api_response.jpg_result_pages

        for image in images:
            img = image.content
            page = image.page_number

            with open("temp/CV_{}.jpg".format(page), "wb") as fh:
                fh.write(base64.decodebytes(bytes(img, encoding="utf8")))
            fh.close()

    except ApiException as e:
        print("Exception: %s\n" %e)


def parse_pdf(local_cv_path, is_pdf):
    remove_words = []
    remove_keys = []
    with open("preprocess/REMOVE_WORD.txt", "r") as rm_file:
        remove_words = rm_file.readlines()
        remove_words = [ re.sub(r"\n", "", remove_word) for remove_word in remove_words ]

    if is_pdf:
        convert_pdf_to_jpg(local_cv_path)
    else:
        convert_word_to_jpg(local_cv_path)

    img_directory = "temp"
    sentences = []

    for img in os.listdir(img_directory):
        img_name = os.fsdecode(img)

        if img_name != '.gitignore':
            img_fname = os.path.join(img_directory, img_name)

            image = cv2.imread(img_fname)

            thresholds_image = pre_processing(image)

            parsed_data = parse_text(thresholds_image)

            arranged_text = format_text(parsed_data)
            arranged_text = [ sen for sen in arranged_text if len(sen) > 0 ]

            for sen in arranged_text:
                sentences.append(' '.join(sen).strip())

    sentences = [re.sub(r"(protected data)|(protected@topcv.vn)", "", sen) for sen in sentences]
    sentences = [sen for sen in sentences if len(sen) > 0]

    for w in remove_words:
        sentences = [sentence for sentence in sentences if w not in sentence]

    rm_file.close()

    return sentences


def process_raw_text(sentences):
    sentences = [ (sen.lower(), i) for (sen, i) in sentences ]
    sentences = [ (re.sub(r"[^a-zA-Z\s]+", "", sen), i) for (sen, i) in sentences ]

    sentences = [ (word_tokenize(sen), i) for (sen, i) in sentences ]
    sentences = [ ([word for word in sen if word not in stop_words and len(word) > 1], i) for (sen, i) in sentences ]

    sentences = [ (' '.join(sen), i) for (sen, i) in sentences if len(sen) > 0 ]

    return sentences

def get_topic(educations, experiences, skills, cue_word):
    tmp = cue_word.split()
    if cue_word in educations:
        return "EDUCATION"
    elif cue_word in experiences:
        return "EXPERIENCE"
    elif cue_word in skills:
        return "SKILL"
    elif len(tmp) == 2:
        if tmp[0] in educations or tmp[1] in educations:
            return "EDUCATION"
        elif tmp[0] in experiences or tmp[1] in experiences:
            return "EXPERIENCE"
        elif tmp[0] in skills or tmp[1] in skills:
            return "SKILL"
        else:
            return ""
    else:
        return ""

def get_general_technical_skills(text):
    # hardcode general domain for extracting as many skills as posible.
    return get_technical_skills('general', text, modules="syntactic")

def get_soft_skills(text):
    return get_technical_skills('softskill', text)


def get_links(text):
    """
    Get links.
    """
    github = RegexHelper.find_github_link(text)
    twitter = RegexHelper.find_twitter_link(text)
    facebook = RegexHelper.find_fb_link(text)
    linkedin = RegexHelper.find_linkedin_link(text)
    phone = RegexHelper.find_phone_number(text)
    email = RegexHelper.find_email(text)

    return {
        "github": github,
        "twitter": twitter,
        "facebook": facebook,
        "linkedin": linkedin,
        "phone": phone,
        "email": email,
    }


def cv_segmentation(local_cv_path, is_pdf):
    sentences = parse_pdf(local_cv_path, is_pdf)

    print(sentences)
    educations_cue = experiences_cue = skills_cue = awards_cue = certifications_cue = []

    with open('preprocess/topic.json') as json_file:
        data = json.load(json_file)
        educations_cue = data["Education"]
        experiences_cue = data["Experience"]
        skills_cue = data["Skills"]
        # awards_cue = data["Awards"]
        # certifications_cue = data["Certification"]

    index_sentences = [(sentences[i], i) for i in range(len(sentences))]
    index_sentences = process_raw_text(index_sentences)

    topics = []
    cur_topic = ""

    for (sen, id) in index_sentences:
        tmp = sen.split()
        length = len(tmp)
        if (length == 1 and sen.lower() in cue_words) or \
        (length == 2 and (tmp[0] in cue_words or tmp[1] in cue_words)) or \
        (length > 1 and sen.lower() in cue_phrases):
            cur_topic = get_topic(educations_cue, experiences_cue, skills_cue, sen)
            topics.append((id,cur_topic))
        else:
            topics.append((id, cur_topic))

    educations = [sentences[topic[0]] for topic in topics if topic[1] == 'EDUCATION']
    experiences = [sentences[topic[0]] for topic in topics if topic[1] == 'EXPERIENCE']
    skills = [sentences[topic[0]] for topic in topics if topic[1] == 'SKILL']
    # awards = [sentences[topic[0]] for topic in topics if topic[1] == 'AWARD']
    # certifications = [sentences[topic[0]] for topic in topics if topic[1] == 'CERTIFICATION']


    (tech_skills, _) = get_general_technical_skills('\n'.join(sentences))
    (soft_skills, _) = get_soft_skills('\n'.join(sentences))

    (general_skills_graph, _) = generate_graph_tree_with(domain='general', skills=tech_skills)
    (soft_skills_graph, _) = generate_graph_tree_with(domain='softskill', skills=soft_skills)


    pickled_general = codecs.encode(pickle.dumps(general_skills_graph), "base64").decode()
    pickled_softskill = codecs.encode(pickle.dumps(soft_skills_graph), "base64").decode()
    
    links = get_links('\n'.join(sentences))

    return {
        'educations': '\n'.join(educations),
        'experiences': '\n'.join(experiences),
        'tech_skills': tech_skills,
        'soft_skills': soft_skills,
        'skill_segmentation': '\n'.join(skills),
        "github": links['github'],
        "twitter": links['twitter'],
        "facebook": links['facebook'],
        "linkedin": links['linkedin'],
        "email": links['email'],
        "phone": links['phone'],
        "graph_general" : pickled_general,
        "graph_softskill" : pickled_softskill
        # 'award': '\n'.join(awards),
    }
