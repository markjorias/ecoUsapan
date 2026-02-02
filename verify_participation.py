import unittest
from webapp import create_app, db
from webapp.models import User, Initiative
from flask_login import current_user

class TestParticipationRestrictions(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        
        # Ensure context for tests
        self.setup_data()

    def tearDown(self):
        self.ctx.pop()

    def setup_data(self):
        # Create Users
        self.admin = User.query.filter_by(role='Admin_LGU').first()
        self.creator = User.query.filter_by(role='User').first() # Assuming this is 'tester'
        
        # Create another user for valid participation
        self.other_user = User.query.filter_by(email='other@test.com').first()
        if not self.other_user:
            self.other_user = User(email='other@test.com', username='OtherUser', password='pw', role='User')
            db.session.add(self.other_user)
            db.session.commit()
            
        # Create Initiative by creator
        self.initiative = Initiative(
            title="Restriction Test Event",
            user_id=self.creator.id,
            description="Testing restrictions",
            status="Approved"
        )
        db.session.add(self.initiative)
        db.session.commit()
        self.init_id = self.initiative.id

    def login(self, user):
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True

    def test_admin_cannot_join(self):
        self.login(self.admin)
        response = self.client.post(f'/participate/{self.init_id}', json={
            'full_name': 'Admin User', 'address': 'LGU', 'contact': '123', 'email': 'admin@test.com', 'purpose': 'check'
        })
        print(f"Admin Join attempt status: {response.status_code}")
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Admins cannot participate', response.data)

    def test_creator_cannot_join_own_event(self):
        self.login(self.creator)
        response = self.client.post(f'/participate/{self.init_id}', json={
            'full_name': 'Creator', 'address': 'Home', 'contact': '123', 'email': self.creator.email, 'purpose': 'check'
        })
        print(f"Creator Join attempt status: {response.status_code}")
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'You cannot join your own initiative', response.data)

if __name__ == '__main__':
    unittest.main()
