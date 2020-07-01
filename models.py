from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from sqlalchemy_utils import EmailType, PasswordType
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()


class User(db.Model, UserMixin):
    """User model"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(EmailType, nullable=False, unique=True)
    password = db.Column(PasswordType, nullable=False)
    country = db.Column(db.String, nullable=False)
    state = db.Column(db.String)

    stocks = db.relationship(
        'Stock', secondary="user_stocks", primaryjoin=(), secondaryjoin=(), backref='users')

    @classmethod
    def set_password(cls, password):
        """create hashed password"""
        cls.password = bcrypt.generate_password_hash(password).decode('UTF-8')

    @classmethod
    def check_password(cls, username, password):
        """check hashed password"""
        cls.password = bcrypt.check_password_hash(cls.password, password)

    def __repr__(self):
        u = self
        return f'< User: id={u.id}, username={u.username}, email={u.email}, password=HIDDEN, country={u.country}, state={u.state} >'


class Stock(db.Model):
    """Stock model"""

    __tablename__ = "stocks"

    stock_symbol = db.Column(db.String, primary_key=True)
    stock_name = db.Column(db.String, nullable=False)

    def __repr__(self):
        s = self
        return f'< Stock: stock_symbol={s.stock_symbol}, stock_name={s.stock_name} >'


class Notify_Period_Enum(Enum):
    daily = 'daily'
    weekly = 'weekly'
    monthly = 'monthly'


class User_Stock(db.Model):
    """user_stock model"""

    __tablename__ = "user_stocks"

    id = db.Column(db.Integer, primary_key=True)
    stock_symbol = db.Column(db.String, db.ForeignKey('stocks.stock_symbol'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    notification_period = db.Column(
        db.Enum(Notify_Period_Enum), nullable=False, default=Notify_Period_Enum.weekly.value)
    start_date = db.Column(db.DateTime, nullable=False)
    start_stock_price = db.Column(db.Numeric, nullable=False)
    current_date = db.Column(db.DateTime, nullable=False)
    curr_stock_price = db.Column(db.Numeric, nullable=False)
    stock_num = db.Column(db.Integer, default=None)

    def __repr__(self):
        u = self
        return f'< User_Stock: id={u.id}, stock_symbol={u.stock_symbol}, user_id={u.user_id}, notification_period={u.notification_period}, start_date={u.start_date}, start_stock_price={u.start_stock_price}, current_date={u.current_date}, curr_stock_price={u.curr_stock_price}, stock_num={u.stock_num} >'


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)
