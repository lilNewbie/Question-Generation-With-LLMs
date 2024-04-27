from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Course, PDF_link, QAs, Tests
from . import db
import json
import PyPDF2
import io
import requests
from pprint import pprint
from lmqg import TransformersQG
import gdown
import os
from pypdf import PdfReader

op_path = '/pdfs'
# def generator(pdfs, model):
#     text=''
#     for i in pdfs:
#         r = requests.get(i)
#         f = io.BytesIO(r.content)
#         reader = PyPDF2.PdfReader(f)
#         pages = reader.pages
#         text = ' '.join([page.extract_text() for page in pages])
#     question_answer = model.generate_qa(text)
#     return question_answer[0][0], question_answer[0][1]


views = Blueprint('views', __name__)

@views.route('/home', methods=['POST','GET'])
@login_required
def home():
    if request.method=='POST':
        course_id = request.form.get('course_id')
        course_name = request.form.get('course_name')
        pdf_link = request.form.get('pdf_link')
        pdf_name = request.form.get('pdf_name')
        if len(course_id) < 1 or len(course_name) < 1 or len(pdf_link) < 1:
            flash('Data is too short', category='error')
        else:
            #CHECK IF COURSE EXISTS IN DATABASE
            existing_course = Course.query.filter_by(course_id=course_id, user_id=current_user.id).first()
            
            if existing_course:
                print(existing_course.user_id)
                pass
            else:
                new_course = Course(course_id=course_id, course_name=course_name, user_id=current_user.id)
                db.session.add(new_course)
                
                db.session.commit()
                print(new_course.user_id)

            # print(current_user.courses)
            #ADD THE PDF
            existing_pdf = PDF_link.query.filter_by(link=pdf_link, course_id=course_id, user_id=current_user.id).first()
            if existing_pdf:
                # print(existing_pdf.user_id)
                pass
            else:
                new_pdf = PDF_link(link=pdf_link, pdf_name=pdf_name, course_id=course_id, user_id=current_user.id)
                db.session.add(new_pdf)
                db.session.commit()
            # p = existing_course.pdf
            # print(p[0].link)
            flash('PDF added', category='success')
    return render_template('home.html', user=current_user)



@views.route('/tests', methods=['POST','GET'])
@login_required
def generate_test():
    new_qa = None
    new_test = None
    if request.method=='POST':
        test_name = request.form.get('test_name')
        n_qs = request.form.get('n_questions')
        course_id = request.form.get('course_name')
        selected_pdf_ids = request.form.getlist('my_checkboxes')
        selected_pdfs = [i.link for i in current_user.pdfs if str(i.id) in selected_pdf_ids]
        
        existing_test = Tests.query.filter_by(test_name=test_name, course_id=course_id, user_id=current_user.id).first()
        if existing_test:
            flash('Change test name', category='error')
            pass
        else:
            new_test = Tests(test_name=test_name, user_id=current_user.id, course_id=course_id)
            db.session.add(new_test)
            db.session.commit()
            flash('Test added', category='success')

            new_qa = None
            model = TransformersQG('lmqg/t5-base-squad-qag')

            for i in range(int(n_qs)):
                text=''
                for j in selected_pdfs:
                    doc = PdfReader('website\pdfs\CHEESECAKE.pdf')
                    
                    for page in doc.pages:
                        print(page)
                        text = page.extract_text()
                if text!=[]:
                    question_answer = model.generate_qa(text[:450])
                    q,a =  question_answer[0][0], question_answer[0][1]

                    new_qa = QAs(question=q, answer=a, test_id=new_test.id)
                    db.session.add(new_qa)
                    db.session.commit()
        

    return render_template('tests.html', user=current_user, qnas=new_qa, ntest=new_test)




@views.route('/delete-course', methods=['POST'])
def delete_course():
    data = json.loads(request.data)
    courseId = data['courseId']
    course = Course.query.get(courseId)
    if course:
        if course.user_id==current_user.id:
            db.session.delete(course)
            db.session.commit()
    return jsonify({})

@views.route('/delete-pdf', methods=['POST'])
def delete_pdf():
    data = json.loads(request.data)
    pdfId = data['pdfId']
    pdf = PDF_link.query.get(pdfId)
    if pdf:
        if pdf.user_id==current_user.id:
            db.session.delete(pdf)
            db.session.commit()
    return jsonify({})