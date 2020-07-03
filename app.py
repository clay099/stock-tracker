import os

from flask import Flask, render_template, request, flash, redirect, session, url_for, abort
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager, logout_user, current_user, login_user, login_required
from sqlalchemy.exc import IntegrityError

from secrets import APP_KEY

from models import db, connect_db, User, Stock, User_Stock, finnhub_client
from forms import NewUserForm, LoginForm, NewStockForm, UserSettings, UpdatePassword, EditStock
from sqlalchemy.exc import IntegrityError


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///stock_tracker'))
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', APP_KEY)

toolbar = DebugToolbarExtension(app)

connect_db(app)
# db.create_all()


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
    flash('You must be logged in to view that page.', 'warning')
    return redirect(url_for('login'))

# ************base routes************


@app.route('/')
def homepage():
    """home page"""
    return render_template('home.html')


@app.route('/about')
def about():
    """about page"""
    return render_template('about.html')


# ************auth routes************
@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        user = User.check_password(form.username.data, form.password.data)

        if user:
            login_user(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect(url_for('portfolio'))

        flash("Invalid credentials.", 'warning')
    return render_template('auth/login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = NewUserForm(notification_period='weekly')

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
                notification_period=form.notification_period.data
            )

            db.session.commit()
            login_user(user)

            flash('User Created', 'success')

            return redirect(url_for('portfolio'))

        flash('Username is already taken', 'warning')

    return render_template('auth/signup.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out", "success")
    return redirect(url_for('login'))


# ************user routes************

@app.route('/user')
@login_required
def portfolio():

    form = NewStockForm()
    edit_stock_form = EditStock()
    stock_details = User_Stock.get_users_stocks(current_user.id)

    return render_template('user/portfolio.html', form=form, stock_details=stock_details, edit_stock_form=edit_stock_form)


@app.route('/user/add', methods=['POST'])
@login_required
def add_stock():

    form = NewStockForm()

    if form.validate_on_submit():

        user_id = current_user.id

        new_stock = User_Stock.add_stock(
            user_id,
            form.stock_symbol.data,
            form.stock_num.data,
            form.notification_period.data)

        if new_stock:
            try:
                db.session.commit()
                flash('Stock added', 'success')
                return redirect(url_for('portfolio'))
            except IntegrityError:
                flash('Stock already in portfolio', 'warning')
                return redirect(url_for('portfolio'))

        flash('Stock Symbol Not Recognized', 'warning')

    return redirect(url_for('portfolio'))


@app.route('/user/settings', methods=['GET', 'POST'])
@login_required
def user_settings():
    user = User.query.get(current_user.id)
    form = UserSettings(obj=user)
    password_form = UpdatePassword()
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        flash(f"{user.username} settings have been updated", "success")
        return redirect(url_for('portfolio'))
    if password_form.validate_on_submit():
        user = User.check_password(
            current_user.username, form.current_password.data)

        if user:
            updated_user = User.update_password(
                user, form.new_password.data, form.confirm_new_password.data)
            if updated_user:
                flash(f"{user.username} password has been updated", "success")
                return redirect(url_for('portfolio'))

            flash('New Passwords do not match', 'warning')

    return render_template('user/settings.html', form=form, password_form=password_form)


@app.route('/user/password', methods=['POST'])
@login_required
def edit_password():
    password_form = UpdatePassword()
    if password_form.validate_on_submit():
        user = User.check_password(
            current_user.username, password_form.current_password.data)

        if user:
            updated_user = User.update_password(
                user, password_form.new_password.data, password_form.confirm_new_password.data)
            if updated_user:
                db.session.commit()
                flash(f"{user.username} password has been updated", "success")
                return redirect(url_for('portfolio'))

            flash('New Passwords do not match', 'warning')
        else:
            flash("Invalid credentials.", 'warning')
    return redirect(url_for('user_settings'))


@app.route('/user/stock', methods=['POST'])
@login_required
def edit_stock():
    form = EditStock()
    if form.validate_on_submit():

        user_stock = User_Stock.query.filter_by(
            user_id=current_user.id).filter_by(stock_symbol=form.stock_symbol.data).first()
        user_stock.stock_num = form.stock_num.data
        user_stock.stock_symbol = form.stock_symbol.data

        db.session.commit()
        return redirect(url_for('portfolio'))

    return redirect(url_for('portfolio'))

    ##############################################################################
    # Turn off all caching in Flask
    #   (useful for dev; in production, this kind of stuff is typically
    #   handled elsewhere)
    #
    # https://stackoverflow.com/questions/34066804/disabling-caching-in-flask


@ app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
