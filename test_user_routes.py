"""views test"""

import os
from unittest import TestCase
from secrets import APP_KEY, MAIL_PASSWORD, MAIL_USER

from sqlalchemy import exc
from models import db, connect_db, User, Stock, User_Stock, finnhub_client, News, Peer

# use testing DB - needs to run before import app
os.environ['DATABASE_URL'] = "postgresql:///stock-tracker-test"

from app import app, mail
# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['SQLALCHEMY_ECHO'] = False

# Don't have WTForms use CSRF at all
app.config['WTF_CSRF_ENABLED'] = False

db.drop_all()
db.create_all()

class UserViewsTestCase(TestCase):
    """basic portfolio views test case"""

    # Users & stocks to be created once (not for every test) to limit API calls (limited to 60 per min)
    u = User.signup("testUser", "testUser@gmail.com",
                    "password", "USA", "CA")
    u.id = 9876

    u_stock = User_Stock.add_stock(u.id, "AAPL", "5")
    u_stock_2 = User_Stock.add_stock(u.id, "UNH", "1")

    db.session.add_all([u, u_stock, u_stock_2])
    db.session.commit()


    def setUp(self):
        """create test client, add sample data"""

        self.client = app.test_client()

        u = User.query.get(9876)
        self.u = u
        u_stock = User_Stock.query.filter_by(stock_symbol = 'AAPL').filter_by(user_id=self.u.id)
        self.u_stock = u_stock[0]
        u_stock_2 = User_Stock.query.filter_by(stock_symbol = 'UNH').filter_by(user_id=self.u.id)
        self.u_stock_2 = u_stock_2[0]
        self.s = Stock.query.get('AAPL')

    def tearDown(self):
        db.session.rollback()
    
    def test_portfolio_route(self):
        """test portfolio route"""
        with self.client as c:
            login = c.post('/login', data={"login_username": self.u.username, "login_password": 'password'})

            resp = c.get('/user') 

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'TOTAL PORTFOLIO VALUE', resp.data)
    
    def test_portfolio_route_not_signed_in(self):
        """test portfolio route when not signed in"""
        with self.client as c:

            resp = c.get('/user', follow_redirects=True) 

            self.assertEqual(resp.status_code, 405)
    
    def test_add_stock_route(self):
        """test add_stock route"""
        with self.client as c:
            login = c.post('/login', data={"login_username": self.u.username, "login_password": 'password'})

            resp = c.post('/user/add', data={"stock_symbol": 'MS', "stock_num": '1'}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Stock added", resp.data)

    def test_add_stock_route_not_valid_stock(self):
        """test add_stock route with a stock Symbol which is not valid"""
        with self.client as c:
            login = c.post('/login', data={"login_username": self.u.username, "login_password": 'password'})

            resp = c.post('/user/add', data={"stock_symbol": 'THISISNOTVALID', "stock_num": '1'}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Stock Symbol Not Recognized", resp.data)
        
    def test_add_stock_route_stock_exists(self):
        """test add_stock route with a stock Symbol which already exists in user portfolio"""
        with self.client as c:
            login = c.post('/login', data={"login_username": self.u.username, "login_password": 'password'})

            resp = c.post('/user/add', data={"stock_symbol": 'AAPL', "stock_num": '1'}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Stock already in portfolio", resp.data)
    
    
    def test_add_stock_route_not_signed_in(self):
        """test add_stock route can only be accessed when signed in"""
        with self.client as c:
            resp = c.post('/user/add', data={"stock_symbol": 'AAPL', "stock_num": '1'}, follow_redirects=True)

            self.assertEqual(resp.status_code, 405)

    def test_user_settings_get_route(self):
        """test user settings get route"""
        with self.client as c:

            login = c.post('/login', data={"login_username": self.u.username, "login_password": 'password'})

            resp = c.get('/user/settings')

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'Update User Settings', resp.data)
            # checks that current details have been prefilled
            self.assertIn(self.u.username, str(resp.data))
            self.assertIn(self.u.email, str(resp.data))
            self.assertIn(self.u.country, str(resp.data))

    def test_user_settings_post_route(self):
        """test user settings post route with updated details"""
        with self.client as c:

            login = c.post('/login', data={"login_username": self.u.username, "login_password": 'password'})

            resp = c.post('/user/settings', data={'username': 'newUserName', 'email': self.u.email, 'password': self.u.password, 'country': self.u.country, 'state': self.u.state}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'settings have been updated', resp.data)
            self.assertIn(b'newUserName', resp.data)
        
    def test_user_settings_post_route_login_required(self):
        """test user settings post route can only be accessed if logged in"""
        with self.client as c:
            resp = c.post('/user/settings', data={'username': 'newUserName', 'email': self.u.email, 'password': self.u.password, 'country': self.u.country, 'state': self.u.state}, follow_redirects=True)

            self.assertEqual(resp.status_code, 405)

    def test_edit_password_route(self):
        """test updating user password"""
        with self.client as c:

            login = c.post('/login', data={"login_username": self.u.username, "login_password": 'password'})

            resp = c.post('user/password', data={'current_password': 'password', 'new_password': 'newPW', 'confirm_new_password':'newPW'}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'password has been updated', resp.data)

            # reset password back to original for future tests
            resp = c.post('user/password', data={'current_password': 'newPW', 'new_password': 'password', 'confirm_new_password':'password'}, follow_redirects=True)

    def test_edit_password_route_wrong_current_pw(self):
        """test updating user password with wrong current password does not let the password update"""
        with self.client as c:

            login = c.post('/login', data={"login_username": self.u.username, "login_password": 'password'})

            resp = c.post('user/password', data={'current_password': 'WrongPW', 'new_password': 'newPW', 'confirm_new_password':'newPW'}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'Invalid credentials', resp.data)

    def test_edit_password_route_new_pw_not_matched(self):
        """test updating user password with new passwords which do not match does not update password"""
        with self.client as c:

            login = c.post('/login', data={"login_username": self.u.username, "login_password": 'password'})

            resp = c.post('user/password', data={'current_password': 'password', 'new_password': 'newPW1', 'confirm_new_password':'newPW2'}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'New Passwords do not match', resp.data)

    def test_edit_password_route_login_required(self):
        """test updating user password can only be accessed when logged in"""
        with self.client as c:
            resp = c.post('user/password', data={'current_password': 'password', 'new_password': 'newPW', 'confirm_new_password':'newPW'}, follow_redirects=True)

            self.assertEqual(resp.status_code, 405)

    def test_edit_stock_route(self):
        """test edit stock route"""
        with self.client as c:
            login = c.post('/login', data={"login_username": self.u.username, "login_password": 'password'})

            resp = c.post('/user/stock', data={'stock_num':'100000','stock_symbol':self.u_stock.stock_symbol}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'100000', resp.data)
    
    def test_edit_stock_stock_symbol_not_valid(self):
        """test edit stock route with a stock symbol which is not in the User_Stock portfolio"""
        with self.client as c:
            login = c.post('/login', data={"login_username": self.u.username, "login_password": 'password'})

            resp = c.post('/user/stock', data={'stock_num':'100000','stock_symbol':'NOTVALID'}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'an error occurred', resp.data)
    
    def test_edit_stock_stock_symbol_login_required(self):
        """test edit stock route can only be accessed when logged in"""
        with self.client as c:
            resp = c.post('/user/stock', data={'stock_num':'100000','stock_symbol':self.u_stock.stock_symbol}, follow_redirects=True)

            self.assertEqual(resp.status_code, 405)

    def test_send_portfolio_route(self):
        """test flask mail"""
    
        with mail.record_messages() as outbox:
            with self.client as c:
                login = c.post('/login', data={"login_username": self.u.username, "login_password": 'password'})

                resp = c.get('/user/send-portfolio', follow_redirects=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn(b'Portfolio Snap Shot Sent', resp.data)
                self.assertEqual(len(outbox), 1)
                self.assertEqual(outbox[0].subject, 'Portfolio SnapShot')

    def test_send_portfolio_login_required(self):
        """test send portfolio route can only be accessed when logged in"""
        with self.client as c:
            resp = c.get('/user/send-portfolio', follow_redirects=True)

            self.assertEqual(resp.status_code, 405)

    def test_delete_stock_route(self):
        """test delete stock route"""

        new_stock = User_Stock.add_stock(9876, "GS", "1")
        db.session.add(new_stock)
        db.session.commit()

        with self.client as c:
            login = c.post('/login', data={"login_username": self.u.username, "login_password": 'password'})

            resp = c.post('/user/stock/delete', data={'stock_symbol': 'GS'}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('GS has been deleted from your portfolio', str(resp.data))
    
    def test_delete_stock_symbol_not_valid(self):
        """test delete stock route with not a valid stock symbol"""
        with self.client as c:
            login = c.post('/login', data={"login_username": self.u.username, "login_password": 'password'})

            resp = c.post('/user/stock/delete', data={'stock_symbol': 'NOTVALID'}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('An error occurred', str(resp.data))

    def test_delete_stock_symbol_login_required(self):
        """test delete stock route can only be accessed when logged in"""
        with self.client as c:
            resp = c.post('/user/stock/delete', data={'stock_symbol': 'NOTVALID'}, follow_redirects=True)

            self.assertEqual(resp.status_code, 405)