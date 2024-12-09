from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from . import db
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from firebase_admin import firestore
import uuid
from .models import User

list = Blueprint('list', __name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@list.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        year = request.form.get('year')
        condition = request.form.get('condition')
        price = request.form.get('price')
        other = request.form.get('other')
        product_picture = request.files.get('product_picture')


        try:
            year = int(year)
            price = float(price)
        except ValueError:
            flash('Year and Price must be valid numbers.', category='error')
            return render_template("create.html", user=current_user)

        if len(name) < 3:
            flash('Item name must be greater than 3 characters.', category='error')
        elif year <= 0:
            flash('Year must be a positive number.', category='error')
        elif len(condition) < 2 :
            flash('Condition must be greater than 3 characters.', category='error')
        elif price <= 0:
            flash('Price must be a positive number.', category='error')
        else:
            image_path = None
            if product_picture:
                filename = secure_filename(product_picture.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                product_picture.save(filepath)
                image_path = f'uploads/{filename}'  

            # Generate a unique item_id
            unique_id = str(uuid.uuid4())


            item_data = {

                "name": name,
                "year": int(year),
                "condition": condition,
                "price": float(price),
                "other": other,
                "date": firestore.SERVER_TIMESTAMP,
                "owner_id": str(current_user.id),  
                "product_picture": image_path,
                "item_id": unique_id
            }
            # Add to main Items collection using unique_id as document ID
            doc_ref = db.collection('Items').document(unique_id)
            doc_ref.set(item_data)
            
            # Add to user's Items subcollection with the same ID
            user_ref = db.collection('Users').document(str(current_user.id))
            user_ref.collection('Items').document(unique_id).set(item_data)  # Use document() instead of add()
            flash('Item added successfully!', category='success')
            return redirect(url_for('list.show_items'))

    return render_template("create.html", user=current_user)

class Item:
    def __init__(self, name, year, condition, price, other, date, product_picture,
                 item_id):
        self.name = name
        self.year = year
        self.condition = condition
        self.price = price
        self.other = other
        self.date = date
        self.owner_id = current_user.id
        self.product_picture = product_picture
        self.item_id = item_id
                                

@list.route('/public')
def show_items():
    items = []
    users_ref = db.collection('Users')
    for user_doc in users_ref.stream():
        owner_id = user_doc.id
        items_collection = user_doc.reference.collection('Items').stream()
        for doc in items_collection:
            item_data = doc.to_dict()
            item_data['id'] = doc.id
            item_data['owner_id'] = owner_id  
            items.append(item_data)
    
    return render_template('public.html', items=items, user=current_user)




@list.route('/deleteitem/<item_id>', methods=['GET'])
def deleteitem(item_id):
    print(item_id)
    item_ref = db.collection('Items').document(item_id)
    item_data = item_ref.get()
    if item_data:
        print("yes")
    else:
        print("no")
    

    flash('Item deleted successfully!', category='success')
    return render_template('Myprofile.html', user=current_user) 




@list.route('/mylist', methods=['GET'])
@login_required
def mylist():
    return render_template("mylist.html", user=current_user)

@list.route('/item/<item_id>/<owner_id>')
def BigItem(item_id, owner_id):
    item_ref = db.collection('Items').document(item_id)
    user_ref = db.collection('Users').document(owner_id)
    user_data = user_ref.get()
    item_data = item_ref.get()
    if item_data.exists:
        data = item_data.to_dict()
        item = Item(
            name=data['name'],
            year=data['year'],
            condition=data['condition'],
            price=data['price'],
            other=data['other'],
            date=data['date'],
            product_picture=data['product_picture'],
            item_id=item_id
        )
        if user_data.exists:
            user_data = user_data.to_dict()
            user = User(
                id=owner_id,
                user_name=user_data['user_name'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                password=user_data['password'],
            )
        
        return render_template('BigItem.html', user=user, item=item)
    
    flash('Item not found', category='error')
    return redirect(url_for('list.show_items'))
@list.route('/profile2/<owner_id>', methods=['GET'])
def profile2(owner_id):

    return render_template('Myprofile.html', user_id=owner_id)




