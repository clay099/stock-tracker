import os

from flask import Flask, render_template, request, flash, redirect, session, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager, logout_user, current_user, login_user, login_required
from sqlalchemy.exc import IntegrityError
from flask_mail import Mail, Message

if os.environ.get('SECRET_KEY',"") == "":
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


# ************Configure Flask-Login************

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

@app.errorhandler(404)
def page_not_found(e):
    """404 error page"""
    return render_template('404.html'), 404

@app.errorhandler(405)
def page_not_found(e):
    """405 error page"""
    return render_template('405.html'), 405

@app.route('/')
def homepage():
    """home page"""
    login_form = LoginForm()
    new_user_form = NewUserForm()

    return render_template('home.html', login_form=login_form, new_user_form=new_user_form)


@app.route('/login', methods=['POST'])
def login():
    """login route"""
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.check_password(
            login_form.login_username.data, login_form.login_password.data)

        # user is only returned if check_password id true
        if user:
            login_user(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect(url_for('portfolio'))
        
        flash("Invalid credentials.", 'warning')
    return redirect(url_for('homepage'))


@app.route('/signup', methods=['POST'])
def signup():
    """signup route"""
    new_user_form = NewUserForm()

    if new_user_form.validate_on_submit():
        existing_user = User.query.filter_by(
            username=new_user_form.username.data).first()
        # checks that username has not been taken
        if existing_user is None:
            # create user
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


@app.route('/logout')
@login_required
def logout():
    """log out user"""
    logout_user()
    flash("You have been logged out", "success")
    return redirect(url_for('homepage'))


# ************user routes************

@app.route('/user')
@login_required
def portfolio():
    """user portfolio page"""

    # newStockForm is displayed as a Modal in the html
    form = NewStockForm()
    # editStockForm is displayed as a Modal in the html
    edit_stock_form = EditStock()
    # used to fill table
    stock_details = User_Stock.get_users_stocks(current_user.id)

    return render_template('user/portfolio.html', form=form, stock_details=stock_details, edit_stock_form=edit_stock_form)


@app.route('/user/add', methods=['POST'])
@login_required
def add_stock():
    """add stock route"""
    form = NewStockForm()

    if form.validate_on_submit():

        user_id = current_user.id

        # adds new user_stock
        new_stock = User_Stock.add_stock(
            user_id,
            form.stock_symbol.data,
            form.stock_num.data)

        if new_stock:
            try:
                db.session.commit()
                flash('Stock added', 'success')
                return redirect(url_for('portfolio'))
            # IntegrityError occurs if primary-key error occurs(PK here is a combination of user_id & stock_symbol)
            except IntegrityError:
                flash('Stock already in portfolio', 'warning')
                return redirect(url_for('portfolio'))

        flash('Stock Symbol Not Recognized', 'warning')

    return redirect(url_for('portfolio'))


@app.route('/user/settings', methods=['GET', 'POST'])
@login_required
def user_settings():
    """user setting route"""

    # this should not be an issue as login is already required
    user = User.query.get_or_404(current_user.id)

    # fill UserSettings form displayed as HTML with current user details
    form = UserSettings(obj=user)
    # to change password additional security is enforced - see forms.py for further details - validation is enforced via a separate route 
    password_form = UpdatePassword()

    # UserSettings validation
    if form.validate_on_submit():
        # update userSettings with completed details
        form.populate_obj(user)
        db.session.commit()
        flash(f"{user.username} settings have been updated", "success")
        return redirect(url_for('portfolio'))

    return render_template('user/settings.html', form=form, password_form=password_form)


@app.route('/user/password', methods=['POST'])
@login_required
def edit_password():
    """edit password route - form is submitted from user_settings"""
    password_form = UpdatePassword()
    if password_form.validate_on_submit():
        # checks original PW entered matches current password
        user = User.check_password(
            current_user.username, password_form.current_password.data)

        if user:
            # form enforces updated PW to be entered twice
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
    """edit stock route"""
    # form submitted from portfolio modal
    form = EditStock()
    if form.validate_on_submit():

        # finds user_stock to edit
        user_stock = User_Stock.query.filter_by(
            user_id=current_user.id).filter_by(stock_symbol=form.stock_symbol.data).first()

        try:
            # update User_stock
            user_stock.stock_num = form.stock_num.data
            user_stock.stock_symbol = form.stock_symbol.data

            db.session.commit()
            flash(f"stock has been edited", "success")
            return redirect(url_for('portfolio'))
        except AttributeError:
            flash(f"an error occurred", "warning")
    return redirect(url_for('portfolio'))


@app.route('/user/stock/delete', methods=['POST'])
@login_required
def delete_stock():
    """delete stock route"""
    # route is accessed via javascript

    symbol = request.form['stock_symbol']

    # finds stock
    user_stock = User_Stock.query.filter_by(
        user_id=current_user.id).filter_by(stock_symbol=symbol).first()
    if user_stock:
        # deletes stock
        db.session.delete(user_stock)
        db.session.commit()
        flash(f'{symbol} has been deleted from your portfolio', 'warning')
    else:
        flash(f'An error occurred', 'warning')

    return redirect(url_for('portfolio'))


@app.route('/user/send-portfolio')
@login_required
def send_portfolio():
    """send portfolio via email route"""

    # get details to send
    stock_details = User_Stock.get_users_stocks(current_user.id)

    # craft message
    msg = Message('Portfolio SnapShot', recipients=[current_user.email])
    msg.html = render_template(
        'user/_portfolio_summary.html', stock_details=stock_details)
    # send message with flask-mail
    mail.send(msg)
    flash(f"Portfolio Snap Shot Sent", "success")

    return redirect(url_for('portfolio'))

# ************news route************

@app.route('/api/company-details/news', methods=['POST'])
def get_news():
    """returns JSON with news model"""

    # checks is a specific company / stock symbol has been requested
    if request.json:
        # checks that a stock_symbol was provided with JSON
        stock_symbol = request.json.get('stock_symbol')
        if stock_symbol:
            # request for stock object
            returned_stock_details = Stock.query.get_or_404(stock_symbol)
            if returned_stock_details:
                # get news for stock
                returned_news = News.get_news(stock_symbol)
                # if no news was returned
                if returned_news is False:
                    return jsonify(news='no news obtained')
                
                # create a list with each item is a dictionary which is able to be jsonify'ed
                all_news = [news.serialize_news() for news in returned_news]
                return jsonify(news=all_news)

    # if no stock symbol passed as json
    returned_news = News.get_news()
    if returned_news is False:
        return jsonify(news='no news obtained')
    all_news = [news.serialize_news() for news in returned_news]
    return jsonify(news=all_news)

# ************company details routes************

@app.route('/company-details/<stock_symbol>')
def company_details(stock_symbol):
    """generate company details route"""
    # check DB for stock
    returned_stock_details = Stock.query.get(stock_symbol)
    if returned_stock_details:
        company_name = returned_stock_details.stock_name
        # render template
        return render_template('/stock/detailed_stock_view.html', stock_symbol=stock_symbol, company_name=company_name)
    
    # if company was not found in DB - search API for stock symbol
    returned_stock_details = User_Stock.add_stock_symbol(stock_symbol)
    # if stock symbol returned true (stock found and added to our DB)
    if returned_stock_details:
        # add stock basic details to DB
        returned_stock_details = Stock.add_stock_details(stock_symbol)
        company_name = returned_stock_details.stock_name
        # render template
        return render_template('/stock/detailed_stock_view.html', stock_symbol=stock_symbol, company_name=company_name)

    # if stock symbol returned false (stock not found in API)
    flash('Stock was not found', 'warning')
    return redirect(url_for('homepage'))

@app.route('/api/company-details', methods=['POST'])
def send_stock_details():
    """returns JSON with basic company details - similar to what is found on portfolio page"""

    stock_symbol = request.json.get('stock_symbol')

    # 404 should not be an issue if we have gotten to this stage
    returned_stock_details = Stock.query.get_or_404(stock_symbol)

    # adds / updates stock details to DB
    returned_stock_details = Stock.add_stock_details(stock_symbol)

    db.session.add(returned_stock_details)
    db.session.commit()

    return jsonify(stock=returned_stock_details.serialize_basic_stock_details())


@app.route('/api/advanced-company-details', methods=['POST'])
def send_advanced_details():
    """returns JSON with advanced company details"""
    stock_symbol = request.json.get('stock_symbol')

    # 404 should not be an issue if gotten to this stage
    returned_stock_details = Stock.query.get_or_404(stock_symbol)

    # sends request to API & adds to database
    returned_fin = Stock.add_basic_financial(stock_symbol)
    returned_rec = Stock.add_rec_trend(stock_symbol)
    returned_target = Stock.add_target(stock_symbol)
    returned_peer = Stock.add_peers(stock_symbol)

    # gets updated stock object
    returned_stock_details = Stock.query.get_or_404(stock_symbol)

    # creates a list containing each peers symbol (peers is a realted SQL object)
    peers = [peer.peer_stock_symbol for peer in returned_stock_details.peers]

    return jsonify(stock=returned_stock_details.serialize_advanced_stock_details(), peers=peers)



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
