# מייבא ספריות נדרשות מפלאסק ומודולים אחרים
from flask import  render_template, request, flash , Blueprint
from flask_login import login_required, current_user
from . import db
from .models import User
from firebase_admin.firestore import FieldFilter, firestore
from werkzeug.utils import secure_filename
import os
from flask import redirect, url_for

# יוצר בלופרינט חדש לניהול שינויים בפרופיל המשתמש
profile_changes = Blueprint('profile_changes', __name__)

# /////////////////////////////////////////////////////////////////////////////////////////////////

# ראוט לעדכון הביוגרפיה של המשתמש
@profile_changes.route('/update_bio', methods=['POST','GET'])
@login_required  # דורש התחברות לאתר
def update_bio():
        bio = request.form.get('Bio')  # מקבל מידע מהטופס
        user_ref = db.collection('Users').document(current_user.id)  # מקבל הפניה למסמך המשתמש במסד הנתונים
        user_ref.update({"Bio": bio})  # מעדכן את הביוגרפיה
        flash("Bio updated successfully!", category='success')  # הודעת הצלחה למשתמש
        return redirect(url_for('pages.profile2', owner_id=current_user.id))  # מפנה את המשתמש חזרה לדף הפרופיל

# /////////////////////////////////////////////////////////////////////////////////////////////////

# מגדיר את תיקיית התמונות הפרופיל ויוצר אותה אם לא קיימת
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'website/static/profile_pictures')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ראוט לשינוי תמונת הפרופיל
@profile_changes.route('/change_profile_picture', methods=['POST','GET'])
@login_required  # דורש התחברות לאתר
def change_profile_picture():
        product_picture = request.files.get('profile_picture')  # מקבל את קובץ התמונה מהטופס
        filename = secure_filename(product_picture.filename)  # מבטיח שם קובץ בטוח
        filepath = os.path.join(UPLOAD_FOLDER, filename)  # בונה את הנתיב המלא לשמירת הקובץ
        product_picture.save(filepath)  # שומר את התמונה בשרת
        image_path = f'profile_pictures/{filename}'  # מגדיר את הנתיב היחסי לתמונה
        user_ref = db.collection('Users').document(current_user.id)  # מקבל הפניה למסמך המשתמש
        user_ref.update({"profile_pic": image_path})  # מעדכן את נתיב התמונה במסד הנתונים
        flash("Profile picture updated successfully!", category='success')  # הודעת הצלחה למשתמש
        print(image_path)  # מדפיס את הנתיב לקונסול (לצרכי דיבאג)
        return redirect(url_for('pages.profile2', owner_id=current_user.id))  # מפנה את המשתמש חזרה לדף הפרופיל

# /////////////////////////////////////////////////////////////////////////////////////////////////

# ראוט למחיקת משתמש (פונקציה מנהלית)
@profile_changes.route('/delete_user/<user_id>', methods=['POST'])
@login_required  # דורש התחברות לאתר
def delete_user(user_id):
        items_ref = db.collection('Items').where('owner_id', '==', user_id).stream()  # מוצא את כל הפריטים של המשתמש
        for item in items_ref:
            item.reference.delete()  # מוחק כל פריט שהמשתמש פרסם
        
        user_ref = db.collection('Users').document(user_id)  # מקבל הפניה למסמך המשתמש
        user_ref.delete()  # מוחק את המשתמש ממסד הנתונים
        flash("User and their items deleted successfully!", category='success')  # הודעת הצלחה למנהל
        return redirect(url_for('pages.admin'))  # מפנה חזרה לדף הניהול