from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Course, PDF_link, QAs, Tests
from . import db
import json
import os
from pypdf import PdfReader
from lmqg import TransformersQG
import gdown

op_path = 'pdfs'  # Directory to store downloaded PDFs
if not os.path.exists(op_path):
    os.makedirs(op_path)

views = Blueprint('views', __name__)

def get_direct_gdrive_link(gdrive_url):
    """Convert a Google Drive shareable link to a direct download link."""
    try:
        if "drive.google.com" in gdrive_url:
            file_id = gdrive_url.split('/d/')[1].split('/')[0]
            return f"https://drive.google.com/uc?id={file_id}"
        return gdrive_url
    except Exception as e:
        print(f"Error processing Google Drive link: {e}")
        return None

def download_pdf_from_drive(link, filename):
    """Download a PDF file from Google Drive and ensure it has the correct extension."""
    try:
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'  # Add .pdf extension if not present
        output_path = os.path.join(op_path, filename)
        gdown.download(link, output_path, quiet=False)
        return output_path if os.path.exists(output_path) else None
    except Exception as e:
        print(f"Error downloading PDF: {e}")
        return None

def is_valid_pdf(file_path):
    """Check if the file is a valid PDF by reading its header."""
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)
        return header == b'%PDF'
    except Exception as e:
        print(f"File validation error: {e}")
        return False

def is_non_empty_file(file_path):
    """Check if the file exists and is not empty."""
    return os.path.exists(file_path) and os.path.getsize(file_path) > 0

@views.route('/home', methods=['POST', 'GET'])
@login_required
def home():
    if request.method == 'POST':
        course_id = request.form.get('course_id')
        course_name = request.form.get('course_name')
        pdf_link = request.form.get('pdf_link')
        pdf_name = request.form.get('pdf_name')

        if not all([course_id, course_name, pdf_link, pdf_name]):
            flash('All fields are required!', category='error')
            return render_template('home.html', user=current_user)

        # Check if course exists in the database
        existing_course = Course.query.filter_by(course_id=course_id, user_id=current_user.id).first()
        if not existing_course:
            new_course = Course(course_id=course_id, course_name=course_name, user_id=current_user.id)
            db.session.add(new_course)
            db.session.commit()

        # Check if PDF exists in the database
        existing_pdf = PDF_link.query.filter_by(link=pdf_link, course_id=course_id, user_id=current_user.id).first()
        if not existing_pdf:
            direct_link = get_direct_gdrive_link(pdf_link)
            pdf_path = download_pdf_from_drive(direct_link, pdf_name) if direct_link else None
            if pdf_path and is_non_empty_file(pdf_path) and is_valid_pdf(pdf_path):
                new_pdf = PDF_link(link=pdf_link, pdf_name=pdf_name, course_id=course_id, user_id=current_user.id)
                db.session.add(new_pdf)
                db.session.commit()
                flash('PDF added successfully!', category='success')
            else:
                flash('Failed to download or validate the PDF. Check the link and try again.', category='error')
        else:
            flash('PDF already exists.', category='info')

    return render_template('home.html', user=current_user)

@views.route('/tests', methods=['POST', 'GET'])
@login_required
def generate_test():
    new_qa = None
    new_test = None
    if request.method == 'POST':
        test_name = request.form.get('test_name')
        n_qs = int(request.form.get('n_questions') or 0)
        course_id = request.form.get('course_name')
        selected_pdf_ids = request.form.getlist('my_checkboxes')

        if not all([test_name, n_qs, course_id, selected_pdf_ids]):
            flash('All fields are required!', category='error')
            return render_template('tests.html', user=current_user)

        existing_test = Tests.query.filter_by(test_name=test_name, course_id=course_id, user_id=current_user.id).first()
        if existing_test:
            flash('Test name already exists. Choose a different name.', category='error')
        else:
            new_test = Tests(test_name=test_name, user_id=current_user.id, course_id=course_id)
            db.session.add(new_test)
            db.session.commit()

            model = TransformersQG('lmqg/t5-base-squad-qag')
            for pdf_id in selected_pdf_ids:
                pdf = PDF_link.query.get(pdf_id)
                if not pdf:
                    continue

                try:
                    pdf_path = os.path.join(op_path, pdf.pdf_name+".pdf")
                    print(pdf_path)
                    # print(is_non_empty_file(pdf_path))
                    # print(is_valid_pdf(pdf_path))
                    # if is_non_empty_file(pdf_path) and is_valid_pdf(pdf_path):
                    reader = PdfReader(pdf_path)
                    text = ' '.join(page.extract_text() for page in reader.pages if page.extract_text())

                    if text:
                        qa_pairs = model.generate_qa(text[:1000])  # Limit input size for the model
                        for q, a in qa_pairs[:n_qs]:
                            new_qa = QAs(question=q, answer=a, test_id=new_test.id)
                            db.session.add(new_qa)
                    # else:
                    #     flash(f"Invalid or corrupted PDF: {pdf.pdf_name}", category='error')
                except Exception as e:
                    print(f"Error processing PDF {pdf.pdf_name}: {e}")
                    flash(f"Failed to process {pdf.pdf_name}.", category='error')

            db.session.commit()
            flash('Test generated successfully!', category='success')

    return render_template('tests.html', user=current_user, qnas=new_qa, ntest=new_test)

@views.route('/delete-course', methods=['POST'])
def delete_course():
    data = json.loads(request.data)
    courseId = data.get('courseId')
    course = Course.query.get(courseId)
    if course and course.user_id == current_user.id:
        db.session.delete(course)
        db.session.commit()
    return jsonify({})

@views.route('/delete-pdf', methods=['POST'])
def delete_pdf():
    data = json.loads(request.data)
    pdfId = data.get('pdfId')
    pdf = PDF_link.query.get(pdfId)
    if pdf and pdf.user_id == current_user.id:
        db.session.delete(pdf)
        db.session.commit()
    return jsonify({})
