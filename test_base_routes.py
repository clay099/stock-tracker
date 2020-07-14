"""views test"""

import os
from unittest import TestCase
from secrets import APP_KEY, MAIL_PASSWORD, MAIL_USER

from sqlalchemy import exc
from models import db, connect_db, User, finnhub_client, News, Peer
from flask_login import login_user

# use testing DB - needs to run before import app
os.environ['DATABASE_URL'] = "postgresql:///stock-tracker-test"

from app import app
# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['SQLALCHEMY_ECHO'] = False

db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all
app.config['WTF_CSRF_ENABLED'] = False

class BaseViewsTestCase(TestCase):
    """basic views test case"""

    def setUp(self):
        """create test client, add sample data"""

        self.client = app.test_client()

        u = User.signup("testUser", "testUser@gmail.com",
                        "password", "USA", "CA")
        u.id = 9876

        db.session.add(u)
        db.session.commit()
        self.u = u

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        User.query.delete()
        return res


# page text can be obtained from (all assume resp = c.get(<route>)):
    # html = resp.get_data(as_text=True) - then reference html
    # str(resp.data) - note can cause iss with characters
    # enclose the text the check in b'' then check against resp.data 

# examples have been incorporated into the test_homepage route

    def test_homepage(self):
        """test homepage"""

        with self.client as c:
            
            resp = c.get('/')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Create and track your own stock portfolio with zero risk", str(resp.data))
            self.assertIn("About This Project", html)
            self.assertIn(b'General News', resp.data)

    def test_404(self):
        """test 404 error page"""
        with self.client as c:
            
            resp = c.get('/djklasjfkdlasfjlks')

            self.assertEqual(resp.status_code, 404)
            self.assertIn(b"We can't seem to find the page you're looking for.", resp.data)
    
    def test_405(self):
        """test 405 error page"""
        with self.client as c:
            
            resp = c.get('/user', follow_redirects=True)

            self.assertEqual(resp.status_code, 405)
            self.assertIn(b"You are not authorized to view that page.", resp.data)

    def test_login(self):
        """test logging a user"""
        with self.client as c:
            resp = c.post('/login', data={"login_username": self.u.username, "login_password": 'password'}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'Hello, testUser!', resp.data)

    def test_login_wrong_pw(self):
        """test login route with wrong password"""
        with self.client as c:
            resp = c.post('/login', data={"login_username": self.u.username, "login_password": 'wrongpassword'}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'Invalid credentials.', resp.data)
    
    def test_login_wrong_username(self):
        """test login route with wrong username"""
        with self.client as c:
            resp = c.post('/login', data={"login_username": 'wrongUserName', "login_password": 'password'}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'Invalid credentials.', resp.data)

    def test_signup(self):
        """test signup"""
        with self.client as c:
            resp = c.post('/signup', data={"username":"newUser", "email":"newUserEmail@gmail.com", "password":"newUserPW", "country":"USA", "state":"CA"}, follow_redirects=True)

            self.assertIn(b'User Created', resp.data)

    def test_signup_duplicate_user(self):
        """test signup of duplicate user"""
        with self.client as c:
            resp = c.post('/signup', data={"username":self.u.username, "email":self.u.email, "password":"password", "country":"USA", "state":"CA"}, follow_redirects=True)

            self.assertIn(b'Username is already taken', resp.data)

    def test_logout(self):
        """test loggin out route"""
        with self.client as c:
            # need to be logged in first
            resp = c.post('/login', data={"login_username": self.u.username, "login_password": 'password'}, follow_redirects=True)

            logout = c.get('/logout', follow_redirects=True)

            self.assertIn(b'You have been logged out', logout.data)