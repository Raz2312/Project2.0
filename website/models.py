import firebase_admin
from firebase_admin import credentials , firestore
from flask import Flask, request, flash, Response, render_template, redirect, url_for
from flask_login import UserMixin


# מחלקת משתמש המשתמשת ב-UserMixin עבור פונקציונליות Flask-Login
class User(UserMixin):
    def __init__(
        self,
        id,
        Bio,
        user_name,
        email,
        password,
        first_name,
        last_name,
        profile_pic,
        items=None,
    ):
        # הגדרת תכונות המשתמש
        self.id = id                # מזהה ייחודי
        self.user_name = user_name  # שם משתמש
        self.email = email          # כתובת דוא"ל
        self.password = password    # סיסמה מוצפנת
        self.first_name = first_name  # שם פרטי
        self.last_name = last_name    # שם משפחה
        self.Bio = Bio              # ביוגרפיה
        self.profile_pic = profile_pic  # תמונת פרופיל
        self.items = items if items is not None else []  # רשימת פריטים של המשתמש

    def add_item(self, item):
        """הוספת פריט לרשימת הפריטים של המשתמש."""
        self.items.append(item)

# מחלקה המגדירה את מאפייני הפריט
class Item:
    def __init__(self, name, year, condition, price, other, date, owner_id, product_picture, item_id, address):
        # הגדרת תכונות הפריט
        self.name = name            # שם הפריט
        self.year = year            # שנת ייצור
        self.condition = condition  # מצב הפריט
        self.price = price          # מחיר
        self.other = other          # מידע נוסף
        self.date = date            # תאריך הוספה
        self.owner_id = owner_id    # מזהה הבעלים
        self.product_picture = product_picture  # תמונת הפריט
        self.item_id = item_id      # מזהה ייחודי של הפריט
        self.address = address      # כתובת המיקום של הפריט