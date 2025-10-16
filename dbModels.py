from datetime import datetime
import io
import csv
from math import ceil, floor

from flask import Flask, render_template_string, request, redirect, url_for, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect

app = Flask(__name__)
app.secret_key = "dev-secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tournaments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

class tournament(db.Model):
    #__name__="to"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    course_name = db.Column(db.String(120),nullable=False)
    course_rating = db.Column(db.Integer,default=72,nullable=True)
    yardage = db.Column(db.Integer,default=6500,nullable=True)
    
    
class player(db.Model):
    #__name__="player"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120),nullable=False)
    
class division(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(120),nullable=False)
    

