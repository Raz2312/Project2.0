# ייבוא הספריות הנדרשות
from website import create_app
from flask import Flask, render_template
from flask_login import login_required, current_user

# יצירת אובייקט אפליקציית Flask
app = Flask(__name__)

# יצירת והגדרת אפליקציית Flask עם הגדרות מהמודול website
app = create_app()

# הגדרת נתיב הבית של האפליקציה
@app.route('/')
def index():
    return render_template("index.html", user=current_user)

# הפעלת האפליקציה כאשר הקובץ מופעל ישירות
if __name__ == '__main__':
    app.run(debug=True)  # הפעלת השרת במצב דיבוג