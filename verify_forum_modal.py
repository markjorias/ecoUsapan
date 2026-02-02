import unittest
from flask import Flask
from webapp import create_app
from webapp.models import ForumPost, User, db

class TestForumModal(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        
        # Ensure a test user and post exist
        self.user = User.query.filter_by(email='superadmin@ecousapan.com').first()
        if not self.user:
            # Create dummy if needed (should exist from seed)
            pass 
            
        self.post = ForumPost.query.first()

    def test_partial_route(self):
        if not self.post:
            print("SKIPPING: No posts found to test.")
            return

        # Login
        with self.client:
            self.client.post('/login', data={'email': 'superadmin@ecousapan.com', 'password': 'password123'})
            
            # Request partial
            resp = self.client.get(f'/forum-post-partial/{self.post.id}')
            
            if resp.status_code == 200:
                print("Route /forum-post-partial/ID: PASS (200 OK)")
                html = resp.get_data(as_text=True)
                if 'forum-details-content' in html and 'forum-main-title' in html:
                    print("Partial Content Structure: PASS")
                else:
                    print(f"Partial Content Structure: FAIL. Got: {html[:100]}...")
            else:
                print(f"Route /forum-post-partial/ID: FAIL ({resp.status_code})")

    def test_dashboard_file(self):
        with open('webapp/templates/admin_dashboard.html', 'r') as f:
            content = f.read()
            
        if 'id="forumDetailsModal"' in content:
            print("Modal Container in HTML: PASS")
        else:
            print("Modal Container in HTML: FAIL")
            
        if 'function openForumPost(id)' in content:
            print("JS Function (openForumPost): PASS")
        else:
            print("JS Function (openForumPost): FAIL")

if __name__ == '__main__':
    unittest.main()
