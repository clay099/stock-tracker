import os

from flask import Flask, render_template, request, flash, redirect, session, g, url_for, abort
from flask_debugtoolbar import DebugToolbarExtension
import finnhub
from secrets import API_KEY, APP_KEY
from flask_login import LoginManager

from models import db, connect_db, User, Stock, User_Stock
from forms import NewUserForm, LoginForm, Stock, UserStockForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///stock_tracker'))
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', APP_KEY)

toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

# Configure API key
configuration = finnhub.Configuration(
    api_key={
        'token': API_KEY
    }
)

finnhub_client = finnhub.DefaultApi(finnhub.ApiClient(configuration))

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/')
def homepage():
    return render_template('home.html')


@app.route('/login')
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect(url_for("homepage"))
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = NewUserForm()
    if form.validate_on_submit():
        return redirect(url_for("homepage"))
    return render_template('signup.html', form=form)
