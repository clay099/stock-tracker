import os

from flask import Flask, render_template, request, flash, redirect, session, g, url_for, abort
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager, logout_user, current_user, login_user, login_required
from sqlalchemy.exc import IntegrityError

import finnhub
from secrets import API_KEY, APP_KEY

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
# db.drop_all()
# db.create_all()

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
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.', 'danger')
    return redirect(url_for('login'))


@app.route('/')
def homepage():
    """home page"""
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        user = User.check_password(form.username.data, form.password.data)

        if user:
            login_user(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect(url_for('homepage'))

        flash("Invalid credentials.", 'danger')
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = NewUserForm()
    print("*****")
    if form.validate_on_submit():
        existing_user = User.query.filter_by(
            username=form.username.data).first()
        if existing_user is None:
            user = User.signup(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                country=form.country.data,
                state=form.state.data,
            )

            db.session.commit()
            login_user(user)

            flash('User Created', 'success')

            return redirect(url_for('login'))

        flash('Username is already taken', 'danger')

    return render_template('signup.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out", "success")
    return redirect(url_for('login'))
