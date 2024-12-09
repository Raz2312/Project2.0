from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify, Response ,abort
from flask_login import login_required, current_user
from .models import Bio,Img
from . import db
import json
from werkzeug.utils import secure_filename

views = Blueprint('views', __name__)

@views.route('/home', methods=['GET', 'POST'])
def home():
    return render_template("home.html", user=current_user)



@views.route('/add-bio', methods=['POST'])
@login_required
def add_bio():
    bio_text = request.form.get('bio')
    if bio_text:
        new_bio = Bio(data=bio_text, user_id=current_user.id)
        db.collection('Users').document(current_user.id).collection('Bio').add(new_bio)
        flash('Bio entry added successfully!', 'success')
    else:
        flash('Bio entry cannot be empty', 'error')
    return redirect(url_for('views.home'))


@views.route('/upload', methods=['POST'])
@login_required
def upload():
    pic = request.files.get('pic')
    if not pic:
        flash('No picture uploaded!', 'error')
        return redirect(url_for('views.home'))

    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    if not filename or not mimetype:
        flash('Invalid upload!', 'error')
        return redirect(url_for('views.home'))

    # Delete old image if it exists
    if current_user.img_id:
        old_img = Img.query.get(current_user.img_id)
        if old_img:
            db.session.delete(old_img)
            db.session.commit()

    # Save new image data to the Img model
    new_img = Img(img=pic.read(), name=filename, mimetype=mimetype)
    db.session.add(new_img)
    db.session.commit()

    # Update current_user profile to link to the new image
    current_user.img_id = new_img.id
    db.session.commit()

    flash('Image uploaded successfully!', 'success')
    return redirect(url_for('views.home'))


@views.route('/profile-pic/<int:img_id>')
def get_profile_pic(img_id):
    img = Img.query.get(img_id)
    if not img:
        abort(404)
    return Response(img.img, mimetype=img.mimetype)

