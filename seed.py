from webapp import create_app, db
from webapp.models import User, Initiative, ServiceRequest, Participation
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def seed_database():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        print("Creating Multi-Admin test accounts...")
        # 1. LGU Admin (General Management)
        lgu_admin = User(
            email='lgu@ecousapan.com',
            username='lgu_admin',
            password=generate_password_hash('admin123', method='pbkdf2:sha256'),
            role='Admin_LGU'
        )
        
        # 2. DA Admin (Seeds Management)
        da_admin = User(
            email='da@ecousapan.com',
            username='da_seeds_officer',
            password=generate_password_hash('admin123', method='pbkdf2:sha256'),
            role='Admin_DA'
        )

        # 3. DENR Admin (Seedlings Management)
        denr_admin = User(
            email='denr@ecousapan.com',
            username='denr_forester',
            password=generate_password_hash('admin123', method='pbkdf2:sha256'),
            role='Admin_DENR'
        )
        
        # Standard User
        user1 = User(
            email='user1@ecousapan.com',
            username='EcoWarrior99',
            password=generate_password_hash('user123', method='pbkdf2:sha256'),
            role='User'
        )
        
        db.session.add_all([lgu_admin, da_admin, denr_admin, user1])
        db.session.commit()

        print("Creating test data...")
        init1 = Initiative(
            user_id=user1.id,
            title="Magsaysay Coastal Cleanup",
            event_type="Cleanup Drive",
            status="Pending", 
            city="Naga City",
            date_created=datetime.utcnow()
        )
        
        req_seed = ServiceRequest(
            user_id=user1.id,
            item_name="Pechay Seeds",
            service_type="Seed",
            status="Pending"
        )
        
        req_tree = ServiceRequest(
            user_id=user1.id,
            item_name="Narra Seedlings",
            service_type="Seedling",
            status="Pending"
        )

        db.session.add_all([init1, req_seed, req_tree])
        db.session.commit()
        
        print("Database re-seeded with roles successfully!")

if __name__ == "__main__":
    seed_database()