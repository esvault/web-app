from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=6, message=f'At least 6 symbols required')])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, message=f'At least 6 symbols required')])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=6, message=f'At least 6 symbols required')])
    email = StringField('Email', validators=[Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, message=f'At least 6 symbols required')])
    password2 = PasswordField('Repeat password', validators=[EqualTo('password')])
    submit = SubmitField('Sign up')

    def validate_username(self, username):
        u = User.query.filter_by(username=username.data).first()
        if u is not None:
            raise   ValidationError("Choose another username")
        
    def validate_email(self, email):
        u = User.query.filter_by(email=email.data).first()
        if u is not None:
            raise   ValidationError("User with email {} already exists".format(email))
        
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = StringField('About me', validators=[Length(max=140)])
    submit = SubmitField('Save')