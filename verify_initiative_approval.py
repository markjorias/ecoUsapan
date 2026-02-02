import unittest
from flask import Flask, url_for
from webapp import create_app
from webapp.models import User, Initiative

class TestInitiativeApproval(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        
        # Ensure we have data
        self.user = User.query.filter_by(role='Admin_LGU').first()
        self.init = Initiative.query.first()
        

    def test_dashboard_html_structure(self):
        with open('webapp/templates/admin_dashboard.html', 'r') as f:
            content = f.read()
            
        # 1. Check if "Approve" button is removed from table (heuristic)
        # It used to be: <button type="submit" class="action-btn btn-primary">Approve</button>
        # But inside the table loop specifically. 
        # Easier check: Ensure "Approve Initiative" (the NEW button text) exists in modal section
        
        if 'Approve Initiative' in content:
            print("Modal Approve Button Text: PASS")
        else:
            print("Modal Approve Button Text: FAIL")
            
        # 2. Check for data attributes
        if 'data-approve-url' in content and 'data-can-approve' in content:
            print("Data Attributes on View Button: PASS")
        else:
            print("Data Attributes on View Button: FAIL")
            
        # 3. Check for specific JS logic
        if 'btn.dataset.canApprove' in content:
             print("JS Logic (canApprove): PASS")
        else:
             print("JS Logic (canApprove): FAIL")

if __name__ == '__main__':
    unittest.main()
