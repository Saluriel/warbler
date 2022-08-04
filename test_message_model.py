import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()

class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u1 = User.signup("test", "test1@email.com", "password", None)
        u1_id = 1111
        u1.id = u1_id
        
        db.session.commit()

        u1 = User.query.get(u1_id)
        self.u1=u1
        self.u1_id = u1_id

        self.client = app.test_client()
    
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        """Does the basic model work?"""

        m = Message(text="Test", user_id=self.u1_id, user=self.u1)

        db.session.add(m)
        db.session.commit()

        self.assertEqual(m.text, "Test")
        self.assertEqual(m.user, self.u1)
    
    def test__no_user_likes(self):
        """Does it show if a user has no likes?"""

        self.assertEqual(len(self.u1.likes), 0)

    def test_user_likes(self):

        m = Message(text = "Text", user = self.u1, user_id=self.u1_id)
        db.session.add(m)
        db.session.commit()

        new_like = Likes(user_id=self.u1_id, message_id=m.id)
        db.session.add(new_like)
        db.session.commit()

        self.assertEqual(len(self.u1.likes), 1)