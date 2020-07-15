import os

# set variables from secrets or from environment variables
if os.environ.get('APP_KEY') is None:
    from secrets import APP_KEY, MAIL_PASSWORD, MAIL_USER
else:
    APP_KEY = os.environ.get('APP_KEY')
    MAIL_USER = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

class Config(object):
    """set flask config variables"""

    TESTING = False
    DEBUG = False
    CSRF_ENABLED = True 
    SECRET_KEY = APP_KEY
    
    # database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgres:///stock_tracker')

    # flask-mail



class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False