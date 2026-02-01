from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_required, current_user
from .models import Initiative, ServiceRequest, Participation
from . import db
import os
from werkzeug.utils import secure_filename
from flask import current_app

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    # Only show initiatives that have been approved by an admin
    initiatives = Initiative.query.filter_by(status='Approved').order_by(Initiative.date_created.desc()).all()
    return render_template('home.html', initiatives=initiatives, user=current_user)

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
        
        image_file = request.files.get('event_image')
        filename = 'default_event.png'
        if image_file:
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join(current_app.static_folder, 'images', 'userupload')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            image_file.save(os.path.join(upload_folder, filename))
        
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
            image_filename=filename,
            status='Pending' # Explicitly set to Pending for the workflow
        )
        
        db.session.add(new_initiative)
        db.session.commit()
        session.pop('init_part1', None)
        return redirect(url_for('views.status')) # Redirect to status so they see it's pending
        
    return render_template('launch_initiative2.html', user=current_user)


@views.route('/request-item/<string:item_type>/<string:item_name>')
@login_required
def request_item(item_type, item_name):
    new_req = ServiceRequest(user_id=current_user.id, item_name=item_name, service_type=item_type)
    db.session.add(new_req)
    db.session.commit()
    return redirect(url_for('views.status'))

@views.route('/approve-initiative/<int:id>')
@login_required
def approve_initiative(id):
    if not current_user.is_admin:
        return redirect(url_for('views.home'))
    
    initiative = Initiative.query.get_or_404(id)
    initiative.status = 'Approved'
    db.session.commit()
    return redirect(url_for('views.status'))

@views.route('/participate/<int:event_id>')
@login_required
def participate(event_id):
    # Check if already joined
    existing = Participation.query.filter_by(user_id=current_user.id, initiative_id=event_id).first()
    if not existing:
        new_part = Participation(user_id=current_user.id, initiative_id=event_id)
        db.session.add(new_part)
        db.session.commit()
    return redirect(url_for('views.status'))

@views.route('/request-seeds')
@login_required
def request_seeds():
    return render_template('request_seeds.html')

@views.route('/request-seedlings')
@login_required
def request_seedlings():
    return render_template('request_seedlings.html')

@views.route('/events')
@login_required
def events():
    return render_template('events.html')

@views.route('/forum')
@login_required
def forum():
    return render_template('forum.html')

@views.route('/event-view')
@login_required
def event_view():
    return render_template('event-view.html')

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

@views.route('/status')
@login_required
def status():
    if current_user.is_admin:
        initiatives = Initiative.query.all()
        requests = ServiceRequest.query.all()
        # Admin sees all participations as "Global Participations"
        participations = Participation.query.all()
        is_admin_view = True
    else:
        initiatives = Initiative.query.filter_by(user_id=current_user.id).all()
        requests = ServiceRequest.query.filter_by(user_id=current_user.id).all()
        # User sees events they joined
        participations = Participation.query.filter_by(user_id=current_user.id).all()
        is_admin_view = False

    return render_template('status.html', 
                           initiatives=initiatives, 
                           requests=requests,
                           participations=participations, # Pass this to the restored section
                           user=current_user,
                           is_admin_view=is_admin_view)

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

@views.route('/submit-request/<string:item_name>/<string:service_type>')
@login_required
def submit_request(item_name, service_type):
    new_req = ServiceRequest(
        user_id=current_user.id, 
        item_name=item_name, 
        service_type=service_type,
        status='Pending'
    )
    db.session.add(new_req)
    db.session.commit()
    flash('Request submitted!', category='success')
    return redirect(url_for('views.status'))
