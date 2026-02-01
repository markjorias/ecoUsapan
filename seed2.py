from webapp import db, create_app
from webapp.models import User, Initiative, ServiceRequest, Participation, ForumPost, Comment, PostVote
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def seed_all():
    app = create_app()
    with app.app_context():
        # 1. Reset Database (Warning: This deletes existing data for a clean test)
        print("Resetting database...")
        db.drop_all()
        db.create_all()

        # 2. Create Users (One for each role)
        print("Creating users...")
        users_data = [
            {'email': 'lgu@ecousapan.ph', 'username': 'aaLGU', 'role': 'Admin_LGU'},
            {'email': 'da@ecousapan.ph', 'username': 'AgricultureDept', 'role': 'Admin_DA'},
            {'email': 'denr@ecousapan.ph', 'username': 'EnvironmentDept', 'role': 'Admin_DENR'},
            {'email': 'tester@gmail.com', 'username': 'EcoTester', 'role': 'Standard'}
        ]
        
        users = {}
        for u in users_data:
            user = User(
                email=u['email'],
                username=u['username'],
                password=generate_password_hash('password123'),
                role=u['role']
            )
            db.session.add(user)
            users[u['role']] = user
        
        db.session.commit()

        # 3. Create Initiatives
        print("Creating initiatives...")
        initiatives = [
            Initiative(
                title="Nabua River Cleanup 2026",
                org_name="LGU Nabua Youth",
                description="A massive cleanup drive to protect our local waterways. Volunteers will be provided with gloves and refreshments.",
                city="Nabua",
                province="Camarines Sur",
                contact_fname="John",
                contact_lname="Doe",
                contact_role="Youth Leader",
                email="john@nabua.gov.ph",
                status="Pending", # Ready for LGU Admin to Approve
                user_id=users['Standard'].id,
                image_filename="default_event.png"
            ),
            Initiative(
                title="Iriga Tree Planting",
                org_name="Green Iriga",
                description="Planting 500 narra seedlings at the foot of Mt. Iriga.",
                city="Iriga",
                province="Camarines Sur",
                contact_fname="Maria",
                contact_lname="Santos",
                contact_role="Coordinator",
                email="maria@iriga.ph",
                status="Approved", # Already published
                user_id=users['Standard'].id,
                image_filename="default_event.png"
            )
        ]
        db.session.add_all(initiatives)
        db.session.commit()

        # 4. Create Service Requests
        print("Creating service requests...")
        requests = [
            ServiceRequest(
                item_name="Hybrid Rice Seeds",
                quantity_requested=50,
                planting_site_desc="Barangay San Roque Farm Area",
                service_type="Seed",
                status="Pending", # For Admin_DA
                user_id=users['Standard'].id
            ),
            ServiceRequest(
                item_name="Mahogany Seedlings",
                quantity_requested=100,
                planting_site_desc="Private Lot, Nabua",
                service_type="Seedling",
                status="Pending", # For Admin_DENR
                user_id=users['Standard'].id
            )
        ]
        db.session.add_all(requests)
        db.session.commit()

        # 5. Create Forum Posts
        print("Creating forum content...")
        posts = [
            ForumPost(
                title="Welcome to EcoUsapan!",
                content="This is the official discussion board for eco-conscious citizens in Bicol.",
                category="News",
                votes=10,
                user_id=users['Admin_LGU'].id
            ),
            ForumPost(
                title="How to dispose of electronics?",
                content="I have an old laptop. Is there an e-waste facility in CamSur?",
                category="Question",
                votes=5,
                user_id=users['Standard'].id
            )
        ]
        db.session.add_all(posts)
        db.session.commit()

        # 6. Create Interactions (Votes, Comments, Participation)
        print("Creating interactions...")
        
        # User registers for the approved initiative with required NOT NULL fields
        reg = Participation(
            user_id=users['Standard'].id, 
            initiative_id=initiatives[1].id,
            full_name="Eco Tester",
            address="123 Eco Street, Nabua, Camarines Sur",
            contact_number="09123456789",
            email="tester@gmail.com",
            purpose="I want to contribute to the reforestation of Mt. Iriga."
        )
        db.session.add(reg)

        # User upvotes the news post
        vote = PostVote(user_id=users['Standard'].id, post_id=posts[0].id, vote_type='up')
        db.session.add(vote)

        # User comments on the news post
        comm = Comment(
            content="Great to see this platform live!",
            user_id=users['Standard'].id,
            post_id=posts[0].id
        )
        db.session.add(comm)

        db.session.commit()
        print("\nSUCCESS: System seeded successfully!")
        print("-" * 30)
        print("Standard User: tester@gmail.com / password123")
        print("LGU Admin: lgu@ecousapan.ph / password123")
        print("DA Admin: da@ecousapan.ph / password123")
        print("DENR Admin: denr@ecousapan.ph / password123")
        print("-" * 30)

if __name__ == "__main__":
    seed_all()