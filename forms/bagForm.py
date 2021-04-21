from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from werkzeug.security import check_password_hash, generate_password_hash


class BagForm(FlaskForm):
    submit = SubmitField('Войти')
