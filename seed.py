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
        # 1.5 SETUP IMAGES
        # ========================
        print("Setting up images...")
        import shutil
        import os
        
        # Define paths
        base_dir = os.path.abspath(os.path.dirname(__file__))
        static_dir = os.path.join(base_dir, 'webapp', 'static')
        uploads_dir = os.path.join(static_dir, 'uploads')
        images_dir = os.path.join(static_dir, 'images')
        
        # Create uploads directory if it doesn't exist
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Source directories to look for images
        source_dirs = [
            os.path.join(images_dir, 'inventory-seeds-mock'),
            os.path.join(images_dir, 'inventory-seedlings-mock'),
            os.path.join(images_dir, 'events-initiative-mock'),
            os.path.join(images_dir, 'forum-mock', 'news-mock')
        ]
        
        copied_count = 0
        for source_dir in source_dirs:
            if os.path.exists(source_dir):
                for filename in os.listdir(source_dir):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        src_path = os.path.join(source_dir, filename)
                        dst_path = os.path.join(uploads_dir, filename)
                        shutil.copy2(src_path, dst_path)
                        copied_count += 1
        
        print(f"  Copied {copied_count} images to uploads directory.")

        # ========================
        # 2. CREATE USERS
        # ========================
        print("Creating users...")
        users_data = [
            # Admins
            {'email': 'superadmin@ecousapan.com', 'username': 'SuperAdmin', 'role': 'Superadmin', 'fname': 'Super', 'lname': 'Admin'},
            {'email': 'lgu@ecousapan.ph', 'username': 'Admin_LGU', 'role': 'Admin_LGU', 'fname': 'LGU', 'lname': 'Officer'}, # Renamed from LGU_Admin to Admin_LGU
            {'email': 'da@ecousapan.ph', 'username': 'DA_Admin', 'role': 'Admin_DA', 'fname': 'DA', 'lname': 'Officer'},
            {'email': 'denr@ecousapan.ph', 'username': 'DENR_Admin', 'role': 'Admin_DENR', 'fname': 'DENR', 'lname': 'Officer'},
            
            # Standard Users (Original)
            {'email': 'tester@gmail.com', 'username': 'EcoTester', 'role': 'User', 'fname': 'Eco', 'lname': 'Tester'},
            {'email': 'juan@gmail.com', 'username': 'JuanDelaCruz', 'role': 'User', 'fname': 'Juan', 'lname': 'Dela Cruz'},

            # Standard Users (Mock Data)
            {'email': 'inecar@adnu.edu.ph', 'username': 'inecar_adnu', 'role': 'User', 'fname': 'INECAR', 'lname': 'AdNU'},
            {'email': 'cityenro@naga.gov.ph', 'username': 'city_enro_naga', 'role': 'User', 'fname': 'City', 'lname': 'ENRO'},
            {'email': 'agri@naga.gov.ph', 'username': 'naga_city_agri', 'role': 'User', 'fname': 'Naga City', 'lname': 'Agriculture'},
            {'email': 'sanfelipe@youth.com', 'username': 'sanfelipe_youth', 'role': 'User', 'fname': 'San Felipe', 'lname': 'Youth'},
            {'email': 'jpcs@cspc.edu.ph', 'username': 'jpcs_cspc', 'role': 'User', 'fname': 'JPCS', 'lname': 'CSPC'},
            {'email': 'guardian@bicolriver.com', 'username': 'BicolRiverGuardian', 'role': 'User', 'fname': 'River', 'lname': 'Guardian'},
            {'email': 'nagayouth@council.com', 'username': 'NagaYouthCouncil', 'role': 'User', 'fname': 'Naga', 'lname': 'Youth Council'},
            {'email': 'green@naga.com', 'username': 'GreenNagaVolunteers', 'role': 'User', 'fname': 'Green', 'lname': 'Naga'},
            {'email': 'concerned@triangulo.com', 'username': 'ConcernedCitizen_Tri', 'role': 'User', 'fname': 'Concerned', 'lname': 'Citizen'},
            {'email': 'carolina@planter.com', 'username': 'Carolina_Planter', 'role': 'User', 'fname': 'Carolina', 'lname': 'Planter'},
            {'email': 'concepcion@resident.com', 'username': 'ConcepcionResident22', 'role': 'User', 'fname': 'Concepcion', 'lname': 'Resident'},
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
            # Seeds
            {'name': 'Pechay', 'category': 'Seed', 'description': 'Leafy vegetable rich in vitamins.', 'stock_quantity': 1000, 
             'image_filename': 'Pechay.png'},
            {'name': 'Eggplant', 'category': 'Seed', 'description': 'Common vegetable used in many dishes.', 'stock_quantity': 1000, 
             'image_filename': 'Eggplant.png'},
            {'name': 'Ampalaya', 'category': 'Seed', 'description': 'Bitter gourd, healthy and nutritious.', 'stock_quantity': 1000, 
             'image_filename': 'Ampalaya.png'},
            {'name': 'Saluyot', 'category': 'Seed', 'description': 'Leafy vegetable, easy to grow.', 'stock_quantity': 1000, 
             'image_filename': 'Saluyot.png'},
            {'name': 'Okra', 'category': 'Seed', 'description': 'Lady finger, good source of fiber.', 'stock_quantity': 1000, 
             'image_filename': 'Okra.png'},
            
            # Seedlings
            {'name': 'Narra', 'category': 'Seedling', 'description': 'Philippine national tree, hardwood.', 'stock_quantity': 1000, 
             'image_filename': 'Narra.png'},
            {'name': 'Mahogany', 'category': 'Seedling', 'description': 'Fast-growing timber tree.', 'stock_quantity': 1000, 
             'image_filename': 'mahogany.jpg'},
            {'name': 'Kamagong', 'category': 'Seedling', 'description': 'Iron wood tree, indigenous.', 'stock_quantity': 1000, 
             'image_filename': 'Kamagong.png'},
            {'name': 'Molave', 'category': 'Seedling', 'description': 'Premium hardwood, durable.', 'stock_quantity': 1000, 
             'image_filename': 'Molave.png'},
            {'name': 'Acacia', 'category': 'Seedling', 'description': 'Large shade tree.', 'stock_quantity': 1000, 
             'image_filename': 'Acacia.png'},
            {'name': 'Guyabano', 'category': 'Seedling', 'description': 'Fruit bearing tree.', 'stock_quantity': 1000, 
             'image_filename': 'Guyabano.png'}
        ]
        
        for item in inventory_data:
            inv = InventoryItem(
                name=item['name'],
                category=item['category'],
                description=item['description'],
                stock_quantity=item['stock_quantity'],
                image_filename=item['image_filename']
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
                title="Isarog Foothill Reforestation",
                org_name="INECAR - AdNU",
                description="A collaborative tree planting effort at the base of Mt. Isarog to restore native tree species and protect the watershed.",
                city="Naga City",
                province="Camarines Sur",
                address_line1="Zone 6, Brgy. Panicuason",
                contact_fname="INECAR",
                contact_lname="AdNU",
                contact_role="Organizer",
                email="inecar@adnu.edu.ph",
                status="Approved",
                user_id=users['inecar_adnu'].id,
                date="2026-03-15",
                time="06:30",
                event_type="Tree Planting",
                latitude=13.6628,
                longitude=123.3183,
                image_filename="Isarog Foothill Reforestation.jpeg"
            ),
            Initiative(
                title="Naga River Cleanup Drive",
                org_name="City ENRO Naga",
                description="A community-led cleanup focusing on removing plastic waste from the Naga River to improve water quality and urban health.",
                city="Naga City",
                province="Camarines Sur",
                address_line1="Brgy. Sabang Riverbanks",
                contact_fname="City",
                contact_lname="ENRO",
                contact_role="Organizer",
                email="cityenro@naga.gov.ph",
                status="Approved",
                user_id=users['city_enro_naga'].id,
                date="2026-04-18",
                time="07:00",
                event_type="Coastal Cleanup",
                latitude=13.6197,
                longitude=123.1814,
                image_filename="Naga_River_Cleanup_Drive.jpg"
            ),
            Initiative(
                title="Urban Gardening Seminar",
                org_name="Naga City Agriculture Office",
                description="A workshop teaching modernized urban agriculture techniques to transform local spaces into productive community gardens.",
                city="Naga City",
                province="Camarines Sur",
                address_line1="Brgy. Balatas Multipurpose Hall",
                contact_fname="Naga City",
                contact_lname="Agri",
                contact_role="Organizer",
                email="agri@naga.gov.ph",
                status="Approved",
                user_id=users['naga_city_agri'].id,
                date="2026-05-09",
                time="13:30", # 01:30 PM
                event_type="Seminar / Workshop",
                latitude=13.6304,
                longitude=123.2010,
                image_filename="Urban_Gardening_Seminar.jpg"
            ),
            Initiative(
                title="Ecopark Community Plot",
                org_name="San Felipe Youth Council",
                description="Establishing a shared vegetable garden within the Ecology Park to promote food security and sustainable local farming.",
                city="Naga City",
                province="Camarines Sur",
                address_line1="Naga City Ecology Park, Brgy. San Felipe",
                contact_fname="San Felipe",
                contact_lname="Youth",
                contact_role="Organizer",
                email="sanfelipe@youth.com",
                status="Approved",
                user_id=users['sanfelipe_youth'].id,
                date="2026-06-20",
                time="08:00",
                event_type="Community Garden",
                latitude=13.6415,
                longitude=123.2041,
                image_filename="Ecopark_Community_Plot.jpg"
            ),
            Initiative(
                title="Eco-Walk & Awareness",
                org_name="Junior Philippine Computer Society (JPCS)",
                description="An awareness walk through downtown Naga to promote digital sustainability and environmental consciousness among tech students.",
                city="Naga City",
                province="Camarines Sur",
                address_line1="Plaza Rizal, Brgy. San Francisco",
                contact_fname="JPCS",
                contact_lname="CSPC",
                contact_role="Organizer",
                email="jpcs@cspc.edu.ph",
                status="Approved",
                user_id=users['jpcs_cspc'].id,
                date="2026-07-11",
                time="16:00", # 04:00 PM
                event_type="Other",
                latitude=13.6235,
                longitude=123.1850,
                image_filename="Eco-Walk_Awareness.jpg"
            )
        ]
        db.session.add_all(initiatives)
        db.session.commit()
        print(f"  Created {len(initiatives)} initiatives.")

        # ======================
        # 6. CREATE FORUM POSTS
        # ======================
        print("Creating forum content...")
        posts = [
            # News
            ForumPost(
                title="LiDAR & UP NOAH Validation",
                content="Is your street truly safe from the next typhoon?\n\nFollowing the 2025 flood validation activity by the UP Resilience Institute, residents are discussing the new centimeter-precision maps. The community is debating whether this data will finally lead to better drainage in high-risk zones like San Felipe and Cararayan, or if it’s just another set of maps while the pipes stay small.",
                category="News",
                votes=100,
                user_id=users['Admin_LGU'].id,
                date_posted=datetime.utcnow() - timedelta(days=2),
                image_filename="LiDAR_UP_NOAH_Validation.png"
            ),
            ForumPost(
                title="The 2025 Water Shortage",
                content="When will the flow return to our taps?\n\nAfter Mayor Leni Robredo’s recent forum with the Metropolitan Naga Water District (MNWD), users are reacting to the news of three new well-drilling projects. The debate centers on why water pressure remains low in urban sitios and whether the city should prioritize Rainwater Harvesting over drawing more from the depleting groundwater.",
                category="News",
                votes=34,
                user_id=users['Admin_LGU'].id,
                date_posted=datetime.utcnow() - timedelta(days=1),
                image_filename="The_2025_Water_Shortage.png"
            ),
            ForumPost(
                title="Beating the 27.3°C Average",
                content="Can \"Greening Education\" cool down Naga?\n\nWith scientific projections showing Naga’s average temperature hitting a record 27.3°C this year, this thread explores urban heat mitigation. Residents are sharing tips on community gardening and questioning if the city’s plan for \"pocket parks\" and roadside tree-planting is moving fast enough to counter the \"concrete heat\" in the CBD.",
                category="News",
                votes=12,
                user_id=users['Admin_LGU'].id,
                date_posted=datetime.utcnow() - timedelta(hours=10),
                image_filename="Beating_the_27.3C_Average.png"
            ),
            ForumPost(
                title="Naga’s \"AI City Planner\"",
                content="Will technology solve our urban sprawl?\n\nThis thread covers the ₱6.7M grant Naga recently won to develop the Philippines' first AI-powered City Planner. Citizens are brainstorming how this AI should prioritize land use—specifically, whether it should prevent new subdivisions from building over natural floodplains and \"lost\" creeks that the city is currently trying to \"heal.\"",
                category="News",
                votes=18,
                user_id=users['Admin_LGU'].id,
                date_posted=datetime.utcnow() - timedelta(hours=2),
                image_filename="Nagas_AI_City_Planner.png"
            ),

            # Discussion
            ForumPost(
                title="Bayanihan sa Naga River",
                content="Sino ang sasama sa Cleanup Drive sa Sabado?\n\nMainit na pinag-uusapan sa \"Events\" tab ang gaganaping malawakang paglilinis sa Naga River. Nagtatanong ang mga users kung magbibigay ba ang LGU ng bota at gloves, habang ang iba naman ay nag-oorganize na ng mga grupo para sa kanilang barangay para makasali sa pakontes ng \"Most Productive Volunteer Group\" sa app.",
                category="Discussion",
                votes=5,
                user_id=users['BicolRiverGuardian'].id,
                date_posted=datetime.utcnow() - timedelta(days=3)
            ),
            ForumPost(
                title="Eco-Bricks Workshop sa Jesse M. Robredo Museum: May slots pa ba?",
                content="Maraming kabataan ang interesadong sumali sa workshop kung paano gagawing eco-bricks ang mga non-recyclable plastics. Nagtatanong ang mga users kung kailangan bang magdala ng sariling plastic bottles at kung saan pwedeng i-donate ang mga matatapos na eco-bricks para magamit sa mga \"green park\" projects ng lungsod.",
                category="Discussion",
                votes=3,
                user_id=users['NagaYouthCouncil'].id,
                date_posted=datetime.utcnow() - timedelta(days=1)
            ),
            ForumPost(
                title="San Alfonso 'Forest-in-Our-Midst' Maintenance: Volunteer-needs for Saturday",
                content="Matapos ang malawakang tree planting, kailangan naman ng mga volunteers para sa pag-aalis ng damo (weeding) at paglalagay ng mulch sa mga bagong tanim na puno sa San Alfonso. Nag-uusap ang mga users tungkol sa carpooling at kung anong oras ang pinakamainam pumunta para hindi masyadong mainit ang sikat ng araw.",
                category="Discussion",
                votes=2,
                user_id=users['GreenNagaVolunteers'].id,
                date_posted=datetime.utcnow() - timedelta(hours=5)
            ),

            # Suggestion
            ForumPost(
                title="Dapat bulan-bulan an paglinig kan mga kanal sa Brgy. Triangulo",
                content="Aram tana na madali bahaon an Triangulo. An sugestyon ko iyo na imbes na halaton pa an bagyo, dapat magkaigwa nin regular na declogging o paglinig kan mga kanal tanganing dai magpundo an tubig uran asin dai maglangkaw an baha sa tinampo.",
                category="Suggestion",
                votes=10,
                user_id=users['ConcernedCitizen_Tri'].id,
                date_posted=datetime.utcnow() - timedelta(days=2)
            ),
            ForumPost(
                title="Magtanom kita nin dugang na mga kahoy sa gilid dalan kan Brgy. Carolina",
                content="Mantang an Carolina an saro sa pinakamalipot na parte kan Naga, marhay na mantiniron ta ini paagi sa pagtatanom nin mga kahoy (arog kan Pili o Narra). Makakatabang ini para dai magka-landslide asin magdanay na presko an duros sa satuyang barangay.",
                category="Suggestion",
                votes=5,
                user_id=users['Carolina_Planter'].id,
                date_posted=datetime.utcnow() - timedelta(days=1)
            ),
            ForumPost(
                title="Sana magkaigwa nin saktong oras an pagkolekta kan basura sa Brgy. Concepcion Pequeña",
                content="Dakul an nagrereklamo na minsan naiiwan an mga basura kaya pigkakalkal kan mga ayam. Kun igwa nin saktong schedule na aram kan gabos na residente, iluluwas sana an basura kun harani na an truck tanganing magdanay na malinig an satuyang mga kalsada.",
                category="Suggestion",
                votes=3,
                user_id=users['ConcepcionResident22'].id,
                date_posted=datetime.utcnow() - timedelta(hours=12)
            )
        ]
        # Fix for last item timedelta syntax
        posts[-1].date_posted = datetime.utcnow() - timedelta(hours=12) # Manual fix because I messed up the line above

        db.session.add_all(posts)
        db.session.commit()
        print(f"  Created {len(posts)} forum posts.")

        # =========================
        # 5. CREATE PARTICIPATIONS (Generic)
        # =========================
        print("Creating participations...")
        participations = [
            Participation(
                user_id=users['JuanDelaCruz'].id, 
                initiative_id=initiatives[0].id, # Isarog
                full_name="Juan Dela Cruz",
                address="San Felipe, Naga City",
                contact_number="09998887777",
                email="juan@gmail.com",
                purpose="Support reforestation."
            ),
            Participation(
                user_id=users['EcoTester'].id, 
                initiative_id=initiatives[1].id, # Cleanup
                full_name="Eco Tester",
                address="Nabua, CamSur",
                contact_number="09123456789",
                email="tester@gmail.com",
                purpose="Community service."
            )
        ]
        db.session.add_all(participations)
        db.session.commit()
        print(f"  Created {len(participations)} participation records.")

        # =====================
        # SUMMARY
        # =====================
        print("\n" + "=" * 50)
        print("SUCCESS: Database seeded successfully!")
        print("=" * 50)
        print("\nACCOUNTS CREATED:")
        for u in users_data:
            print(f"  [{u['role']:12}] {u['username']} ({u['email']}) / password123")
        print("\nTABLES SEEDED:")
        print(f"  - Users: {len(users_data)}")
        print(f"  - Inventory Items: {len(inventory_data)}")
        print(f"  - Initiatives: {len(initiatives)}")
        print(f"  - Forum Posts: {len(posts)}")
        print(f"  - Participations: {len(participations)}")
        print("=" * 50)

if __name__ == "__main__":
    seed_all()