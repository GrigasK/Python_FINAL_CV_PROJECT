
import json
import requests
from flask import render_template, request, session, redirect, url_for, flash, send_file, jsonify
from app.modules import get_user
from flask_login import LoginManager, UserMixin, current_user, logout_user, login_user, login_required
from flask_bcrypt import Bcrypt
from app.db import *
from app.forms import *
from datetime import datetime


import sqlite3

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = "Login if you want to see the information"


category = 'knowledge'
api_url = 'https://api.api-ninjas.com/v1/quotes?category={}'.format(category)

responses = requests.get(
    api_url, headers={'X-Api-Key': 'ipoHMLHaN6vCHaeuNUcrmeTiI9u0qNmBIy2YeTqP'})

print(responses.text)


def get_quotes():
    if responses.status_code == requests.codes.ok:
        data = responses.json()
        try:
            quote = data[0]["quote"]
            author = data[0]["author"]
            return quote, author
        except KeyError:
            return "No quotes found for this category."

    else:
        print("Error:", responses.status_code, responses.text)


api_url = 'https://api.api-ninjas.com/v1/chucknorris'
response = requests.get(
    api_url, headers={'X-Api-Key': 'ipoHMLHaN6vCHaeuNUcrmeTiI9u0qNmBIy2YeTqP'})
if response.status_code == requests.codes.ok:
    print(response.text)
else:
    print("Error:", response.status_code, response.text)


def get_Chuck():
    if response.status_code == requests.codes.ok:
        data = response.json()
        try:
            Chuck = data["joke"]
            return Chuck
        except KeyError:
            return "No Chuck joke found."

    else:
        print("Error:", responses.status_code, responses.text)


# url = "https://dad-jokes.p.rapidapi.com/random/joke"

# headers = {
#     "X-RapidAPI-Key": "c37eef3288mshd78531aeaf00a44p1327b5jsn8d3622e9b165",
#     "X-RapidAPI-Host": "dad-jokes.p.rapidapi.com"
# }


# response = requests.get(url, headers=headers)

# print(response.text)


# def get_joke():
#     if response.status_code == 200:
#         data = response.json()
#         setup = data["body"][0]["setup"]
#         joke = data["body"][0]["punchline"]
#         return setup, joke
#     else:
#         print("Error: Failed to retrieve joke from API")


menu = [
    # {"name": "Register", "url": "register"},
    {"name": "Login", "url": "login"},
]

admenu = [{"name": "CV", "url": "cv"},
          {"name": "Visitors", "url": "visitors"},
          {"name": "Log out", "url": "/cv"}
          ]

app.secret_key = "secret_key"


@login_manager.user_loader
def load_user(user_id):
    db.create_all()
    return User.query.get(int(user_id))


# MY INDEX PAGE

@app.route('/')
def first_load():
    return render_template('public/index.html', menu=menu)


@app.route('/database')
def get_data():
    conn = sqlite3.connect("app/UserDatabase.db", check_same_thread=False)
    cur = conn.cursor()
    cur.execute('SELECT * FROM skill')
    data = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(data)


@app.route("/cv")
def cv():
    authenticated = current_user.is_authenticated
    education = Education.query.filter_by().order_by(
        Education.start_date.desc()).all()
    experience = Experience.query.filter_by().order_by(
        Experience.start_date.desc()).all()
    return render_template('public/cv.html', authenticated=authenticated, quote=get_quotes(),  menu=menu, title='CV', skill=fetch_skills(), user=fetch_user(), language=fetch_language(), competence=fetch_competence(), education=education,
                           experience=experience)


@app.route('/visitors')
@login_required
def visitors():
    return render_template('admin/visitors.html', visitor=fetch_visitor(), title='Visitors', admin_menu=admenu)


@app.route("/add_visitor", methods=["GET", "POST"])
def add_visitor():

    if request.method == 'POST':

        visitor_name = request.form['visitor_name']
        visitor_company = request.form['visitor_company']
        visitor_email = request.form['visitor_email']
        visit_time = datetime.now()

        new_visitor = Visitor(
            visitor_name=visitor_name, visitor_company=visitor_company, visitor_email=visitor_email, visit_time=visit_time)

        db.session.add(new_visitor)
        db.session.commit()
        db.session.close()

        return redirect(url_for('cv'))
    # return render_template('public/cv.html', menu=menu, visitor=fetch_visitor())


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('admin_view'))

    form = RegisterForm()
    if form.validate_on_submit():
        user_email = User.query.filter_by(email=form.email.data).first()
        if user_email is not None:
            flash('Email already in use', 'danger')
        else:
            encripted_password = bcrypt.generate_password_hash(
                form.password.data).decode('utf-8')
            user = User(email=form.email.data, password=encripted_password)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('login'))

    return render_template('public/register.html', menu=menu, title='Register', form=form)


# MY LOGIN PAGE

@app.route('/login', methods=["GET", "POST"])
def login():
    db.create_all()
    if current_user.is_authenticated:
        return redirect(url_for('admin_view'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(
            email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin_view'))
        else:
            flash('Something went wrong, please check your email and password', 'danger')
    return render_template('public/login.html', menu=menu, title='login', form=form)


# MY ADMIN PAGE

@app.route('/admin', methods=["GET", "POST"])
@login_required
def admin_view():
    db.create_all()
    try:
        user = User.query.filter_by(id=current_user.id).all()
        skill = Skill.query.filter_by(user_id=current_user.id).all()
        education = Education.query.filter_by(
            user_id=current_user.id).order_by(Education.start_date.desc()).all()

        experience = Experience.query.filter_by(
            user_id=current_user.id).order_by(Experience.start_date.desc()).all()
        competence = Competence.query.filter_by(user_id=current_user.id).all()
        language = Language.query.filter_by(user_id=current_user.id).all()
    except:
        user = []
        skill = []
        education = []
        experience = []
        competence = []
        language = []

    return render_template("admin/admin.html", Chuck=get_Chuck(), skill=skill, menu=menu, admin_menu=admenu, user=user, language=language, competence=competence, education=education, experience=experience)


# MY LOGOUT FUNCTION


@app.route('/logout', methods=["POST"])
@login_required
def logout():

    session.pop('user', None)

    session.clear()

    return redirect(url_for('first_load'))


# ADD USER
# ---------------------------------------------------------


@app.route('/add_user', methods=['POST'])
@login_required
def add_user():
    if request.method == 'POST':
        user = User.query.filter_by(id=current_user.id).first()

        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.phone = request.form['phone']
        user.dob = datetime.strptime(request.form['dob'], '%Y-%m-%d').date()
        user.linkedin = request.form['linkedin']
        user.github = request.form['github']

        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user.photo = filename

        db.session.commit()
        db.session.close()

        flash("User updated successfully")
        return redirect(url_for('admin_view'))


# EDIt USER ------------------------------------------

@app.route('/update_user/<int:id>', methods=['GET', 'POST'])
@login_required
def update_user(id):
    user = User.query.filter_by(id=current_user.id).first()

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        dob = datetime.strptime(request.form['dob'], '%Y-%m-%d').date()
        linkedin = request.form['linkedin']
        github = request.form['github']

        user.first_name = first_name
        user.last_name = last_name
        user.phone = phone
        user.dob = dob
        user.linkedin = linkedin
        user.github = github

        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user.photo = filename

        db.session.commit()
        flash('User has been updated!')
        return redirect(url_for('admin_view'))

    return render_template("admin/admin.html", skill=fetch_skills(), menu=menu, admin_menu=admenu, user=user)

# INSERT DATA INTO SKILL TABLE


@app.route('/add_skill', methods=['POST'])
@login_required
def add_skill():

    if request.method == 'POST':

        name = request.form['skill_name']
        level = request.form['level']
        user_id = current_user.id

        new_skill = Skill(name=name, level=level, user_id=user_id)

        db.session.add(new_skill)
        db.session.commit()
        db.session.close()
        flash("New skill added successfully")

        return redirect(url_for('admin_view'))

# DELETE SKILLS


@app.route("/skill_delete/<int:id>")
@login_required
def skill_delete(id):
    skill_to_delete = Skill.query.get_or_404(id)

    try:
        db.session.delete(skill_to_delete)
        db.session.commit()
        flash("Skill deleted successfully")
        return redirect(url_for('admin_view'))

    except:
        flash("FAILED")
        return redirect(url_for('admin_view'))


# EDIT SKILL - --------------------------------


@app.route('/update_skill/<int:id>', methods=['GET', 'POST'])
@login_required
def update_skill(id):
    skills = Skill.query.filter_by(
        id=id, user_id=current_user.id).first()

    if request.method == 'POST':
        name = request.form['skill_name']
        level = request.form['level']
        # user_id = current_user.id

        skills.name = name
        skills.level = level
        # skills.user_id = user_id

        db.session.commit()
        flash('Skill has been updated!')
        return redirect(url_for('admin_view'))
    return render_template("admin/admin.html",  skill=fetch_skills(), menu=menu, admin_menu=admenu)


# INSERT DATA INTO EDUCATION TABLE -----------------------------

@app.route('/add_education', methods=['POST'])
@login_required
def add_education():

    if request.method == 'POST':

        institution_name = request.form['institution_name']
        degree = request.form['degree']
        field_of_study = request.form['field_of_study']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        user_id = current_user.id

        new_education = Education(institution_name=institution_name, degree=degree,
                                  field_of_study=field_of_study, start_date=start_date, end_date=end_date, user_id=user_id)

        db.session.add(new_education)
        db.session.commit()
        db.session.close()
        flash("Education added successfully")

        return redirect(url_for('admin_view'))


# EDIT EDUCATION ----------------------------------

@app.route('/edit_education/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_education(id):
    education = Education.query.filter_by(
        id=id, user_id=current_user.id).first()

    if request.method == 'POST':
        institution_name = request.form['institution_name']
        degree = request.form['degree']
        field_of_study = request.form['field_of_study']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        education.institution_name = institution_name
        education.degree = degree
        education.field_of_study = field_of_study
        education.start_date = start_date
        education.end_date = end_date

        db.session.commit()
        flash('Education has been updated!')
        return redirect(url_for('admin_view'))
    return render_template("admin/admin.html",  skill=fetch_skills(), menu=menu, admin_menu=admenu, education=fetch_education())

# DELETE EDUCATION----------------------------------------------------


@app.route("/delete_education/<int:id>")
@login_required
def delete_education(id):
    delete_education = Education.query.get_or_404(id)

    try:
        db.session.delete(delete_education)
        db.session.commit()
        flash("Education deleted successfully")
        return redirect(url_for('admin_view'))

    except:
        flash("FAILED")
        return redirect(url_for('admin_view'))


# INSERT DATA INTO EXPERIENCE TABLE --------------------------------------

@app.route('/add_experience', methods=['POST'])
@login_required
def add_experience():

    if request.method == 'POST':

        company_name = request.form['company_name']
        position = request.form['position']
        description = request.form['description']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        user_id = current_user.id

        new_experience = Experience(company_name=company_name, position=position,
                                    description=description, start_date=start_date, end_date=end_date, user_id=user_id)

        db.session.add(new_experience)
        db.session.commit()
        db.session.close()
        flash("Experience added successfully")

        return redirect(url_for('admin_view'))

# -- EDIT EXPERIENCE ------------------------------------------------------


@app.route('/edit_experience/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_experience(id):
    experience = Experience.query.filter_by(
        id=id, user_id=current_user.id).first()

    if request.method == 'POST':
        company_name = request.form['company_name']
        position = request.form['position']
        description = request.form['description']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        experience.company_name = company_name
        experience.position = position
        experience.description = description
        experience.start_date = start_date
        experience.end_date = end_date

        db.session.commit()
        flash('Experience has been updated!')
        return redirect(url_for('admin_view'))
    return render_template("admin/admin.html", menu=menu, admin_menu=admenu, experience=fetch_experience())

# DELETE EXPERIENCE----------------------------------------------------


@app.route("/delete_experience/<int:id>")
@login_required
def delete_experience(id):
    delete_experience = Experience.query.get_or_404(id)

    try:
        db.session.delete(delete_experience)
        db.session.commit()
        flash("Experience deleted successfully")
        return redirect(url_for('admin_view'))

    except:
        flash("FAILED")
        return redirect(url_for('admin_view'))


# -- ADD LANGUAGE ------------------------------------------------------

@app.route('/add_language', methods=['POST'])
@login_required
def add_language():

    if request.method == 'POST':

        language = request.form['language']
        level = request.form['level']
        user_id = current_user.id

        new_language = Language(language=language, level=level,
                                user_id=user_id)

        db.session.add(new_language)
        db.session.commit()
        db.session.close()
        flash("Language added successfully")

        return redirect(url_for('admin_view'))

# -- EDIT LANGAUGE ------------------------------------------------------


@app.route('/edit_language/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_language(id):
    language = Language.query.filter_by(
        id=id, user_id=current_user.id).first()

    if request.method == 'POST':
        language.language = request.form['language']
        language.level = request.form['level']

        # language.language = language
        # language.level = level

        db.session.commit()
        flash('Language has been updated!')
        return redirect(url_for('admin_view'))
    return render_template("admin/admin.html", menu=menu, admin_menu=admenu, language=fetch_language())

# DELETE LANGUAGE----------------------------------------------------


@app.route("/delete_language/<int:id>")
@login_required
def delete_language(id):
    delete_language = Language.query.get_or_404(id)

    try:
        db.session.delete(delete_language)
        db.session.commit()
        flash("Language deleted successfully")
        return redirect(url_for('admin_view'))

    except:
        flash("FAILED")
        return redirect(url_for('admin_view'))


# -- ADD COMPETENCE ------------------------------------------------------

@app.route('/add_competence', methods=['POST'])
@login_required
def add_competence():

    if request.method == 'POST':

        competence = request.form['competence']

        user_id = current_user.id

        new_competence = Competence(name=competence,
                                    user_id=user_id)

        db.session.add(new_competence)
        db.session.commit()
        db.session.close()
        flash("Competence added successfully")

        return redirect(url_for('admin_view'))

# -- EDIT COMPETENCE ------------------------------------------------------


@app.route('/edit_competence/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_competence(id):
    name = Competence.query.filter_by(
        id=id, user_id=current_user.id).first()

    if request.method == 'POST':
        competence = request.form['competence']

        name.name = competence

        db.session.commit()
        flash('Competence has been updated!')
        return redirect(url_for('admin_view'))
    return render_template("admin/admin.html")

# DELETE COMPETENCE----------------------------------------------------


@app.route("/delete_competence/<int:id>")
@login_required
def delete_competence(id):
    delete_competence = Competence.query.get_or_404(id)

    try:
        db.session.delete(delete_competence)
        db.session.commit()
        flash("Competence deleted successfully")
        return redirect(url_for('admin_view'))

    except:
        flash("FAILED")
        return redirect(url_for('admin_view'))


# -- EDIT INFORMATION ABOUT USER ------------------------------------------------------


@app.route('/edit_info/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_info(id):
    user = User.query.filter_by(id=current_user.id).first()

    if request.method == 'POST':
        info = request.form['info']

        user.info = info

        db.session.commit()
        flash('Introduction has been updated!')
        return redirect(url_for('admin_view'))
    return render_template("admin/admin.html")

# DELETE USER INFO----------------------------------------------------


@app.route("/delete_info/<int:id>")
@login_required
def delete_info(id):
    user = User.query.get_or_404(id)
    user.info = ''
    try:
        db.session.commit()
        flash("Introduction deleted successfully")
    except:
        db.session.rollback()
        flash("FAILED")
    return redirect(url_for('admin_view'))
