"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u1 = User.signup("test", "test1@email.com", "password", None)
        u1_id = 1111
        u1.id = u1_id

        u2 = User.signup("test2", "test2@email.com", "password", None)
        u2_id = 2222
        u2.id = u2_id
        
        db.session.commit()

        u1 = User.query.get(u1_id)
        self.u1=u1
        self.u1_id = u1_id

        u2 = User.query.get(u2_id)
        self.u2 = u2
        self.u2_id = u2_id

        self.client = app.test_client()
    
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    # ************
    # Following Tests
    # ************
    
    def test_user_is_following(self):
        """Does is_following successfully detect when user1 is following user2"""
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u1.following), 1)

    def test_user_is_not_following(self):
        """Does is_following successfully detect when user1 is not following user2"""
        self.assertEqual(len(self.u2.followers), 0)
        self.assertEqual(len(self.u1.followers), 0)

        self.assertEqual(len(self.u1.following), 0)
        self.assertEqual(len(self.u2.following), 0)
    
    def test_is_followed_by(self):
        self.u2.following.append(self.u1)
        db.session.commit()

        self.assertTrue(self.u1.is_followed_by(self.u2))
        self.assertFalse(self.u2.is_followed_by(self.u1))

     # ************
    # Signup Tests
    # ************

    def test_create_user(self):
        """Does User.signup successfully create a new user given valid credentials?"""

        u3 = User.signup("test3", "test3@email.com", "password", None)
        u3_id = 3333
        u3.id = u3_id
        db.session.commit()

        test = User.query.get(u3_id)
        self.assertEqual(test.username, "test3")
        self.assertEqual(test.id, 3333)
        self.assertEqual(test.email, "test3@email.com")
        self.assertNotEqual(test.password, "password")

    def test_create_duplicate_user(self):
        """Does User.signup fail to create a new user if the unique validator fails"""

        u3 = User.signup("test", "test1@email.com", "password", None)
        with self.assertRaises(exc.IntegrityError):
            db.session.commit()
        
    
    def test_create_null_user(self):
        """Does User.signup fail to create a new user if the password field is unfilled"""
        
        with self.assertRaises(ValueError):
            u3 = User.signup("test", "test1@email.com", "", None)
        
        with self.assertRaises(ValueError):
            u3 = User.signup("test", "test1@email.com", None, None)

    def test_authenticate_user(self):
        """Tests that User.authenticate will return the user when given the username and password"""
        authentic = User.authenticate("test2", "password")

        self.assertEqual(authentic, self.u2)
    
    def test_authenticate_username_fail(self):
        """User.authenticate returns false when given the wrong username"""
        not_authentic = User.authenticate("test3", "password")

        self.assertEqual(not_authentic, False)
    
    def test_authenticate_password_fail(self):
        """User.authenticate returns false when given the wrong password"""
        not_authentic = User.authenticate("test2", "wrongpassword")

        self.assertEqual(not_authentic, False)
