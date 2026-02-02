from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import User
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('views.admin_dashboard'))
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            login_user(user, remember=True)
            if user.is_admin:
                return redirect(url_for('views.admin_dashboard'))
            return redirect(url_for('views.home'))
        else:
            flash('Account not found.', category='error')

    # FIX: We can no longer filter by 'is_admin' in SQL because it's a property.
    # We filter by 'role' instead to populate the login list.
    standard_users = User.query.filter_by(role='User').all()
    # Include Superadmin in the admins list
    admins = User.query.filter(User.role.in_(['Admin_LGU', 'Admin_DA', 'Admin_DENR', 'Superadmin'])).all()
    
    return render_template("login.html", user=current_user, users=standard_users, admins=admins)

@auth.route('/add-test-user')
def add_test_user():
    user_count = User.query.filter_by(role='User').count()
    new_index = user_count + 1
    
    new_username = f"Tester {new_index}"
    new_email = f"user{new_index}@ecousapan.com"
    
    if not User.query.filter_by(email=new_email).first():
        new_user = User(
            email=new_email,
            username=new_username,
            password=generate_password_hash('user', method='pbkdf2:sha256'),
            role='User'
        )
        db.session.add(new_user)
        db.session.commit()
    
    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))