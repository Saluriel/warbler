"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser_id = 1111
        self.testuser.id = self.testuser_id

        db.session.commit()
    
    def test_logged_out_add_message(self):
        """Test that the user is shown an unauthorized message when not logged in"""
        with app.test_client() as client:

            resp = client.get("/messages/new")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            # Shows access unauthorized when the user is not logged in
            self.assertIn('Access unauthorized.', html)

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 200)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")
    
    def test_message_invalid_user(self):
        """Can use add a message as an invalid user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 99222224

            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", html)
    
    def test_message_form(self):
        """Does the add message form show up?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/messages/new")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Add my message!', html)
    
    def test_show_message(self):
        """Does the correct message show up when you view it?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            new_message = Message(id = 1234, text = "This is a test message!", user_id = self.testuser.id, user = self.testuser)
            db.session.add(new_message)
            db.session.commit()

            resp = c.get("/messages/1234")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('This is a test message!', html)
    
    def test_delete_message_logged_in(self):
        """Can a user delete a message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            new_message = Message(id = 1234, text = "This is a test message!", user_id = self.testuser.id, user = self.testuser)
            db.session.add(new_message)
            db.session.commit()
            
            resp = c.post("/messages/1234/delete")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Message deleted", html)
    
    def test_delete_message_logged_out(self):

        new_message = Message(id = 1234, text = "This is a test message!", user_id = self.testuser.id, user = self.testuser)
        db.session.add(new_message)
        db.session.commit()

        with app.test_client() as client:
            
            resp = client.post("/messages/1234/delete")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)