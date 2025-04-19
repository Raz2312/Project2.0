from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from . import db
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from firebase_admin import firestore
import uuid
from .models import User
from google.cloud.firestore_v1.base_query import FieldFilter
from .models import Item

# מודול זה מכיל את כל הפונקציות לטיפול בפריטים - יצירה, מחיקה והצגה
item_funcs = Blueprint('item_funcs', __name__)

# הגדרת תיקיית ההעלאות ויצירתה אם היא לא קיימת
# תיקייה זו תשמש לשמירת תמונות המוצרים שהמשתמשים מעלים
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'website/static/uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# /////////////////////////////////////////////////////////////////////////////////////////////////

@item_funcs.route('/create', methods=['GET', 'POST'])# פעולה מסופיה אייטם חדש למשתמש
@login_required  # דרישה להתחברות לפני יצירת פריט חדש
def create():
    if request.method == 'POST':
        # קבלת נתוני הטופס מהמשתמש דרך הבקשה
        name = request.form.get('name')  # שם הפריט
        year = request.form.get('year')  # שנת הפריט
        condition = request.form.get('condition')  # מצב הפריט
        price = request.form.get('price')  # מחיר הפריט
        other = request.form.get('other')  # מידע נוסף על הפריט
        product_picture = request.files.get('product_picture')  # תמונת הפריט
        address = request.form.get('address')  # כתובת המוכר/המיקום



        try:
            # המרת שנה ומחיר למספרים - חייבים להיות ערכים מספריים
            year = int(year)
            price = float(price)
        except ValueError:
            # הצגת הודעת שגיאה אם ההמרה נכשלה והחזרה לדף היצירה
            flash('Year and Price must be valid numbers.', category='error')
            return render_template("create.html", user=current_user)

        # בדיקות תקינות הנתונים לפני שמירה במסד הנתונים
        if len(name) < 3:
            # שם הפריט חייב להיות באורך סביר
            flash('Item name must be greater than 3 characters.', category='error')
        elif year <= 0:
            # השנה חייבת להיות מספר חיובי
            flash('Year must be a positive number.', category='error')
        elif len(condition) < 2 :
            # תיאור מצב הפריט חייב להיות באורך סביר
            flash('Condition must be greater than 3 characters.', category='error')
        elif price <= 0:
            # המחיר חייב להיות מספר חיובי
            flash('Price must be a positive number.', category='error')
        else:
            # טיפול בתמונת המוצר אם הועלתה
            image_path = None
            if product_picture:
                # אבטחת שם הקובץ למניעת התקפות
                filename = secure_filename(product_picture.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                # שמירת הקובץ בתיקיית ההעלאות
                product_picture.save(filepath)
                # שמירת הנתיב היחסי לתמונה
                image_path = f'uploads/{filename}'  

            # יצירת מזהה ייחודי לפריט באמצעות UUID
            unique_id = str(uuid.uuid4())

            # יצירת מילון עם נתוני הפריט לשמירה במסד הנתונים
            item_data = {
                "name": name,
                "year": int(year),
                "condition": condition,
                "price": float(price),
                "other": other,
                "date": firestore.SERVER_TIMESTAMP,  # חותמת זמן אוטומטית מהשרת
                "owner_id": str(current_user.id),  # שמירת מזהה המשתמש היוצר
                "product_picture": image_path,
                "item_id": unique_id,  # שמירת המזהה הייחודי גם בתוך המסמך
                "address": address
            }

            # שמירת הפריט במסד הנתונים הכללי של כל הפריטים
            doc_ref = db.collection('Items').document(unique_id)
            doc_ref.set(item_data)
            
            # שמירת הפריט גם באוסף הפריטים האישי של המשתמש
            user_ref = db.collection('Users').document(str(current_user.id))
            user_ref.collection('Items').document(unique_id).set(item_data)  
            # הודעה על הצלחת הפעולה
            flash('Item added successfully!', category='success')
            # הפניה לדף הפריטים הציבורי
            return redirect(url_for('item_funcs.show_items'))

    # החזרת תבנית דף היצירה אם זו בקשת GET או אם הייתה שגיאה
    return render_template("create.html", user=current_user)
# /////////////////////////////////////////////////////////////////////////////////////////////////

@item_funcs.route('/delete/<item_id>' , methods = ['POST'])
# פונקציה למחיקת פריט על ידי משתמש רגיל
def delete(item_id):
    # חיפוש הפריט לפי המזהה שלו במסד הנתונים
    find_item = db.collection('Items').where(filter=FieldFilter('item_id', '==', item_id)).stream()
    
    for item in find_item:
        # מחיקת הפריט ממסד הנתונים הכללי
        item.reference.delete()  
        # מחיקת הפריט מאוסף הפריטים של המשתמש הנוכחי
        user_ref = db.collection('Users').document(str(current_user.id))
        user_ref.collection('Items').document(item.id).delete()
        # הודעה על הצלחת המחיקה למשתמש
        flash('Item deleted successfully!', category='success')
        
    # הפניה לדף הפרופיל של המשתמש לאחר המחיקה
    return redirect(url_for('pages.profile2', owner_id=current_user.id))
# /////////////////////////////////////////////////////////////////////////////////////////////////

@item_funcs.route('/admin/delete/<item_id>' , methods = ['POST'])
@login_required  
# פונקציה למחיקת פריט על ידי מנהל המערכת
def admin_delete(item_id):
    # חיפוש הפריט לפי המזהה שלו במסד הנתונים
    find_item = db.collection('Items').where(filter=FieldFilter('item_id', '==', item_id)).stream()
    
    for item in find_item:
        # מחיקת הפריט ממסד הנתונים הכללי
        item.reference.delete()  
        # קבלת כל נתוני הפריט לפני המחיקה הסופית
        item_data = item.to_dict()  
        # קבלת מזהה המשתמש שהפריט שייך לו - חשוב במיוחד כשמנהל מוחק
        user_id = item_data.get('owner_id')  
       
        # מחיקת הפריט גם מאוסף הפריטים של המשתמש הבעלים
        user_ref = db.collection('Users').document(str(user_id))  
        user_ref.collection('Items').document(item.id).delete()
        # הודעה על הצלחת המחיקה למנהל
        flash('Item deleted successfully!', category='success')
        
    # הפניה לדף הניהול של המנהל
    return redirect(url_for('pages.admin', owner_id=current_user.id))

# /////////////////////////////////////////////////////////////////////////////////////////////////

@item_funcs.route('/public')# פעולה המציגה את כל האייטמים 
# פונקציה להצגת כל הפריטים בדף הציבורי
def show_items():
    # קבלת רשימת כל הפריטים ממסד הנתונים
    items = show_items()
    # הצגת דף הפריטים הציבורי עם כל הפריטים שנמצאו
    return render_template('public.html', items=items, user=current_user)

# /////////////////////////////////////////////////////////////////////////////////////////////////