from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin,db.Model):
    username = db.Column(db.String,primary_key=True)
    api_id = db.Column(db.Integer,nullable=False, unique=True)
    api_hash = db.Column(db.String,nullable=False, unique=True)
    phone = db.Column(db.Integer,nullable=False, unique=True)
    t_client = db.Column(db.PickleType(),nullable=True)
    wp_user = db.Column(db.String,nullable=False)
    wp_app_password = db.Column(db.String,nullable=False)
    wp_website = db.Column(db.String,nullable=False)
