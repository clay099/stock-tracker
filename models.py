from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()


class User(db.Model):
    """User model"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False)
    state = db.Column(db.String)

    stocks = db.relationship(
        'Stock', secondary="user_stocks", primaryjoin=(), secondaryjoin=(), backref='users')

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


class User_Stock(db.Model):
    """user_stock model"""

    __tablename__ = "user_stocks"

    id = db.Column(db.Integer, primary_key=True)
    stock_symbol = db.Column(db.String, db.ForeignKey('stocks.stock_symbol'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    notification_period = db.Column(db.String, nullable=False)
    start_date = db.Column(db.Timestamp, nullable=False)
    start_stock_price = db.Column(db.Decimal, nullable=False)
    current_date = db.Column(db.Timestamp, nullable=False)
    curr_stock_price = db.Column(db.decimal, nullable=False)
    stock_num = db.Column(db.Integer, default=None)

    def __repr__(self):
        u = self
        return f'< User_Stock: id={u.id}, stock_symbol={u.stock_symbol}, user_id={u.user_id}, notification_period={u.notification_period}, start_date={u.start_date}, start_stock_price={u.start_stock_price}, current_date={u.current_date}, curr_stock_price={u.curr_stock_price}, stock_num={u.stock_num} >'


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)
