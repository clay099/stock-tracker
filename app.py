import os

from flask import Flask, render_template, request, flash, redirect, session, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager, logout_user, current_user, login_user, login_required
from sqlalchemy.exc import IntegrityError
from flask_mail import Mail, Message

from secrets import APP_KEY, MAIL_PASSWORD, MAIL_USER

from models import db, connect_db, User, Stock, User_Stock, finnhub_client, News
from forms import NewUserForm, LoginForm, NewStockForm, UserSettings, UpdatePassword, EditStock
from sqlalchemy.exc import IntegrityError


app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or, if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///stock_tracker'))
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', APP_KEY)


app.config.update(
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME', MAIL_USER),
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD', MAIL_PASSWORD),
    MAIL_DEFAULT_SENDER=os.environ.get('MAIL_USERNAME', MAIL_USER)
)

mail = Mail(app)

toolbar = DebugToolbarExtension(app)

connect_db(app)
# db.drop_all()
# db.create_all()


# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        return User.query.get_or_404(user_id)
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
    login_form = LoginForm()
    new_user_form = NewUserForm()

    return render_template('home.html', login_form=login_form, new_user_form=new_user_form)


@app.route('/login', methods=['POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.check_password(
            login_form.login_username.data, login_form.login_password.data)

        if user:
            login_user(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect(url_for('portfolio'))

        flash("Invalid credentials.", 'warning')
    return redirect(url_for('homepage'))


@app.route('/signup', methods=['POST'])
def signup():
    new_user_form = NewUserForm()

    if new_user_form.validate_on_submit():
        existing_user = User.query.filter_by(
            username=new_user_form.username.data).first()
        if existing_user is None:
            user = User.signup(
                username=new_user_form.username.data,
                email=new_user_form.email.data,
                password=new_user_form.password.data,
                country=new_user_form.country.data,
                state=new_user_form.state.data
            )

            db.session.commit()
            login_user(user)

            flash('User Created', 'success')

            return redirect(url_for('portfolio'))

        flash('Username is already taken', 'warning')
    return redirect(url_for('homepage'))


@app.route('/about')
def about():
    """about page"""
    return render_template('about.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out", "success")
    return redirect(url_for('homepage'))


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
            form.stock_num.data)

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
    user = User.query.get_or_404(current_user.id)
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
        flash(f"stock has been edited", "success")
        return redirect(url_for('portfolio'))

    return redirect(url_for('portfolio'))


@app.route('/user/stock/delete', methods=['POST'])
@login_required
def delete_stock():

    symbol = request.form['stock_symbol']

    user_stock = User_Stock.query.filter_by(
        user_id=current_user.id).filter_by(stock_symbol=symbol).first()
    if user_stock:
        db.session.delete(user_stock)
        db.session.commit()
        flash(f'{symbol} has been deleted from your portfolio', 'warning')
    else:
        flash(f'An error occurred', 'warning')

    return redirect(url_for('portfolio'))


@app.route('/user/send-portfolio')
@login_required
def send_portfolio():

    stock_details = User_Stock.get_users_stocks(current_user.id)

    msg = Message('Porfolio SnapShot', recipients=[current_user.email])
    msg.html = render_template(
        'user/_portfolio_summary.html', stock_details=stock_details)
    mail.send(msg)
    flash(f"Portfolio Snap Shot Sent", "success")

    return redirect(url_for('portfolio'))

@app.route('/api/company-details', methods=['POST'])
@login_required
def send_stock_details():
    stock_symbol = request.json.get('stock_symbol')

    returned_stock_details = Stock.query.get_or_404(stock_symbol)

    if returned_stock_details.ipo:
        return jsonify(stock=returned_stock_details.serialize_basic_stock_details())
    else:
        returned_stock_details = Stock.add_stock_details(stock_symbol)
        # add to database
        db.session.add(returned_stock_details)
        db.session.commit()
        return jsonify(stock=returned_stock_details.serialize_basic_stock_details())

@app.route('/api/company-details/news', methods=['POST'])
@login_required
def get_news():
    stock_symbol = request.json.get('stock_symbol')
    # checks that a stock_symbol was provided with JSON
    if stock_symbol:
        # request for stock object
        returned_stock_details = Stock.query.get(stock_symbol)
        if returned_stock_details:
            # get news for stock
            returned_news = News.get_news(stock_symbol)

            all_news = [news.serialize_news() for news in returned_news]
            return jsonify(news=all_news)

        # if stock object not in DB
        else:
            # search API for stock symbol
            returned_stock_details = Stock.add_stock_symbol(stock_symbol)
            # if stock symbol returned true (stock found and added to our DB)
            if returned_stock_details:
                returned_news = News.get_news(stock_symbol)
                all_news = [news.serialize_news() for news in returned_news]
                return jsonify(news=all_news)
                
            # if stock symbol returned false (stock not found in API)
            else:
                flash('Stock was not found', 'warning')
                return url_for('homepage')

@app.route('/company-details/<stock_symbol>')
def company_details(stock_symbol):
    returned_stock_details = Stock.query.get_or_404(stock_symbol)
    company_name = returned_stock_details.stock_name
    return render_template('/stock/detailed_stock_view.html', stock_symbol=stock_symbol, company_name=company_name)

##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
