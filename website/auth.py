# ייבוא מודולים נדרשים
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from google.cloud.firestore_v1.base_query import FieldFilter
import uuid

# יצירת Blueprint לניתובי אימות
auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    # טיפול בשליחת טופס
    if request.method == 'POST':
        # קבלת נתוני הטופס
        email = request.form.get('email')
        password = request.form.get('password')

        # שאילתה ל-Firestore עבור משתמש עם אימייל תואם
        user_query = db.collection('Users').where(filter=FieldFilter('email', '==', email)).stream()
        user_docs = list(user_query)  
        if user_docs: 
            # נמצא משתמש, יצירת אובייקט User מנתוני Firestore
            user_data = user_docs[0].to_dict()  
            user = User(
                id=user_docs[0].id,  
                user_name=user_data['user_name'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                Bio=user_data['Bio'],
                profile_pic=user_data['profile_pic']
            )
            # אימות סיסמה
            if check_password_hash(user.password, password):
                # התחברות הצליחה
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('pages.index'))
            else:
                # סיסמה שגויה
                flash('Incorrect password, try again.', category='error')
        else:
            # משתמש לא נמצא
            flash('Email does not exist.', category='error')

    # הצגת תבנית התחברות עבור בקשות GET
    return render_template("login.html", user=current_user)


@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    # התנתקות של המשתמש הנוכחי
    logout_user()
    # הפנייה לדף ההתחברות
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    # טיפול בשליחת טופס
    if request.method == 'POST':
        # קבלת נתוני טופס
        user_name = request.form.get('user_name')
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('LastName', "")
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        profilepic = request.files.get('profile_pic')

        # בדיקה אם האימייל או שם המשתמש כבר קיימים
        email_query = db.collection('Users').where(filter=FieldFilter('email', '==', email)).get()
        username_query = db.collection('Users').where(filter=FieldFilter('user_name', '==', user_name)).get()

        # אימות נתוני קלט
        if email_query:
            flash('Email already exists.', category='error')
        elif username_query:
            flash('User name is already in use.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 1:
            flash('First name must be greater than 1 character.', category='error')
        elif len(last_name) < 1:
            flash('Last name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            # יצירת מזהה ייחודי למשתמש החדש
            unique_id = str(uuid.uuid4())

            # יצירת אובייקט User חדש
            new_user = User(
                id=unique_id, 
                email=email,
                user_name=user_name,
                first_name=first_name,
                last_name=last_name,
                password=generate_password_hash(password1, method='pbkdf2:sha256'),
                Bio="", 
                profile_pic='avatar.jpg'
                
            )
            # שמירת משתמש ב-Firestore
            doc_ref = db.collection('Users').document(unique_id)  
            doc_ref.set(new_user.__dict__) 
            # התחברות המשתמש החדש
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('pages.index'))

    # הצגת תבנית הרשמה עבור בקשות GET
    return render_template("sign_up.html", user=current_user)