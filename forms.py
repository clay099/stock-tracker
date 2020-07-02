from flask_wtf import FlaskForm
from wtforms_alchemy import model_form_factory
from models import db, User, Stock, User_Stock
from wtforms import StringField, PasswordField, SelectField, IntegerField
from wtforms.validators import DataRequired, Optional

BaseModelForm = model_form_factory(FlaskForm)


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


class NewUserForm(ModelForm):
    """new user form"""
    class Meta:
        model = User


class UserSettings(ModelForm):
    """edit user settings form"""

    class Meta:
        model = User
        exclude = ['password']


class UpdatePassword(FlaskForm):
    """update password form"""
    current_password = PasswordField(
        'Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_new_password = PasswordField(
        'Confirm New Password', validators=[DataRequired()])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class NewStockForm(FlaskForm):
    """add a new stock form"""

    stock_symbol = StringField('Stock Symbol', validators=[DataRequired()])
    stock_num = IntegerField(
        'Number of Stocks (optional)', validators=[Optional()])
    notification_period = SelectField("Notification Period", choices=[
        ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')])
