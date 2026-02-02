import unittest
from flask import Flask, url_for
from webapp import create_app
from webapp.models import ForumPost
import re

class TestForumRefinements(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def test_dashboard_html_contains_filter(self):
        with open('webapp/templates/admin_dashboard.html', 'r') as f:
            content = f.read()
            
        if 'id="dbFilterBtn"' in content and 'id="dbFilterDropdown"' in content:
            print("Dashboard Filter HTML: PASS")
        else:
            print("Dashboard Filter HTML: FAIL")
            
        if 'selectFilter' in content:
            print("Dashboard Filter JS: PASS")
        else:
            print("Dashboard Filter JS: FAIL")

    def test_partial_html_delete_position(self):
        with open('webapp/templates/components/forum_post_partials.html', 'r') as f:
            content = f.read()
            
        # Check if form has source=dashboard
        if "source='dashboard'" in content or 'source=dashboard' in content:
            print("Partial Delete Link Source: PASS")
        else:
            print("Partial Delete Link Source: FAIL")

if __name__ == '__main__':
    unittest.main()
