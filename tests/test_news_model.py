"""model test"""
import sys

sys.path.insert(0, "..")

from models import News
from models import db
from unittest import TestCase
import os

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


class NewsModelTestCase(TestCase):
    """News test models"""

    def setUp(self):
        """add sample data"""
        News.query.delete()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_get_news_model_no_stock(self):
        """test adding news model"""

        # returns a list of 20 news objects
        articles = News.get_news()

        # tests random selection of articles that data is returned
        self.assertIsNotNone(articles[0].headline)
        self.assertIsNotNone(articles[5].headline)
        self.assertIsNotNone(articles[10].headline)
        self.assertIsNotNone(articles[19].headline)

        self.assertIsNotNone(articles[0].category)
        self.assertIsNotNone(articles[5].category)
        self.assertIsNotNone(articles[10].category)
        self.assertIsNotNone(articles[19].category)

        self.assertIsNotNone(articles[0].summary)
        self.assertIsNotNone(articles[5].summary)
        self.assertIsNotNone(articles[10].summary)
        self.assertIsNotNone(articles[19].summary)
        
        self.assertIsNotNone(articles[0].id)
        self.assertIsNotNone(articles[5].id)
        self.assertIsNotNone(articles[10].id)
        self.assertIsNotNone(articles[19].id)

    def test_get_news_model_with_stock(self):
        """test adding news model with stock"""

        # returns a list of 6 news objects
        articles = News.get_news(stock_symbol='AAPL')

        # tests random selection of articles that data is returned
        self.assertIsNotNone(articles[0].headline)
        self.assertIsNotNone(articles[2].headline)
        self.assertIsNotNone(articles[5].headline)

        self.assertIsNotNone(articles[0].category)
        self.assertIsNotNone(articles[2].category)
        self.assertIsNotNone(articles[5].category)

        self.assertIsNotNone(articles[0].summary)
        self.assertIsNotNone(articles[2].summary)
        self.assertIsNotNone(articles[5].summary)
        
        self.assertIsNotNone(articles[0].id)
        self.assertIsNotNone(articles[2].id)
        self.assertIsNotNone(articles[5].id)
    
    def test_serialize_news(self):
        a = News.get_news()
        n = a[0]

        answer = {
            'category': n.category,
            'datetime': n.datetime,
            'headline': n.headline,
            'image': n.image,
            'related': n.related,
            'source': n.source,
            'summary': n.summary,
            'url': n.url,
        }

        self.assertEqual(n.serialize_news(), answer)

    def test_news_repr(self):
        """test news repr"""
        a = News.get_news()
        n = a[0]

        self.assertEqual(repr(a[0]), f'< News: id={n.id}, category={n.category}, datetime={n.datetime}, headline={n.headline}, image={n.image}, related={n.related}, source={n.source}, summary={n.summary}, url={n.url} >')