"""model test"""

import os
from unittest import TestCase
from models import db, Peer, Stock

from sqlalchemy import exc

# use testing DB - needs to run before import app
os.environ['DATABASE_URL'] = "postgresql:///stock-tracker-test"

from app import app

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['SQLALCHEMY_ECHO'] = False

# drop all tables & create new ones
db.drop_all()
db.create_all()

class PeerModelTestCase(TestCase):
    """test peer model"""

    def setUp(self):
        """create test client, add sample data"""

        s = Stock(stock_symbol="AAPL", stock_name="Apple")
        p = Peer(lead_stock_symbol=s.stock_symbol, peer_stock_symbol='MSFT')
        p.id = 9876

        db.session.add_all([s, p])
        db.session.commit()
        self.p = p

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        Peer.query.delete()
        Stock.query.delete()
        return res

    def test_peer_model(self):
        """test base peer model"""

        peer = Peer.query.get(self.p.id)

        self.assertEqual(peer.lead_stock_symbol, 'AAPL')
        self.assertEqual(peer.peer_stock_symbol, 'MSFT')
    
    def test_user_repr(self):
        """test peer repr"""

        self.assertEqual(
            repr(self.p), f'< Peer: id={self.p.id}, lead_stock_symbol={self.p.lead_stock_symbol}, peer_stock_symbol={self.p.peer_stock_symbol} >')