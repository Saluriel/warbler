import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):

    def setUp(self):
        """Create test client, add sample data"""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser_id = 1111
        self.testuser.id = self.testuser_id

        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="password",
                                    image_url=None)

        self.testuser_id2 = 2222
        self.testuser2.id = self.testuser_id2

        db.session.commit()
    
    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_show_signup(self):
        """Signup page loads correctly"""

        with app.test_client() as c:

            resp = c.get('/signup')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Join Warbler today.', html)

    def test_signup(self):
        """A new user is able to sign up"""

        with app.test_client() as c:

            resp = c.post('/signup', data={"username": "Test1", "email":"Testemail@email.com", "password":"password"})
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Test1", html)
    
    def test_duplicate_username(self):
        """Duplicate usernames cannot be used"""

        with app.test_client() as c:

            resp = c.post('/signup', data={"username": "testuser", "email":"Testemail@email.com", "password":"password"})
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Username already taken", html)
    
    def test_show_login(self):
        """Shows the login page"""

        with app.test_client() as c:

            resp = c.get('/login')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Log in', html)
    
    def test_login(self):
        """Test logging in a user"""

        with app.test_client() as c:

            resp = c.get('/login', data={"username": "testuser", "password":"testuser"})
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser', html)
        
    def test_invalid_username_login(self):
        """Tests an invalid username"""

        with app.test_client() as c:

            resp = c.get('/login', data={"username": "fakeusername", "password":"testuser"})
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Log in', html)
            self.assertIn('Password', html)
    
    def test_invalid_password_login(self):
        """Tests an invalid password"""

        with app.test_client() as c:

            resp = c.get('/login', data={"username": "testuser", "password":"wrongpassword"})
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Log in', html)
            self.assertIn('Password', html)
    
    def test_users_list(self):
        """Tests that the test user shows up in the user list and you can see it when logged in"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get("/users")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser", html)
        
    def test_user_profile(self):
        """Tests that the user profile shows up"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get("/users/1111")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser", html)
    
    def test_users_following_logged_in(self):
        """Shows a list of users the person is following if logged in"""
        self.testuser.following.append(self.testuser2)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get("/users/1111/following")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser2', html)
    
    def test_users_following_logged_out(self):
        """Does not show the following page if logged out"""
        with app.test_client() as c:
            resp = c.get('/users/1111/following', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', html)
    
    def test_users_followers_logged_in(self):
        """Shows the users following another user if logged in"""
        self.testuser.following.append(self.testuser2)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get("/users/2222/followers")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser', html)
    
    def test_users_followers_logged_out(self):
        """Does not show the followers page if logged out"""
        with app.test_client() as c:
            resp = c.get('/users/2222/following', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', html)

    def test_follow_user(self):
        """Tests following a user"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.post("/users/follow/2222")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser', html)
    
    def test_stop_following_user(self):
        """Tests unfollowing a user"""
        self.testuser.following.append(self.testuser2)
        self.testuser2.following.append(self.testuser)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.post("/users/stop-following/2222")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('testuser2', html)
    
    def show_update_form_logged_in(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get("/users/profile")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('New header image url', html)
    
    def test_user_profile_not_loggedin(self):
        with app.test_client() as c:
            resp = c.get('/users/profile', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', html)

    def test_user_likes(self):
        msg = Message(id=1234, text="Testtext", user=self.testuser2)
        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.post("/users/add_like/1234")
            html = resp.get_data(as_text=True)

            likes = Likes.query.filter(Likes.message_id==1234).all()

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(likes), 1)




    



















