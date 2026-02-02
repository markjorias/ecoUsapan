## **Key Features**

* **Dynamic Forum**: Engage in community discussions with real-time search, category filtering (News, Questions, Suggestions, etc.), and a robust Upvote/Downvote system.  
* **Environmental Initiatives**: Users can propose cleanup drives or tree-planting events. Admins (LGU) can review, approve, or decline these proposals.  
* **Service Requests**: Streamlined access to government services such as requesting rice seeds (DA) or mahogany seedlings (DENR).  
* **Participation Tracking**: A personal dashboard for users to track the status of their service requests and registered events.  
* **Role-Based Access**: Dedicated administrative dashboards for LGU, DA, and DENR officials to manage approvals and community data.

## **Technology Stack**

* **Backend**: Python, Flask  
* **Database**: SQLite with SQLAlchemy ORM  
* **Frontend**: HTML5, CSS3 (Mobile-first design), JavaScript (ES6+)  
* **Authentication**: Flask-Login

## **Installation & Setup**

Follow these steps to get the project running on your local machine:

1. **Clone the Repository**  
   git clone \[https://github.com/yourusername/ecoUsapan.git\](https://github.com/yourusername/ecoUsapan.git)  
   cd ecoUsapan

2. **Create a Virtual Environment**  
   python \-m venv venv  
   \# Windows:  
   venv\\Scripts\\activate  
   \# Mac/Linux:  
   source venv/bin/activate

3. **Install Dependencies**  
   pip install \-r requirements.txt

4. **Initialize the Database**  
   Instead of manually creating tables, use the provided system seeder to set up the schema and test data:  
   python seed.py

5. **Run the Application**  
   python main.py

   Access the app at http://127.0.0.1:5000

## **Testing with Seed Data**

The seed.py script automatically resets the database and creates the following test accounts (Password: password123):

* **Standard User**: tester@gmail.com  
* **LGU Admin**: lgu@ecousapan.ph  
* **DA Admin**: da@ecousapan.ph  
* **DENR Admin**: denr@ecousapan.ph

Shift+L to logout

## **Project Structure**

* webapp/: Main application package.  
  * auth.py: Authentication logic (Login/Signup).  
  * views.py: Main application routes and logic.  
  * models.py: Database schemas.  
  * templates/: Jinja2 HTML templates.  
  * static/: CSS, JS, and UI icons.  
* main.py: Entry point for the Flask server.  
* seed.py: Comprehensive database initialization script.
