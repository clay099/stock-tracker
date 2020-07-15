"""model test"""
import sys

sys.path.insert(0, "..")

import os
from unittest import TestCase
from models import db

from sqlalchemy import exc

from models import Stock, Peer

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
        stock = Stock(stock_symbol="AAPL", stock_name="Apple")
        db.session.add(stock)
        db.session.commit()
        self.stock = stock

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        Peer.query.delete()
        Stock.query.delete()
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

    def test_add_stock_details(self):
        """test adding stock details function"""
        s = self.stock.add_stock_details('AAPL')
        self.assertEqual(s.country, ('US',))
        self.assertEqual(s.currency, ('USD',))
        self.assertEqual(s.name, ('Apple Inc',))
        self.assertEqual(s.phone, ('14089961010',))

    def test_add_stock_details_no_stock(self):
        """test adding not a valid stock returns false"""
        self.assertFalse(self.stock.add_stock_details('NOSTOCKNAME'))

    def test_serialize_basic_stock_details(self):
        """test serialize_basic_stock_details function"""
        
        answer = {'country': 'US', 'currency': 'USD', 'exchange': 'NASDAQ NMS - GLOBAL MARKET', 'ipo': '1980-12-12', 'marketCapitalization': '1662998.0', 'name': 'Apple Inc', 'phone': '14089961010', 'shareOutstanding': '4334.335', 'stock_symbol': 'AAPL', 'weburl': 'https://www.apple.com/', 'logo': 'https://static.finnhub.io/logo/87cb30d8-80df-11ea-8951-00000000092a.png', 'finnhubIndustry': 'Technology'}
        
        #add stock details
        s = self.stock.add_stock_details('AAPL')
        db.session.add(s)
        db.session.commit()
        serialized = s.serialize_basic_stock_details()
        self.assertEqual(answer, serialized)

    def test_add_basic_financials(self):
        """test add basic financials function"""
        s = self.stock.add_basic_financial('AAPL')
        self.assertTrue(s)
        self.assertIsNotNone(self.stock.yearlyHigh)
    
    def test_add_basic_financials_fail(self):
        """test add basic financials function returns false with a stock symbol which is not valid"""
        s = self.stock.add_basic_financial('NOSTOCKNAME')
        self.assertFalse(s)

    def test_add_rec_trend(self):
        """test add_rec_trend function"""
        s = self.stock.add_rec_trend('AAPL')
        self.assertTrue(s)
        self.assertIsNotNone(self.stock.period)

    def test_add_rec_trend_fail(self):
        """test add_rec_trend function returns false with a stock symbol which is not valid"""
        s = self.stock.add_rec_trend('NOSTOCKNAME')
        self.assertFalse(s)
    
    def test_add_target(self):
        """test add_target function"""
        s = self.stock.add_target('AAPL')
        self.assertTrue(s)
        self.assertIsNotNone(self.stock.targetHigh)
    
    def test_add_target_fail(self):
        """test add_target function returns false with a stock symbol which is not valid"""
        s = self.stock.add_target('NOSTOCKNAME')
        self.assertFalse(s)

    def test_add_peers(self):
        """test add_peers function"""
        s = self.stock.add_peers('AAPL')
        self.assertTrue(s)
        self.assertIsNotNone(self.stock.peers[0])

    def test_add_peers_fail(self):
        """test add_peers returns false with a stock symbol which is not valid"""
        s = self.stock.add_peers('NOSTOCKNAME')
        self.assertFalse(s)

    def test_stock_repr(self):
        """test user repr function"""

        self.assertEqual(
            repr(self.stock), f'< Stock: stock_symbol={self.stock.stock_symbol}, stock_name={self.stock.stock_name}, country={self.stock.country}, currency={self.stock.currency}, exchange={self.stock.exchange}, ipo={self.stock.ipo}, marketCapitalization={self.stock.marketCapitalization}, name={self.stock.name}, phone={self.stock.phone}, shareOutstanding={self.stock.shareOutstanding}, stock_symbol={self.stock.stock_symbol}, weburl={self.stock.weburl}, logo={self.stock.logo}, finnhubIndustry={self.stock.finnhubIndustry}, yearlyHigh={self.stock.yearlyHigh}, yearlyHighDate={self.stock.yearlyHighDate}, yearlyLow={self.stock.yearlyLow}, yearlyLowDate={self.stock.yearlyLowDate}, beta={self.stock.beta}, buy={self.stock.buy}, hold={self.stock.hold}, period={self.stock.period}, sell={self.stock.sell}, strongBuy={self.stock.strongBuy}, strongSell={self.stock.strongSell}, lastUpdated={self.stock.lastUpdated}, targetHigh={self.stock.targetHigh}, targetLow={self.stock.targetLow}, targetMean={self.stock.targetMean}, targetMedian={self.stock.targetMedian}, price={self.stock.price}, peers={self.stock.peers} >')

