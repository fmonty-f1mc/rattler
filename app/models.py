from datetime import datetime

import itsdangerous.exc
from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedSerializer
from sqlalchemy.exc import OperationalError
from math import floor

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
    entries = db.relationship('PrelimPlayer', back_populates='player', cascade='all, delete-orphan')
    division_id=db.Column(db.ForeignKey('division.id'))
    player_division=db.relationship('Division',back_populates='players')
    
class Division(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(120),nullable=False)
    players = db.relationship('Player',back_populates='player_division')
    
class PrelimPlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    gross_score = db.Column(db.Integer, default=0)
    net_score = db.Column(db.Integer, default=0)
    player = db.relationship('Player', back_populates='entries')
    
    def update_scores(self,score):
        self.gross_score = score
        strokes_allocated=floor(self.player.handicap)
        self.net_score = self.gross_score - strokes_allocated
        
    
def create_table_if_not_exist(app):
    with app.app_context():
        db.create_all()