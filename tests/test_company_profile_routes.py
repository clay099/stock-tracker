"""views test"""
import sys

sys.path.insert(0, "..")

import os
from unittest import TestCase
from secrets import APP_KEY, MAIL_PASSWORD, MAIL_USER

from sqlalchemy import exc
from models import db, connect_db, User, Stock, User_Stock, finnhub_client, News, Peer

# use testing DB - needs to run before import app
os.environ['DATABASE_URL'] = "postgresql:///stock-tracker-test"

from app import app
# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['SQLALCHEMY_ECHO'] = False

# Don't have WTForms use CSRF at all
app.config['WTF_CSRF_ENABLED'] = False

db.drop_all()
db.create_all()

class CompanyAndNewsViewsTestCase(TestCase):
    """Company and News test case"""

    # Users & stocks to be created once (not for every test) to limit API calls (limited to 60 per min)
    u = User.signup("testUser", "testUser@gmail.com",
                    "password", "USA", "CA")
    u.id = 9876

    u_stock = User_Stock.add_stock(u.id, "AAPL", "5")

    db.session.add_all([u, u_stock])
    db.session.commit()


    def setUp(self):
        """create test client, add sample data"""

        self.client = app.test_client()

        u = User.query.get(9876)
        self.u = u
        u_stock = User_Stock.query.filter_by(stock_symbol = 'AAPL').filter_by(user_id=self.u.id)
        self.u_stock = u_stock[0]
        self.s = Stock.query.get('AAPL')

    def tearDown(self):
        db.session.rollback()

    def test_company_details_route_existing_stock(self):
        """test company details with a stock already in database"""
        with self.client as c:
            resp = c.get('/company-details/AAPL')

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'To see further peer details click on the below links', resp.data)

    def test_company_details_route_existing_stock(self):
        """test company details with a stock already in database"""
        with self.client as c:
            resp = c.get('/company-details/AAPL')

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'To see further peer details click on the below links', resp.data)

    def test_company_details_route_new_stock(self):
        """test company details with a stock not currently in database"""
        with self.client as c:
            resp = c.get('/company-details/GS')

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'To see further peer details click on the below links', resp.data)

            stock = Stock.query.get('GS')
            self.assertEqual('GS', stock.stock_symbol[0])
    
    def test_company_details_route_invalid_stock(self):
        """test company details when stock symbol is not valid"""
        with self.client as c:
            resp = c.get('/company-details/INVALIDNAME', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'Stock was not found', resp.data)

    def test_send_stock_details_route(self):
        """test send stock details"""
        with self.client as c:
            resp = c.post('/api/company-details', json={'stock_symbol':'AAPL'})

            data = resp.json['stock']
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['currency'], 'USD')
            self.assertEqual(data['country'], 'US')
            self.assertEqual(data['name'], 'Apple Inc')
            self.assertEqual(data['ipo'], '1980-12-12')

    def test_send_stock_details_route_invalid_stock(self):
        """test send stock details when stock symbol is not valid"""
        with self.client as c:
            resp = c.post('/api/company-details', json={'stock_symbol':'INVALIDNAME'})

            self.assertEqual(resp.status_code, 404)
    
    def test_send_advanced_stock_details_route(self):
        """test send stock details"""
        with self.client as c:
            resp = c.post('/api/advanced-company-details', json={'stock_symbol':'AAPL'})

            data = resp.json['stock']
            peers = resp.json['peers']
            self.assertEqual(resp.status_code, 200)
            self.assertGreater(data['price'], '0')
            self.assertGreater(data['targetMean'], '0')
            self.assertGreater(data['yearlyHigh'], '0')
            self.assertIsNotNone(peers[0])
    
    def test_send_advanced_stock_details_route_invalid_stock(self):
        """test send stock details when stock symbol is not valid"""
        with self.client as c:
            resp = c.post('/api/advanced-company-details', json={'stock_symbol':'INVALIDNAME'})

            self.assertEqual(resp.status_code, 404)

    def test_news_route(self):
        """test news route with stock symbol sent via json"""
        with self.client as c:
            resp = c.post('/api/company-details/news', json={'stock_symbol':'AAPL'})

            data = resp.json['news']
            self.assertEqual(resp.status_code, 200)
            # only testing the first news article returned
            self.assertIsNotNone(data[0]['category'])
            self.assertIsNotNone(data[0]['datetime'])
    
    def test_news_route_invalid_stock(self):
        """test news route when stock symbol is not valid"""
        with self.client as c:
            resp = c.post('/api/company-details/news', json={'stock_symbol':'INVALIDNAME'})

            self.assertEqual(resp.status_code, 404)

    def test_news_route_with_no_json(self):
        """test news route when not stock symbol given"""
        with self.client as c:
            resp = c.post('/api/company-details/news')

            data = resp.json['news']
            self.assertEqual(resp.status_code, 200)
            # only testing the first news article returned
            self.assertIsNotNone(data[0]['category'])
            self.assertIsNotNone(data[0]['datetime'])