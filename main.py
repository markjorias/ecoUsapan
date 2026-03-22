import os
from webapp import create_app

app = create_app()

if os.environ.get('VERCEL') == '1':
    with app.app_context():
        from webapp.models import User
        try:
            if not User.query.first():
                from seed import seed_all
                print("Seeding database for Vercel...")
                seed_all()
        except Exception as e:
            print(f"Error during Vercel DB check: {e}")

if __name__ == '__main__':
    app.run(debug=True)