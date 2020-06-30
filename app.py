from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, User, Stock, User_Stock

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///stock_tracker"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)
# db.create_all()


@app.route('/')
def index():
    return "text here"
