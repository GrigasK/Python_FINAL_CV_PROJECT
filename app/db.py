from flask import Flask, current_app, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, logout_user, login_user, login_required
from datetime import datetime

import os
from app import app
import sqlite3
from werkzeug.utils import secure_filename

# --------------------------------
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_bootstrap import Bootstrap

# --------------------------------


basedir = os.path.abspath(os.path.dirname(__file__))
print(basedir)


app.config['SECRET_KEY'] = 'GRIG'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'UserDatabase.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


db = SQLAlchemy(app)


admin = Admin(app)
bootstrap = Bootstrap(app)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(120))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    photo = db.Column(db.String(220))
    dob = db.Column(db.Date)
    linkedin = db.Column(db.String)
    github = db.Column(db.String)
    info = db.Column(db.String(3000))


class Skill(db.Model):
    __tablename__ = 'skill'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    level = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    __table_args__ = (
        db.CheckConstraint('level >= 0'),
        db.CheckConstraint('level <= 100'),
    )


class Education(db.Model):
    __tablename__ = 'education'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    institution_name = db.Column(db.String(100))
    degree = db.Column(db.String(50))
    field_of_study = db.Column(db.String(50))
    start_date = db.Column(db.String(50))
    end_date = db.Column(db.String(50))


class Experience(db.Model):
    __tablename__ = 'experience'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    company_name = db.Column(db.String(100))
    position = db.Column(db.String(100))
    description = db.Column(db.String(1000))
    start_date = db.Column(db.String(30))
    end_date = db.Column(db.String(30))


class Competence(db.Model):
    __tablename__ = 'competence'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Language(db.Model):
    __tablename__ = 'language'
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(50))
    level = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Visitor(db.Model):
    __tablename__ = 'visitor'
    id = db.Column(db.Integer, primary_key=True)
    visitor_name = db.Column(db.String(50))
    visitor_company = db.Column(db.String(100), nullable=False)
    visitor_email = db.Column(db.String(100))
    visit_time = db.Column(db.String(100))


conn = sqlite3.connect("app/UserDatabase.db", check_same_thread=False)
conn.row_factory = sqlite3.Row


def fetch_visitor():
    visitor_table = conn.execute("SELECT * from visitor").fetchall()
    visitor = visitor_table
    return visitor


def fetch_skills():
    skill_table = conn.execute("SELECT * FROM skill").fetchall()
    skill = skill_table
    return skill


def fetch_user():
    user_table = conn.execute("SELECT * FROM user").fetchall()
    user_table = user_table
    return user_table


def fetch_language():
    language_table = conn.execute("SELECT * FROM language").fetchall()
    language = language_table
    return language


def fetch_competence():
    competence_table = conn.execute("SELECT * FROM competence").fetchall()
    competence = competence_table
    return competence


def fetch_education():
    education_table = conn.execute("SELECT * FROM education").fetchall()
    education = education_table
    return education


def fetch_experience():
    experience_table = conn.execute("SELECT * FROM experience").fetchall()
    experience = experience_table
    return experience
