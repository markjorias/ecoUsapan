from webapp import create_app, db
from webapp.models import User, Initiative, ServiceRequest, InventoryItem
from werkzeug.security import generate_password_hash
from datetime import datetime

def seed_database():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        print("Seeding Users...")
        # Admins
        lgu = User(email='admin@ecousapan.com', username='admin', password=generate_password_hash('admin', method='pbkdf2:sha256'), role='Admin_LGU')
        da = User(email='da@ecousapan.com', username='da_seeds', password=generate_password_hash('admin123', method='pbkdf2:sha256'), role='Admin_DA')
        denr = User(email='denr@ecousapan.com', username='denr_seedlings', password=generate_password_hash('admin123', method='pbkdf2:sha256'), role='Admin_DENR')
        
        # User
        user = User(email='user@ecousapan.com', username='tester', password=generate_password_hash('user', method='pbkdf2:sha256'), role='User')
        
        db.session.add_all([lgu, da, denr, user])
        
        print("Seeding Inventory...")
        # Seeds for DA
        s1 = InventoryItem(name="Pechay Seeds", category="Seed", stock_quantity=500, description="Easy to grow leafy vegetable.")
        s2 = InventoryItem(name="Tomato Seeds", category="Seed", stock_quantity=300, description="Cherry tomato variety.")
        
        # Seedlings for DENR
        t1 = InventoryItem(name="Narra Seedling", category="Seedling", stock_quantity=50, description="National tree of the Philippines.")
        t2 = InventoryItem(name="Mahogany Seedling", category="Seedling", stock_quantity=100, description="Fast-growing timber tree.")
        
        db.session.add_all([s1, s2, t1, t2])
        db.session.commit()
        print("Database populated successfully!")

if __name__ == "__main__":
    seed_database()