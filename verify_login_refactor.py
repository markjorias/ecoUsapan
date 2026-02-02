from flask import Flask, render_template
from webapp import create_app

app = create_app()
app.config['TESTING'] = True

with app.app_context():
    try:
        with app.test_client() as client:
            response = client.get('/login')
            print(f"Login Page Status: {response.status_code}")
            decoded = response.data.decode('utf-8')
            
            if "login-container" in decoded:
                print("Found login-container class.")
            else:
                print("Missing login-container class.")
                
            if "app-container" not in decoded:
                print("Successfully removed app-container class.")
            else:
                # app-container might still be there if base template is used? 
                # But login.html is standalone usually. Let's check.
                print("Warning: app-container still present (might be okay if intended, but goal was removal).")

            if "css/login.css" in decoded:
                print("Linked login.css found.")
            else:
                print("Missing login.css link.")
                
    except Exception as e:
        print(f"Error: {e}")
