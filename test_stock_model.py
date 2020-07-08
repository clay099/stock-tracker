"""model test"""

import os
from unittest import TestCase
from models import db

from sqlalchemy import exc

from models import Stock

# use testing DB - needs to run before import app
os.environ['DATABASE_URL'] = "postgresql:///stock-tracker-test"

from app import app
# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['SQLALCHEMY_ECHO'] = False

db.drop_all()
db.create_all()


class StockModelTestCase(TestCase):
    """test stock models"""

    def setUp(self):
        """create test client, add sample data"""
        Stock.query.delete()
        stock = Stock(stock_symbol="AAPL", stock_name="Apple")
        db.session.add(stock)
        db.session.commit()
        self.stock = stock

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_stock_model(self):
        """test base stock model"""

        self.assertEqual(self.stock.stock_symbol, "AAPL")
        self.assertEqual(self.stock.stock_name, "Apple")

    def test_missing_stock_symbol_signup(self):
        """test midding stock symbol"""

        invalid_stock = Stock(stock_name="United Health Group")
        with self.assertRaises(exc.IntegrityError):
            db.session.add(invalid_stock)
            db.session.commit()

    def test_missing_stock_name_signup(self):
        """test missing stock name"""

        invalid_stock = Stock(stock_symbol="UNH")
        with self.assertRaises(exc.IntegrityError):
            db.session.add(invalid_stock)
            db.session.commit()

    def test_user_repr(self):
        """test user repr"""

        self.assertEqual(
            repr(self.stock), f'< Stock: stock_symbol={self.stock.stock_symbol}, stock_name={self.stock.stock_name} >')
