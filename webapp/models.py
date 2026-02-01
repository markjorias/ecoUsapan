from . import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    
    # Updated Role Logic: 'User', 'Admin_LGU', 'Admin_DA', 'Admin_DENR'
    role = db.Column(db.String(50), default='User')
    
    initiatives = db.relationship('Initiative', backref='author', lazy=True)
    requests = db.relationship('ServiceRequest', backref='requester', lazy=True)

    @property
    def is_admin(self):
        return self.role in ['Admin_LGU', 'Admin_DA', 'Admin_DENR']

class Initiative(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    event_type = db.Column(db.String(50))
    date = db.Column(db.String(50))
    time = db.Column(db.String(50))
    province = db.Column(db.String(100))
    city = db.Column(db.String(100))
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    postal_code = db.Column(db.String(20))
    description = db.Column(db.Text)
    org_type = db.Column(db.String(50))
    org_name = db.Column(db.String(100))
    contact_fname = db.Column(db.String(50))
    contact_lname = db.Column(db.String(50))
    contact_role = db.Column(db.String(100))
    email = db.Column(db.String(120))
    event_link = db.Column(db.String(255))
    image_filename = db.Column(db.String(100), default='default_event.png')
    status = db.Column(db.String(50), default='Pending') 
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_name = db.Column(db.String(100))
    service_type = db.Column(db.String(50)) # 'Seed' or 'Seedling'
    status = db.Column(db.String(50), default='Pending')
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)

class Participation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    initiative_id = db.Column(db.Integer, db.ForeignKey('initiative.id'), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('participations', lazy=True))
    initiative = db.relationship('Initiative', backref=db.backref('participants', lazy=True))