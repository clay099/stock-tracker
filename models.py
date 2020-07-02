from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from sqlalchemy_utils import EmailType, PasswordType
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
import finnhub
from secrets import API_KEY
from sqlalchemy.exc import IntegrityError

# Configure API key
configuration = finnhub.Configuration(
    api_key={
        'token': API_KEY
    }
)

finnhub_client = finnhub.DefaultApi(finnhub.ApiClient(configuration))


db = SQLAlchemy()

bcrypt = Bcrypt()


class User(db.Model, UserMixin):
    """User model"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(EmailType, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False)
    state = db.Column(db.String)

    stocks = db.relationship(
        'Stock', secondary="user_stocks",  backref='users')

    @classmethod
    def signup(cls, username, email, password, country, state):
        """create hashed password"""
        hashed_password = bcrypt.generate_password_hash(
            password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_password,
            country=country, state=state
        )
        db.session.add(user)
        return user

    @classmethod
    def check_password(cls, username, password):
        """check hashed password"""

        user = User.query.filter_by(
            username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

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

    stock_symbol = db.Column(db.String, db.ForeignKey(
        'stocks.stock_symbol'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), primary_key=True)
    notification_period = db.Column(
        db.Enum(Notify_Period_Enum), nullable=False, default=Notify_Period_Enum.weekly.value)
    start_date = db.Column(db.DateTime, nullable=False)
    start_stock_price = db.Column(db.Numeric, nullable=False)
    current_date = db.Column(db.DateTime, nullable=False)
    curr_stock_price = db.Column(db.Numeric, nullable=False)
    stock_num = db.Column(db.Integer, default=None)

    @classmethod
    def add_stock(cls, user_id, stock_symbol, stock_num, notification_period):
        time = datetime.utcnow()

        stock_symbol = stock_symbol.upper()
        quote = finnhub_client.quote(stock_symbol)
        price = quote.c

        # check our DB for stock symbol
        check_stock = Stock.query.get(stock_symbol)
        # if Stock symbol not in our DB search finnhub
        if not check_stock:
            try:
                # search for stock on finnhub
                new_stock_profile = finnhub_client.company_profile2(
                    symbol=stock_symbol)
                stock_name = new_stock_profile.name

                # add stock to our DB
                new_stock = Stock(stock_name=stock_name,
                                  stock_symbol=stock_symbol)

                db.session.add(new_stock)
                db.session.commit()

            # stock not found
            except IntegrityError:
                return None

        # create new User_Stock
        add_user_stock = User_Stock(
            stock_symbol=stock_symbol,
            user_id=user_id,
            notification_period=notification_period,
            start_date=time,
            start_stock_price=price,
            current_date=time,
            curr_stock_price=price,
            stock_num=stock_num
        )
        db.session.add(add_user_stock)
        return add_user_stock

    @classmethod
    def get_users_stocks(cls, user_id):
        stocks = User_Stock.query.filter_by(user_id=user_id)
        return stocks

    def __repr__(self):
        u = self
        return f'< User_Stock: id={u.id}, stock_symbol={u.stock_symbol}, user_id={u.user_id}, notification_period={u.notification_period}, start_date={u.start_date}, start_stock_price={u.start_stock_price}, current_date={u.current_date}, curr_stock_price={u.curr_stock_price}, stock_num={u.stock_num} >'


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)
