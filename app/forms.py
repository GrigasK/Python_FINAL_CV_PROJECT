from wtforms import SubmitField, BooleanField, StringField, PasswordField, FloatField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Email
from flask_wtf import FlaskForm
from app import app


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo(
        'confirm_password', message='Passwords must match')])
    confirm_password = PasswordField(
        'Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def check_email(self, email):
        user = app.User.query.filter_by(
            email=email.data).first()
        if user:
            raise ValidationError(
                'This email address is already used by another user, please choose another email address.')

class LoginForm(FlaskForm):
    email = StringField('Email', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField('Log in')


class GroupForm(FlaskForm):
    group_name = BooleanField('Group name')
    submit = SubmitField('Submit')


class UpdatePassword(FlaskForm):
    user_email = StringField('Email', [DataRequired()])
    new_password = PasswordField('Password', [DataRequired()])
    submit = SubmitField('Update')
