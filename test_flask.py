from unittest import TestCase

from app import app
from models import db, User, Feedback

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Allow for form validation
app.config['WTF_CSRF_ENABLED'] = False

db.drop_all()
db.create_all()

class ViewsTestCase(TestCase):
    """Tests for routes"""

    def setUp(self):
        """Add sample users and feedback posts"""

        User.query.delete()
        Feedback.query.delete()

        test_user1 = User(first_name="Joe", last_name="Biden", email="joe.biden@test.com", username="joebiden", password="password123")
        test_user2 = User(first_name="George", last_name="Bush", email="george.bush@test.com", username="georgebush", password="123password")

        db.session.add(test_user1)
        db.session.add(test_user2)
        db.session.commit()

        test_feedback1 = Feedback(title="Test Title 1", content="Test content 1", username="joebiden")
        test_feedback2 = Feedback(title="Test Title 2", content="Test content 2", username="georgebush")

        db.session.add(test_feedback1)
        db.session.add(test_feedback2)
        db.session.commit()

        self.username = "joebiden"
        self.feedback_id = test_feedback1.id


    def TearDown(self):
        """Clean up any fouled transactions"""

        db.session.rollback()
        sess.pop("username")
    
    def test_homepage_not_logged_in(self):
        """Test homepage display when no user is logged in"""
        with app.test_client() as client:
            resp = client.get('/')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Recent Feedback", html)
            self.assertIn("Test Title 1", html)
            self.assertNotIn("Add Feedback", html)
    
    def test_homepage_logged_in(self):
        """Test homepage display when user (joebiden) us logged in"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess["username"] = 'joebiden'
            resp = client.get("/")
            html = resp.get_data(as_text=True)
                
            assert sess['username'] == "joebiden"
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Recent Feedback", html)
            self.assertIn("Test Title 1", html)
            self.assertIn('<a href="/users/joebiden/feedback/add">', html)
    
    def test_user_detail_page(self):
        """Test user detail page as logged-in user"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['username'] = 'joebiden'
            resp = client.get("/users/joebiden")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Details for joebiden", html)
            self.assertIn("Delete", html)
            self.assertIn("Test Title 1", html)
            self.assertNotIn("Test Title 2", html)

    def test_user_detail_page_other_user(self):
        """Test user detail page as a different logged-in user"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['username'] = 'georgebush'
            resp = client.get("/users/joebiden")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("Details for joebiden", html)
            self.assertNotIn("Delete", html)
            self.assertIn("Test Title 1", html)
            self.assertNotIn("Test Title 2", html)

    
    def test_non_user_logged_in(self):
        """Test user detail page if not real user, while logged-in"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['username'] = 'georgebush'
            resp = client.get("/users/testuser1")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 404)
    
    def test_non_user_not_logged_in(self):
        """Test user detail page if not real user while not logged-in"""
        with app.test_client() as client:
            resp = client.get("/users/testuser1")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)

    def test_new_feedback(self):
        """Test new feedback submission"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['username'] = 'georgebush'
            d = {"title": "Test Title 3", "content": "Test content 3."}
            resp = client.post("/users/georgebush/feedback/add", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Details for georgebush", html)
            self.assertIn("Test Title 3", html)
            self.assertIn("Test Title 2", html)
            self.assertNotIn("Test Title 1", html)

