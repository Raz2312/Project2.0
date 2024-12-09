import firebase_admin
from firebase_admin import credentials , firestore
from flask import Flask, request, flash, Response, render_template, redirect, url_for
from flask_login import UserMixin


class User(UserMixin):#מחלקת 
    def __init__(
        self,
        id,
        user_name,
        email,
        password,
        first_name,
        last_name,
        items=None,  # New attribute for items
    ):
        self.id = id
        self.user_name = user_name
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.Bio = None
        self.profile_pic = None
        self.items = items if items is not None else []  # Initialize with empty list if not provided

    def add_item(self, item):
        """Adds an Item to the User's item list."""
        self.items.append(item)

Bio = {
    
}

Img = {
    
}
