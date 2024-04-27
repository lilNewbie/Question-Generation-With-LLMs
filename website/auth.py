from flask import Blueprint, render_template, url_for, request, flash, redirect, session
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, Course
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
auth = Blueprint('auth', __name__)


# @auth.route('/', methods=['POST', 'GET'])
@auth.route('/login', methods=['POST', 'GET'])
def login():
    if request.method=='POST':
        email = request.form.get('email')
        password = request.form.get('password')

        #querying the database
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in Successfully!', category='success')
                login_user(user, remember=True)
                print(user.courses)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password', category='error')
        else:
            flash('Email does not exist', category='error')
    
    return render_template('login.html', user=current_user)

@auth.route('/logout')
@login_required
def logout(): 
    logout_user()
    return redirect(url_for('auth.login'))




@auth.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
    new_user = None
    if request.method=='POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user = User.query.filter_by(email=email).first()
        
        if user:
            flash('Email is already in use', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 4 characters', category='error')
        elif len(firstName) < 2:
            flash('First name must be greater than 1 character1', category='error')
        elif password1 != password2:
            flash('Passwords do not match', category='error')
        elif len(password1) < 7:
            flash('Password must be atleast 7 characters', category='error')
        else:
            #add user to database
            new_user = User(email=email, first_name=firstName, password = generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created!', category='success')
            login_user(new_user, remember=True)
            return redirect(url_for('views.home'))
            
    return render_template('sign_up.html', user=current_user)
