from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Course(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(10000))
    course_id = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pdf = db.relationship('PDF_link')
    test = db.relationship('Tests')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique = True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    courses = db.relationship('Course')
    pdfs = db.relationship('PDF_link')
    tests = db.relationship('Tests')

class PDF_link(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    id = db.Column(db.Integer, primary_key=True)
    pdf_name = db.Column(db.String(1000))
    link = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    course_id = db.Column(db.String(100), db.ForeignKey('course.course_id'), nullable=False)

class QAs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(1000))
    answer = db.Column(db.String(10000))
    test_id = db.Column(db.String(100), db.ForeignKey('tests.id'))


class Tests(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    id = db.Column(db.Integer, primary_key=True)
    test_name = db.Column(db.String(1000))
    qa_pairs = db.relationship('QAs')
    course_id = db.Column(db.String(100), db.ForeignKey('course.course_id'), nullable=False)




