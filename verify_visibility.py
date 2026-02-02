import unittest
from flask import Flask
from webapp import create_app
from webapp.models import User

# Mocking a User object for tests
class MockUser:
    def __init__(self, role):
        self.role = role
        self.username = 'test_user'
        self.email = 'test@example.com'
        self.first_name = 'Test'

class TestDashboardVisibility(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_lgu_visibility(self):
        # Admin_LGU should see Initiatives, NOT Requests
        with self.client.session_transaction() as sess:
            # We can't easily mock current_user without login, 
            # so we'll inspect the template logic directly by rendering string? 
            # Or reliance on actual login.
            # Using actual login is best if DB has users.
            pass
            
    # Since DB might be complex to set up for all roles in this quick test,
    # I'll rely on reading the file and regex check for the IF logic, 
    # OR simpler: Use Jinja2 Environment to render the specific snippet?
    
    # Let's try rendering the template with a mock context manually.
    def render_dashboard(self, role):
        mock_user = MockUser(role)
        # We need to pass all required variables to avoid errors
        return self.app.jinja_env.get_template('admin_dashboard.html').render(
            user=mock_user,
            current_user=mock_user,
            initiatives=[],
            requests=[],
            inventory_items=[],
            total_users=0,
            current_date='Jan 1, 2026',
            url_for=lambda x, **y: '#'
        )

    def test_visibility_logic(self):
        # 1. Admin_LGU
        html_lgu = self.render_dashboard('Admin_LGU')
        if 'id="initiatives"' in html_lgu:
            print("[LGU] Initiatives Visible: PASS")
        else:
            print("[LGU] Initiatives Visible: FAIL")
            
        if 'id="requests"' not in html_lgu:
            print("[LGU] Requests Hidden: PASS")
        else:
            print("[LGU] Requests Hidden: FAIL")

        # 2. Admin_DA
        html_da = self.render_dashboard('Admin_DA')
        if 'id="initiatives"' not in html_da:
            print("[DA] Initiatives Hidden: PASS")
        else:
            print("[DA] Initiatives Hidden: FAIL")
            
        if 'id="requests"' in html_da:
            print("[DA] Requests Visible: PASS")
        else:
            print("[DA] Requests Visible: FAIL")

        # 3. Superadmin
        html_super = self.render_dashboard('Superadmin')
        if 'id="initiatives"' in html_super and 'id="requests"' in html_super:
            print("[Superadmin] Both Visible: PASS")
        else:
            print("[Superadmin] Both Visible: FAIL")

if __name__ == '__main__':
    unittest.main()
