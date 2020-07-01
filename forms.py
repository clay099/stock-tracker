from flask_wtf import FlaskForm
from wtforms_alchemy import model_form_factory
from models import db, User, Stock, User_Stock
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

BaseModelForm = model_form_factory(FlaskForm)


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


class NewUserForm(ModelForm):
    """new user form"""
    class Meta:
        model = User


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class Stock(ModelForm):
    """stock form"""
    class Meta:
        model = Stock


class UserStockForm(ModelForm):
    """user stock form"""
    class Meta:
        model = User_Stock
