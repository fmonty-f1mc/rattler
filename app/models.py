from datetime import datetime

import itsdangerous.exc
from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedSerializer
from sqlalchemy.exc import OperationalError

from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    try:
        return Player.query.get(int(user_id))
    except OperationalError:
        return None


class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    course_name = db.Column(db.String(120),nullable=False)
    course_rating = db.Column(db.Integer,default=72,nullable=True)
    yardage = db.Column(db.Integer,default=6500,nullable=True)
    
    
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120),nullable=False)
    email = db.Column(db.String(120),nullable=True)
    handicap = db.Column(db.Integer,default=0)
    
class Division(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(120),nullable=False)
    
def create_table_if_not_exist(app):
    with app.app_context():
        db.create_all()