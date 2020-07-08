"""model test"""

from app import app
import os
from unittest import TestCase
from models import db

from sqlalchemy import exc

from models import User

# use testing DB
os.environ['DATABASE_URL'] = "postgresql:///stock-tracker-test"
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# disable csrf checks
app.config['WTF_CSRF_ENABLED'] = False

# drop all tables & create new ones
db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """test user models"""

    def setUp(self):
        """create test client, add sample data"""

        User.query.delete()

        u = User.signup("testUser", "testUser@gmail.com",
                        "password", "USA", "CA")
        u.id = 9876

        db.session.add(u)
        db.session.commit()
        self.u = u

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """test base user model"""

        user = User.query.get(self.u.id)
        self.assertEqual(self.u.username, user.username)

    def test_missing_username_signup(self):
        """test missign username"""

        with self.assertRaises(TypeError):
            invalid_user = User.signup(
                email="testUser@gmail.com", password="password", country="USA", state="CA")

    def test_duplicate_username_signup(self):
        """test duplicate username"""

        invalid_user = User.signup(
            "testUser", "newEmail@gmail.com", "password", "USA", "CA")
        with self.assertRaises(exc.IntegrityError):
            db.session.add(invalid_user)
            db.session.commit()

    def test_duplicate_email_signup(self):
        """test duplicate email"""

        invalid_user = User.signup(
            "newUser", "testUser@gmail.com", "password", "USA", "CA")
        with self.assertRaises(exc.IntegrityError):
            db.session.add(invalid_user)
            db.session.commit()

    def test_user_repr(self):
        """test user repr"""

        self.assertEqual(
            repr(self.u), f'< User: id={self.u.id}, username={self.u.username}, email={self.u.email}, password=HIDDEN, country={self.u.country}, state={self.u.state} >')

    def test_user_check_password(self):
        """test user class method check_password"""

        self.assertFalse(User.check_password(self.u.username, "wrongPW"))
        self.assertEqual(User.check_password(
            self.u.username, 'password'), User.query.get(self.u.id))

    def test_user_update_password(self):
        """test user class method update_password"""

        self.assertFalse(User.update_password(
            User.query.get(self.u.id), "password", "pw"))
        self.assertEqual(User.update_password(User.query.get(
            self.u.id), "updatepw", "updatepw"), User.query.get(self.u.id))
