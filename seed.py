from webapp import create_app, db
from webapp.models import User, Initiative, ServiceRequest, Participation
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def seed_database():
    app = create_app()
    with app.app_context():
        # 1. Clear existing data
        # Warning: This will delete everything in the DB for a clean start
        db.drop_all()
        db.create_all()
        
        print("Creating test accounts...")
        # 2. Create Admin
        admin = User(
            email='admin@ecousapan.com',
            username='admin_tester',
            password=generate_password_hash('admin123', method='pbkdf2:sha256'),
            is_admin=True
        )
        
        # 3. Create Standard Users
        user1 = User(
            email='user1@ecousapan.com',
            username='EcoWarrior99',
            password=generate_password_hash('user123', method='pbkdf2:sha256'),
            is_admin=False
        )
        
        user2 = User(
            email='user2@ecousapan.com',
            username='NagaPlanter',
            password=generate_password_hash('user123', method='pbkdf2:sha256'),
            is_admin=False
        )
        
        db.session.add_all([admin, user1, user2])
        db.session.commit()

        print("Creating initiatives...")
        # 4. Create Initiatives
        init1 = Initiative(
            user_id=user1.id,
            title="Magsaysay Coastal Cleanup",
            event_type="Cleanup Drive",
            date="2023-11-15",
            time="08:00",
            province="Camarines Sur",
            city="Naga City",
            address_line1="Magsaysay Ave",
            description="A community cleanup drive along the coastal area.",
            org_name="Naga Youth Volunteers",
            org_type="Community Group",
            status="Approved", 
            date_created=datetime.utcnow() - timedelta(days=5)
        )
        
        init2 = Initiative(
            user_id=user1.id,
            title="Backyard Composting Seminar",
            event_type="Environment Education",
            date="2023-12-01",
            time="14:00",
            province="Camarines Sur",
            city="Canaman",
            address_line1="Barangay Hall",
            description="Learning how to compost at home effectively.",
            org_name="Canaman Green Team",
            org_type="LGU",
            status="Pending", 
            date_created=datetime.utcnow() - timedelta(days=1)
        )

        init3 = Initiative(
            user_id=user2.id,
            title="Narra Reforestation",
            event_type="Tree Planting",
            date="2023-11-20",
            time="06:00",
            province="Camarines Sur",
            city="Naga City",
            address_line1="Mt. Isarog Foot",
            description="Planting 100 Narra seedlings to restore the forest cover.",
            org_name="Mount Isarog Guardians",
            org_type="NGO",
            status="Approved",
            date_created=datetime.utcnow() - timedelta(days=10)
        )

        db.session.add_all([init1, init2, init3])
        db.session.commit() # Commit to get IDs for participation
        
        print("Creating participation records...")
        # 5. User 1 joins User 2's reforestation event
        part1 = Participation(
            user_id=user1.id,
            initiative_id=init3.id,
            date_joined=datetime.utcnow()
        )
        db.session.add(part1)
        
        print("Creating service requests...")
        # 6. Create Service Requests
        req1 = ServiceRequest(
            user_id=user1.id,
            item_name="Ampalaya Seeds",
            service_type="Seed",
            status="Ready for Pickup",
            date_submitted=datetime.utcnow() - timedelta(days=3)
        )
        
        req2 = ServiceRequest(
            user_id=user1.id,
            item_name="Narra Seedlings",
            service_type="Seedling",
            status="Pending",
            date_submitted=datetime.utcnow() - timedelta(hours=5)
        )

        db.session.add_all([req1, req2])
        db.session.commit()
        
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()