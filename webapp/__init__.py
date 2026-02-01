from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secretngani'
    
    root_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    instance_path = os.path.join(root_path, 'instance')
    
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_path, 'site.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    with app.app_context():
        db.create_all()
        
        # FIX: Changed 'is_admin=True' to 'role='Admin_LGU'' 
        # because is_admin is now a read-only property.
        if not User.query.filter_by(email='admin@ecousapan.com').first():
            admin = User(
                email='admin@ecousapan.com', 
                username='admin', 
                password=generate_password_hash('admin', method='pbkdf2:sha256'),
                role='Admin_LGU'
            )
            db.session.add(admin)
            
        if not User.query.filter_by(email='user@ecousapan.com').first():
            user = User(
                email='user@ecousapan.com', 
                username='tester', 
                password=generate_password_hash('user', method='pbkdf2:sha256'),
                role='User'
            )
            db.session.add(user)
            
        db.session.commit()
    
    return app