from webapp import db, create_app
from webapp.models import User, Initiative, ServiceRequest, Participation, ForumPost, Comment, PostVote, InventoryItem
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def seed_all():
    app = create_app()
    with app.app_context():
        # 1. Reset Database
        print("Resetting database...")
        db.drop_all()
        db.create_all()

        # ========================
        # 2. CREATE USERS (6 total)
        # ========================
        print("Creating users...")
        users_data = [
            # Admins (4)
            {'email': 'superadmin@ecousapan.com', 'username': 'SuperAdmin', 'role': 'Superadmin', 'fname': 'Super', 'lname': 'Admin'},
            {'email': 'lgu@ecousapan.ph', 'username': 'LGU_Admin', 'role': 'Admin_LGU', 'fname': 'LGU', 'lname': 'Officer'},
            {'email': 'da@ecousapan.ph', 'username': 'DA_Admin', 'role': 'Admin_DA', 'fname': 'DA', 'lname': 'Officer'},
            {'email': 'denr@ecousapan.ph', 'username': 'DENR_Admin', 'role': 'Admin_DENR', 'fname': 'DENR', 'lname': 'Officer'},
            
            # Standard Users (2)
            {'email': 'tester@gmail.com', 'username': 'EcoTester', 'role': 'User', 'fname': 'Eco', 'lname': 'Tester'},
            {'email': 'juan@gmail.com', 'username': 'JuanDelaCruz', 'role': 'User', 'fname': 'Juan', 'lname': 'Dela Cruz'}
        ]
        
        users = {}
        for u in users_data:
            user = User(
                email=u['email'],
                username=u['username'],
                password=generate_password_hash('password123'),
                role=u['role'],
                first_name=u['fname'],
                last_name=u['lname']
            )
            db.session.add(user)
            # Store by role for admins, username for users
            if 'Admin' in u['role'] or u['role'] == 'Superadmin':
                users[u['role']] = user
            users[u['username']] = user
        db.session.commit()
        print(f"  Created {len(users_data)} users.")

        # ===========================
        # 3. CREATE INVENTORY ITEMS
        # ===========================
        print("Creating inventory items...")
        inventory_data = [
            # Seeds (for Admin_DA)
            {'name': 'Hybrid Rice Seeds', 'category': 'Seed', 'description': 'High-yield variety suitable for lowland areas.', 'stock_quantity': 500},
            {'name': 'Corn Kernels (Pioneer)', 'category': 'Seed', 'description': 'Drought-resistant corn seeds.', 'stock_quantity': 300},
            {'name': 'Mung Bean Seeds', 'category': 'Seed', 'description': 'Ideal for intercropping or as cover crop.', 'stock_quantity': 250},
            {'name': 'Peanut Seeds', 'category': 'Seed', 'description': 'Good for nitrogen fixation.', 'stock_quantity': 200},
            
            # Seedlings (for Admin_DENR)
            {'name': 'Narra Seedlings', 'category': 'Seedling', 'description': 'Philippine national tree, hardwood.', 'stock_quantity': 150},
            {'name': 'Mahogany Seedlings', 'category': 'Seedling', 'description': 'Fast-growing timber tree.', 'stock_quantity': 200},
            {'name': 'Mangium (Acacia)', 'category': 'Seedling', 'description': 'Excellent for reforestation projects.', 'stock_quantity': 300},
            {'name': 'Ilang-ilang', 'category': 'Seedling', 'description': 'Fragrant flowering tree.', 'stock_quantity': 100},
            {'name': 'Molave Seedlings', 'category': 'Seedling', 'description': 'Premium hardwood, slow-growing.', 'stock_quantity': 50}
        ]
        
        for item in inventory_data:
            inv = InventoryItem(
                name=item['name'],
                category=item['category'],
                description=item['description'],
                stock_quantity=item['stock_quantity'],
                image_filename='default_item.png'
            )
            db.session.add(inv)
        db.session.commit()
        print(f"  Created {len(inventory_data)} inventory items.")

        # =======================
        # 4. CREATE INITIATIVES
        # =======================
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
                status="Pending", 
                user_id=users['EcoTester'].id,
                image_filename="waste.png",
                date="2026-03-15",
                time="07:00"
            ),
            Initiative(
                title="Iriga Tree Planting",
                org_name="Green Iriga",
                description="Planting 500 narra seedlings at the foot of Mt. Iriga to restore biodiversity.",
                city="Iriga",
                province="Camarines Sur",
                contact_fname="Maria",
                contact_lname="Santos",
                contact_role="Coordinator",
                email="maria@iriga.ph",
                status="Approved", 
                user_id=users['EcoTester'].id,
                image_filename="tree-planting.png",
                date="2026-04-22",
                time="06:30"
            ),
            Initiative(
                title="Bicol Sustainability Workshop",
                org_name="EcoBicol",
                description="A seminar on sustainable living practices for households.",
                city="Naga",
                province="Camarines Sur",
                contact_fname="Pedro",
                contact_lname="Penduko",
                contact_role="Speaker",
                email="pedro@ecobicol.org",
                status="Approved", 
                user_id=users['JuanDelaCruz'].id,
                image_filename="default_event.png",
                date="2026-05-10",
                time="13:00"
            )
        ]
        db.session.add_all(initiatives)
        db.session.commit()
        print(f"  Created {len(initiatives)} initiatives.")

        # ===========================
        # 5. CREATE SERVICE REQUESTS
        # ===========================
        print("Creating service requests...")
        requests_data = [
            ServiceRequest(
                item_name="Hybrid Rice Seeds",
                quantity_requested=50,
                planting_site_desc="Barangay San Roque Farm Area",
                service_type="Seed",
                status="Pending",
                user_id=users['EcoTester'].id,
                date_requested=datetime.utcnow() - timedelta(days=3)
            ),
            ServiceRequest(
                item_name="Mahogany Seedlings",
                quantity_requested=100,
                planting_site_desc="Private Lot, Nabua",
                service_type="Seedling",
                status="Pending",
                user_id=users['JuanDelaCruz'].id,
                date_requested=datetime.utcnow() - timedelta(days=1)
            ),
            ServiceRequest(
                item_name="Narra Seedlings",
                quantity_requested=25,
                planting_site_desc="School backyard, Iriga City",
                service_type="Seedling",
                status="Approved",
                user_id=users['EcoTester'].id,
                date_requested=datetime.utcnow() - timedelta(days=7)
            )
        ]
        db.session.add_all(requests_data)
        db.session.commit()
        print(f"  Created {len(requests_data)} service requests.")

        # ======================
        # 6. CREATE FORUM POSTS
        # ======================
        print("Creating forum content...")
        posts = [
            ForumPost(
                title="Welcome to EcoUsapan!",
                content="This is the official discussion board for eco-conscious citizens in Bicol. Please follow our community guidelines.",
                category="News",
                votes=15,
                user_id=users['Admin_LGU'].id,
                date_posted=datetime.utcnow() - timedelta(days=5)
            ),
            ForumPost(
                title="How to dispose of electronics properly?",
                content="I have an old laptop and some batteries. Is there an accredited e-waste facility in CamSur?",
                category="Question",
                votes=5,
                user_id=users['EcoTester'].id,
                date_posted=datetime.utcnow() - timedelta(days=2)
            ),
            ForumPost(
                title="Organic Farming Tips",
                content="Sharing my experience with vermicomposting. It really improved my soil quality! Happy to answer questions.",
                category="Discussion",
                votes=8,
                user_id=users['JuanDelaCruz'].id,
                date_posted=datetime.utcnow() - timedelta(hours=12)
            ),
            ForumPost(
                title="Suggestion: Add a carbon footprint tracker",
                content="It would be great if the app could track our individual carbon footprint based on activities logged.",
                category="Suggestion",
                votes=12,
                user_id=users['JuanDelaCruz'].id,
                date_posted=datetime.utcnow() - timedelta(days=1)
            )
        ]
        db.session.add_all(posts)
        db.session.commit()
        print(f"  Created {len(posts)} forum posts.")

        # =========================
        # 7. CREATE PARTICIPATIONS
        # =========================
        print("Creating participations...")
        participations = [
            Participation(
                user_id=users['JuanDelaCruz'].id, 
                initiative_id=initiatives[1].id, # Iriga Tree Planting
                full_name="Juan Dela Cruz",
                address="San Felipe, Naga City",
                contact_number="09998887777",
                email="juan@gmail.com",
                purpose="Support reforestation."
            ),
            Participation(
                user_id=users['EcoTester'].id, 
                initiative_id=initiatives[2].id, # Workshop
                full_name="Eco Tester",
                address="Nabua, CamSur",
                contact_number="09123456789",
                email="tester@gmail.com",
                purpose="Learn about sustainability."
            )
        ]
        db.session.add_all(participations)
        db.session.commit()
        print(f"  Created {len(participations)} participation records.")

        # ================================
        # 8. CREATE COMMENTS AND VOTES
        # ================================
        print("Creating comments and votes...")
        
        # Votes
        votes = [
            PostVote(user_id=users['EcoTester'].id, post_id=posts[0].id, vote_type='up'),
            PostVote(user_id=users['JuanDelaCruz'].id, post_id=posts[0].id, vote_type='up'),
            PostVote(user_id=users['JuanDelaCruz'].id, post_id=posts[1].id, vote_type='up'),
            PostVote(user_id=users['EcoTester'].id, post_id=posts[2].id, vote_type='up'),
            PostVote(user_id=users['Admin_LGU'].id, post_id=posts[3].id, vote_type='up'),
        ]
        db.session.add_all(votes)

        # Comments
        comments = [
            Comment(
                content="Looking forward to more updates!",
                user_id=users['EcoTester'].id,
                post_id=posts[0].id,
                date_posted=datetime.utcnow() - timedelta(days=4)
            ),
            Comment(
                content="Great initiative from the LGU.",
                user_id=users['JuanDelaCruz'].id,
                post_id=posts[0].id,
                date_posted=datetime.utcnow() - timedelta(days=3)
            ),
            Comment(
                content="Try checking with the City Environment Office in Naga. They accept e-waste.",
                user_id=users['Admin_DENR'].id,
                post_id=posts[1].id,
                date_posted=datetime.utcnow() - timedelta(days=1)
            ),
            Comment(
                content="Thanks! I'll check it out.",
                user_id=users['EcoTester'].id,
                post_id=posts[1].id,
                parent_id=3, # Reply to DENR's comment
                date_posted=datetime.utcnow() - timedelta(hours=20)
            ),
            Comment(
                content="How long did it take for you to see results with the vermicompost?",
                user_id=users['EcoTester'].id,
                post_id=posts[2].id,
                date_posted=datetime.utcnow() - timedelta(hours=6)
            )
        ]
        db.session.add_all(comments)
        db.session.commit()
        print(f"  Created {len(votes)} votes and {len(comments)} comments.")

        # =====================
        # SUMMARY
        # =====================
        print("\n" + "=" * 50)
        print("SUCCESS: Database seeded successfully!")
        print("=" * 50)
        print("\nACCOUNTS CREATED:")
        for u in users_data:
            print(f"  [{u['role']:12}] {u['email']} / password123")
        print("\nTABLES SEEDED:")
        print(f"  - Users: {len(users_data)}")
        print(f"  - Inventory Items: {len(inventory_data)}")
        print(f"  - Initiatives: {len(initiatives)}")
        print(f"  - Service Requests: {len(requests_data)}")
        print(f"  - Forum Posts: {len(posts)}")
        print(f"  - Participations: {len(participations)}")
        print(f"  - Votes: {len(votes)}")
        print(f"  - Comments: {len(comments)}")
        print("=" * 50)

if __name__ == "__main__":
    seed_all()