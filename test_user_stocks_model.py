"""model test"""

from app import app
import os
from unittest import TestCase
from models import db
from datetime import datetime

from sqlalchemy import exc

from models import User, Stock, User_Stock

# use testing DB
os.environ['DATABASE_URL'] = "postgresql:///stock-tracker-test"
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# disable csrf checks
app.config['WTF_CSRF_ENABLED'] = False

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """test models"""

    def setUp(self):
        """create test client, add sample data"""
        # drop all tables & create new ones

        self.client = app.test_client()

        User_Stock.query.delete()
        Stock.query.delete()
        User.query.delete()

        u = User.signup("testUser", "testUser@gmail.com",
                        "password", "USA", "CA")
        u.id = 9876

        u_stock = User_Stock.add_stock(9876, "AAPL", "5")

        db.session.add_all([u, u_stock])
        db.session.commit()
        self.u = u
        self.u_stock = u_stock

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_adding_stock(self):
        """test adding stock works"""

        new_user_stock = User_Stock.add_stock(9876, "MSFT", 1)
        db.session.add(new_user_stock)
        db.session.commit()

        # checks stock was added to Stock model
        self.assertEqual(new_user_stock.stock_symbol,
                         Stock.query.get("MSFT").stock_symbol)
        # checks a start date was added
        self.assertIsNotNone(new_user_stock.start_date)
        # checks a current date was added
        self.assertIsNotNone(new_user_stock.current_date)
        # checks a start stock price was added
        self.assertIsNotNone(new_user_stock.start_stock_price)
        # checks a current stock price was added
        self.assertIsNotNone(new_user_stock.start_stock_price)
        # checks a stock num was added
        self.assertIsNotNone(new_user_stock.stock_num)

    def test_add_stock_symbol(self):
        """test adding a valid stock symbol works and added to stock model"""
        new_user_stock = User_Stock.add_stock(9876, "MSFT", 1)
        # finds and adds stock_symbol and stock_name to Stock Model
        db.session.add(new_user_stock)
        db.session.commit()

        # checks stock was added to Stock model
        self.assertEqual(new_user_stock.stock_symbol,
                         Stock.query.get("MSFT").stock_symbol)

    def test_add_stock_symbol_not_valid(self):
        """tests that unvalid stock symbols are not returned a value"""

        new_user_stock = User_Stock.add_stock(
            9876, "MSJDSJAKLFLDSJAKLFJLSDKALJFS", 1)
        # finds and adds stock_symbol and stock_name to Stock Model

        self.assertIsNone(new_user_stock)

    def test_get_users_stocks(self):
        """tests that get_user_stocks function returns a tupel with flaskSQL object, value for current val and initial val"""

        returned = User_Stock.get_users_stocks(user_id=self.u.id)
        # checks a value is returned for total initial val
        self.assertIsNotNone(returned[1])
        # checks a value is returned for total current val
        self.assertIsNotNone(returned[2])
        # checks that the original stock is returned
        self.assertIn(returned[0][0].stock_symbol, self.u_stock.stock_symbol)

    def test_update_stock(self):
        """test that update stock function updates the user_stock values"""

        update_stock = self.u_stock.update_stock(self.u_stock)
        # checks that datetime is updated
        self.assertIsNotNone(update_stock.current_date)
        # checks that price is returned
        self.assertIsNotNone(update_stock.curr_stock_price)

    def test_user_stock_repr(self):
        """test user repr"""

        u = self.u_stock
        self.assertEqual(
            repr(u), f'< User_Stock: stock_symbol={u.stock_symbol}, user_id={u.user_id}, start_date={u.start_date}, start_stock_price={u.start_stock_price}, current_date={u.current_date}, curr_stock_price={u.curr_stock_price}, stock_num={u.stock_num} >')
