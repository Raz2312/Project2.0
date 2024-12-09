from flask import Flask, request, flash, render_template, redirect, url_for
from flask_login import LoginManager, login_user, login_required, current_user
import firebase_admin
from firebase_admin import credentials, firestore 

# Initialize Firebase
cred = credentials.Certificate(r"c:\Users\RAZ\Downloads\website-firebase-2f02a-firebase-adminsdk-1gcvh-31adc67afb.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


class User:#מאיפיינים של משתמש
    def __init__(self, id, user_name, email, password, first_name, last_name, img_id):
        self.id = id
        self.user_name = user_name
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.img_id = img_id
        self.items = []

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


class Item:# מאפיינים של אייטם
    def __init__(self, name, year, condition, price, other, date, owner_id, product_picture, item_id):
        self.name = name
        self.year = year
        self.condition = condition
        self.price = price
        self.other = other
        self.date = date
        self.owner_id = owner_id
        self.product_picture = product_picture
        self.item_id = item_id

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'

    from .views import views
    from .auth import auth
    from .list import list

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(list, url_prefix='/')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        user_ref = db.collection('Users').document(user_id)
        user_data = user_ref.get()

        if user_data.exists:
            user_info = user_data.to_dict()

            user = User(
                id=user_id,
                user_name=user_info.get('user_name', 'Unknown'),
                email=user_info.get('email', 'Unknown'),
                password=user_info.get('password', ''),
                first_name=user_info.get('first_name', ''),
                last_name=user_info.get('last_name', ''),
                img_id=user_info.get('profile_pic', None),
            )

            items_ref = user_ref.collection('Items').stream()
            user.items = [
                Item(
                    name=item.to_dict().get('name'),
                    year=item.to_dict().get('year'),
                    condition=item.to_dict().get('condition'),
                    price=item.to_dict().get('price'),
                    other=item.to_dict().get('other'),
                    date=item.to_dict().get('date'),
                    owner_id=user_id,
                    product_picture=item.to_dict().get('product_picture'),
                    item_id=item.to_dict().get('item_id')
                )
                for item in items_ref
            ]

            return user
        return None

    @app.route('/Myprofile', methods=['GET', 'POST'])
    @login_required
    def profile():
        user_ref = db.collection('Users').document(current_user.id)
        user_data = user_ref.get()
        if user_data.exists:
            user = user_data.to_dict()
            return render_template("Myprofile.html", user=current_user)
        flash("User not found!", category='error')
        return redirect(url_for('auth.login'))
    

    @app.route('/profile/<user_id>', methods=['GET', 'POST'])
    @login_required
    def profilefinder(user_id):
        user_ref = db.collection('Users').document(user_id)
        user_data = user_ref.get()

        if user_data.exists:
            user_info = user_data.to_dict()
            user = User(
                id=user_id,
                user_name=user_info.get('user_name'),
                email=user_info.get('email'),
                password=user_info.get('password'),
                first_name=user_info.get('first_name'),
                last_name=user_info.get('last_name'),
                img_id=user_info.get('profile_pic')
            )
            return render_template("Profile.html", user=user)
        else:
            flash("User not found!", category='error')
            return redirect(url_for('views.home'))
    
    @app.route('/update_profile', methods=['POST'])
    @login_required
    def update_profile():
        user_ref = db.collection('Users').document(current_user.id)
        updated_data = {
            "user_name": request.form['user_name'],
            "email": request.form['email'],
            "first_name": request.form['first_name'],
            "last_name": request.form['last_name'],
            "profile_pic": request.form['profile_pic']
        }
        user_ref.update(updated_data)
        flash("Profile updated successfully!", category='success')
        return redirect(url_for('profile'))

    @app.route('/', methods=['GET', 'POST'])
    def upload_image():
        return render_template('Myprofile.html', user=current_user)

    return app
