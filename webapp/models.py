from . import db
from flask_login import UserMixin
from datetime import datetime
import os
from flask import url_for, current_app

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    role = db.Column(db.String(50), default='User') # 'User', 'Admin_LGU', 'Admin_DA', 'Admin_DENR'
    
    initiatives = db.relationship('Initiative', backref='author', lazy=True)
    requests = db.relationship('ServiceRequest', backref='requester', lazy=True)

    @property
    def is_admin(self):
        return self.role in ['Admin_LGU', 'Admin_DA', 'Admin_DENR', 'Superadmin']

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False) # 'Seed' or 'Seedling'
    description = db.Column(db.Text)
    stock_quantity = db.Column(db.Integer, default=0)
    image_filename = db.Column(db.String(100), default='default_item.png')
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

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

    def get_time_left(self):
        try:
            # HTML date input usually gives YYYY-MM-DD
            # HTML time input usually gives HH:MM (24-hour)
            event_datetime = datetime.strptime(f"{self.date} {self.time}", "%Y-%m-%d %H:%M")
            now = datetime.now() # Using local time to match user input
            delta = event_datetime - now

            if delta.total_seconds() <= 0:
                return "Completed"
            
            if delta.days > 0:
                return f"{delta.days} Day{'s' if delta.days > 1 else ''} Left"
            
            hours = int(delta.total_seconds() // 3600)
            if hours > 0:
                return f"{hours} Hour{'s' if hours > 1 else ''} Left"
            
            return "Starting Soon"
        except (ValueError, TypeError):
            return "Time TBA"
    @property
    def image_url(self):
        # Check if the filename exists and is not the default placeholder
        if self.image_filename and self.image_filename != 'default_event.png':
            # Construct the absolute path to check if the file actually exists on the server
            file_path = os.path.join(current_app.root_path, 'static', 'uploads', self.image_filename)
            if os.path.exists(file_path):
                return url_for('static', filename='uploads/' + self.image_filename)
        
        # Fallback to a default image in your static/images folder
        return url_for('static', filename='images/sample-image1.png')

    @property
    def contact_full_name(self):
        return f"{self.contact_fname} {self.contact_lname}"

    @property
    def has_custom_image(self):
        """Check if the initiative has a custom uploaded image (not the default)."""
        if self.image_filename and self.image_filename != 'default_event.png':
            file_path = os.path.join(current_app.root_path, 'static', 'uploads', self.image_filename)
            return os.path.exists(file_path)
        return False

class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_name = db.Column(db.String(100))
    service_type = db.Column(db.String(50)) # 'Seed' or 'Seedling'
    status = db.Column(db.String(50), default='Pending')
    date_requested = db.Column(db.DateTime, default=datetime.utcnow)
    # Additional fields for the 4-step form
    quantity_requested = db.Column(db.Integer)
    planting_site_desc = db.Column(db.Text)
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)
    image_filename = db.Column(db.String(100))

class Participation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    initiative_id = db.Column(db.Integer, db.ForeignKey('initiative.id'), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    # New fields to match the participation modal
    full_name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    purpose = db.Column(db.Text, nullable=False)
    # Relationship to easily access event data
    initiative = db.relationship('Initiative', backref='participants')
    initiative = db.relationship('Initiative', backref='registrations')

class PostVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_post.id'), nullable=False)
    # THIS IS THE MISSING COLUMN
    vote_type = db.Column(db.String(10), nullable=False) # 'up' or 'down'

class ForumPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='Discussion')
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    votes = db.Column(db.Integer, default=0)
    
    # ADD THESE TWO LINES:
    image_filename = db.Column(db.String(150))
    author = db.relationship('User', backref='posts')
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")
    votes_associated = db.relationship('PostVote', backref='post', lazy=True, cascade="all, delete-orphan")

    def get_user_vote(self, user_id):
        vote = PostVote.query.filter_by(user_id=user_id, post_id=self.id).first()
        return vote.vote_type if vote else None

    # Added this earlier for the vote visual logic
    def has_user_voted(self, user_id):
        vote = PostVote.query.filter_by(user_id=user_id, post_id=self.id).first()
        return vote is not None


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_post.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id')) # For nested replies

    # Relationships
    author = db.relationship('User', backref='user_comments')
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy=True)