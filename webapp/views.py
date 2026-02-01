from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_required, current_user
from .models import Initiative, ServiceRequest, Participation
from . import db
from datetime import datetime

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    # Fetch approved initiatives to display on the home feed
    initiatives = Initiative.query.filter_by(status='Approved').order_by(Initiative.date_created.desc()).all()
    return render_template('home.html', initiatives=initiatives, user=current_user)

@views.route('/events')
@login_required
def events():
    """
    FIX: This route was missing, causing the BuildError in home.html.
    It displays the full list of available environmental initiatives.
    """
    initiatives = Initiative.query.filter_by(status='Approved').order_by(Initiative.date_created.desc()).all()
    return render_template('home.html', initiatives=initiatives, user=current_user)

@views.route('/status')
@login_required
def status():
    # Multi-admin Role-Based Access Control (RBAC) filtering
    if current_user.role == 'Admin_LGU':
        # LGU oversees all initiatives and requests
        initiatives = Initiative.query.all()
        requests = ServiceRequest.query.all()
        participations = Participation.query.all()
        is_admin_view = True
        view_title = "LGU Management"
    elif current_user.role == 'Admin_DA':
        # Department of Agriculture handles Seed requests
        initiatives = [] 
        requests = ServiceRequest.query.filter_by(service_type='Seed').all()
        participations = []
        is_admin_view = True
        view_title = "DA Seed Management"
    elif current_user.role == 'Admin_DENR':
        # DENR handles Seedling/Tree requests
        initiatives = []
        requests = ServiceRequest.query.filter_by(service_type='Seedling').all()
        participations = []
        is_admin_view = True
        view_title = "DENR Seedling Management"
    else:
        # Standard User view: see only their own data
        initiatives = Initiative.query.filter_by(user_id=current_user.id).all()
        requests = ServiceRequest.query.filter_by(user_id=current_user.id).all()
        participations = Participation.query.filter_by(user_id=current_user.id).all()
        is_admin_view = False
        view_title = "My Status"

    return render_template('status.html', 
                           initiatives=initiatives, 
                           requests=requests,
                           participations=participations,
                           user=current_user,
                           is_admin_view=is_admin_view,
                           view_title=view_title)

# --- Service & Inventory Routes ---

@views.route('/ecoservices')
@login_required
def ecoservices():
    return render_template('ecoservices.html')

@views.route('/about-seeds')
@login_required
def about_ecoservice_seeds():
    return render_template('about-ecoservice-seeds.html')

@views.route('/about-seedlings')
@login_required
def about_ecoservice_seedlings():
    return render_template('about-ecoservice-seedlings.html')

@views.route('/seed-inventory')
@login_required
def seed_inventory():
    return render_template('seed_inventory.html')

@views.route('/seedling-inventory')
@login_required
def tree_seedlings_inventory():
    return render_template('tree_seedlings_inventory.html')

@views.route('/request-seeds-form')
@login_required
def request_seeds_form():
    return render_template('request-seeds-form.html')

@views.route('/request-seedlings-form')
@login_required
def request_seedlings_form():
    return render_template('request-seedlings-form.html')

# --- Initiative Launch Routes (Multi-step) ---

@views.route('/launch-initiative-1', methods=['GET', 'POST'])
@login_required
def launch_initiative1():
    if request.method == 'POST':
        session['init_part1'] = {
            'title': request.form.get('title'),
            'event_type': request.form.get('event_type'),
            'date': request.form.get('date'),
            'time': request.form.get('time'),
            'province': request.form.get('province'),
            'city': request.form.get('city'),
            'address_line1': request.form.get('address_line1'),
            'address_line2': request.form.get('address_line2'),
            'postal_code': request.form.get('postal_code'),
            'description': request.form.get('description')
        }
        return redirect(url_for('views.launch_initiative2'))
    return render_template('launch_initiative1.html', user=current_user)

@views.route('/launch-initiative-2', methods=['GET', 'POST'])
@login_required
def launch_initiative2():
    if request.method == 'POST':
        part1 = session.get('init_part1', {})
        new_initiative = Initiative(
            user_id=current_user.id,
            title=part1.get('title'),
            event_type=part1.get('event_type'),
            date=part1.get('date'),
            time=part1.get('time'),
            province=part1.get('province'),
            city=part1.get('city'),
            address_line1=part1.get('address_line1'),
            address_line2=part1.get('address_line2'),
            postal_code=part1.get('postal_code'),
            description=part1.get('description'),
            org_type=request.form.get('org_type'),
            org_name=request.form.get('org_name'),
            contact_fname=request.form.get('fname'),
            contact_lname=request.form.get('lname'),
            contact_role=request.form.get('role'),
            email=request.form.get('email'),
            event_link=request.form.get('link'),
            status='Pending'
        )
        db.session.add(new_initiative)
        db.session.commit()
        session.pop('init_part1', None)
        flash('Initiative submitted for approval!', category='success')
        return redirect(url_for('views.status'))
    return render_template('launch_initiative2.html', user=current_user)

# --- Admin Controls ---

@views.route('/approve-initiative/<int:id>')
@login_required
def approve_initiative(id):
    if current_user.role != 'Admin_LGU':
        flash('Unauthorized.', category='error')
        return redirect(url_for('views.home'))
    
    initiative = Initiative.query.get_or_404(id)
    initiative.status = 'Approved'
    db.session.commit()
    flash('Initiative Approved!', category='success')
    return redirect(url_for('views.status'))

# --- Auxiliary Page Routes ---

@views.route('/event-view')
@login_required
def event_view():
    return render_template('event-view.html')

@views.route('/forum')
@login_required
def forum():
    return render_template('forum.html')

@views.route('/forum-view')
@login_required
def forum_view():
    return render_template('forum-view.html')

@views.route('/seeds-view')
@login_required
def seeds_view():
    return render_template('seeds-view.html')

@views.route('/seedlings-view')
@login_required
def seedlings_view():
    return render_template('seedlings-view.html')

@views.route('/event-map')
@login_required
def event_map():
    return render_template('event-map.html')