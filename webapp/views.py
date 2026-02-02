from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify
from flask_login import login_required, current_user
from .models import User, Initiative, ServiceRequest, Participation, InventoryItem, Comment, ForumPost, PostVote
from . import db
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import uuid

views = Blueprint('views', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@views.route('/')
@login_required
def home():
    initiatives = Initiative.query.filter_by(status='Approved').order_by(Initiative.date_created.desc()).limit(5).all()
    return render_template('home.html', initiatives=initiatives, user=current_user)

@views.route('/events')
@login_required
def events():
    # Fetch all approved initiatives to show in the dedicated list
    initiatives = Initiative.query.filter_by(status='Approved').order_by(Initiative.date_created.desc()).all()
    # Change 'home.html' to 'events.html'
    return render_template('events.html', initiatives=initiatives, user=current_user)

@views.route('/status')
@login_required
def status():
    if current_user.is_admin:
        initiatives = Initiative.query.order_by(Initiative.date_created.desc()).all()
        # Admin still sees their own joined events here
        participations = Participation.query.filter_by(user_id=current_user.id).all()
        requests = ServiceRequest.query.all()
    else:
        initiatives = Initiative.query.filter_by(user_id=current_user.id).order_by(Initiative.date_created.desc()).all()
        participations = Participation.query.filter_by(user_id=current_user.id).all()
        requests = ServiceRequest.query.filter_by(user_id=current_user.id).all()

    return render_template('status.html', user=current_user, initiatives=initiatives, requests=requests, participations=participations)

@views.route('/admin-dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied. Admins only.', category='error')
        return redirect(url_for('views.home'))
    
    # Fetch data for dashboard
    initiatives = Initiative.query.order_by(Initiative.date_created.desc()).all()
    requests = ServiceRequest.query.order_by(ServiceRequest.date_requested.desc()).all()
    total_users = User.query.count()
    
    current_date = datetime.now().strftime('%B %d, %Y')
    
    # Fetch inventory for management
    if current_user.role == 'Admin_DA':
        inventory_items = InventoryItem.query.filter_by(category='Seed').all()
    elif current_user.role == 'Admin_DENR':
        inventory_items = InventoryItem.query.filter_by(category='Seedling').all()
    else: # Superadmin or LGU (sees all)
        inventory_items = InventoryItem.query.all()
    
    
    # Fetch Forum Data for Dashboard
    # Trending: Top 5 by votes
    trending_posts = ForumPost.query.order_by(ForumPost.votes.desc()).limit(5).all()
    # Recent: All ordered by date
    recent_posts = ForumPost.query.order_by(ForumPost.date_posted.desc()).all()
    
    return render_template('admin_dashboard.html', 
                           user=current_user, 
                           initiatives=initiatives, 
                           requests=requests, 
                           total_users=total_users,
                           inventory_items=inventory_items,
                           trending=trending_posts,
                           recent=recent_posts,
                           current_date=current_date)



@views.route('/update-request-status/<int:id>', methods=['POST'])
@login_required
def update_request_status(id):
    """
    Updates status of service requests with department-specific security.
    Uses correct model attributes: service_type, quantity_requested, stock_quantity.
    """
    req = ServiceRequest.query.get_or_404(id)
    new_status = request.form.get('status')
    old_status = req.status

    # STRICT ACCESS CONTROL
    if current_user.role == 'Admin_LGU':
        flash('Unauthorized: LGU Admins cannot manage departmental service requests.', category='error')
        return redirect(url_for('views.status'))

    if req.service_type == 'Seed' and current_user.role not in ['Admin_DA', 'Superadmin']:
        flash('Unauthorized: Only DA Admins or Superadmins can manage Seed requests.', category='error')
        return redirect(url_for('views.status'))
    
    if req.service_type == 'Seedling' and current_user.role not in ['Admin_DENR', 'Superadmin']:
        flash('Unauthorized: Only DENR Admins or Superadmins can manage Seedling requests.', category='error')
        return redirect(url_for('views.status'))

    # Revert inventory if declined
    if new_status == 'Declined' and old_status != 'Declined':
        item = InventoryItem.query.filter_by(name=req.item_name, category=req.service_type).first()
        if item:
            item.stock_quantity += req.quantity_requested
            db.session.add(item)
    
    # Re-reserve if changing FROM declined
    elif old_status == 'Declined' and new_status != 'Declined':
        item = InventoryItem.query.filter_by(name=req.item_name, category=req.service_type).first()
        if item:
            if item.stock_quantity >= req.quantity_requested:
                item.stock_quantity -= req.quantity_requested
                db.session.add(item)
            else:
                flash('Insufficient stock to re-reserve item.', category='error')
                return redirect(url_for('views.status'))

    req.status = new_status
    db.session.commit()
    flash(f'Request status updated to {new_status}.', category='success')
    return redirect(url_for('views.status'))

@views.route('/delete-initiative/<int:id>', methods=['POST'])
@login_required
def delete_initiative(id):
    if current_user.role not in ['Superadmin', 'Admin_LGU']:
        flash('Unauthorized action.', category='error')
        return redirect(url_for('views.admin_dashboard'))
        
    initiative = Initiative.query.get_or_404(id)
    try:
        # Delete related participations first to avoid foreign key constraint errors
        Participation.query.filter_by(initiative_id=id).delete()
        db.session.delete(initiative)
        db.session.commit()
        flash('Initiative deleted successfully.', category='success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting initiative.', category='error')
        print(e)
        
    return redirect(url_for('views.admin_dashboard'))


# --- Service & Inventory Routes ---

@views.route('/ecoservices')
@login_required
def ecoservices():
    """
    Role-based EcoServices view:
    - DA Admin: Only shows Seed-related services.
    - DENR Admin: Only shows Seedling-related services.
    - LGU/User: Shows both.
    """
    show_seeds = True
    show_seedlings = True

    if current_user.role == 'Admin_DA':
        show_seedlings = False
    elif current_user.role == 'Admin_DENR':
        show_seeds = False

    return render_template('ecoservices.html', 
                           show_seeds=show_seeds, 
                           show_seedlings=show_seedlings, 
                           user=current_user)

@views.route('/about-seeds')
@login_required
def about_ecoservice_seeds():
    return render_template('ecoservice-about-seeds.html')

@views.route('/about-seedlings')
@login_required
def about_ecoservice_seedlings():
    return render_template('ecoservice-about-seedlings.html')

@views.route('/seed-inventory')
@login_required
def seed_inventory():
    # Capture the search query from the URL
    q = request.args.get('search', '')
    
    if q:
        # Filter by name if search query exists
        items = InventoryItem.query.filter(
            InventoryItem.category == 'Seed',
            InventoryItem.name.contains(q)
        ).all()
    else:
        items = InventoryItem.query.filter_by(category='Seed').all()
        
    return render_template('inventory-seeds.html', items=items, user=current_user, search_query=q)

@views.route('/seedling-inventory')
@login_required
def tree_seedlings_inventory():
    # Capture the search query from the URL
    q = request.args.get('search', '')
    
    if q:
        items = InventoryItem.query.filter(
            InventoryItem.category == 'Seedling',
            InventoryItem.name.contains(q)
        ).all()
    else:
        items = InventoryItem.query.filter_by(category='Seedling').all()
        
    return render_template('inventory-tree-seedlings.html', items=items, user=current_user, search_query=q)

@views.route('/edit-item/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_item(id):
    item = InventoryItem.query.get_or_404(id)
    source = request.args.get('source', '')
    
    if request.method == 'POST':
        item.name = request.form.get('name')
        item.stock_quantity = int(request.form.get('stock')) if request.form.get('stock') else 0
        item.description = request.form.get('description')
        
        # Handle new image if uploaded
        image_file = request.files.get('image')
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            image_file.save(os.path.join(upload_folder, filename))
            item.image_filename = filename
            
        db.session.commit()
        flash(f'{item.name} updated!', category='success')
        
        # Check if source is from dashboard to redirect back there
        form_source = request.form.get('source', '')
        if form_source == 'dashboard':
            return redirect(url_for('views.admin_dashboard', view='inventory'))
        return redirect(url_for('views.seed_inventory' if item.category == 'Seed' else 'views.tree_seedlings_inventory'))

    return render_template('manage_inventory.html', item=item, user=current_user, source=source)

@views.route('/manage-inventory', methods=['GET', 'POST'])
@login_required
def manage_inventory():
    if current_user.role not in ['Admin_DA', 'Admin_DENR', 'Admin_LGU', 'Superadmin']:
        flash('Unauthorized.', category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        stock = request.form.get('stock')
        description = request.form.get('description')
        source = request.form.get('source', '')
        
        # Handle Image Upload
        image_file = request.files.get('image')
        filename = 'default_item.png'
        
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            image_file.save(os.path.join(upload_folder, filename))

        new_item = InventoryItem(
            name=name, 
            category=category, 
            stock_quantity=int(stock) if stock else 0, 
            description=description,
            image_filename=filename
        )
        db.session.add(new_item)
        db.session.commit()
        
        flash(f'{name} added to inventory!', category='success')
        
        # Check if source is from dashboard to redirect back there
        if source == 'dashboard':
            return redirect(url_for('views.admin_dashboard', view='inventory'))
        return redirect(url_for('views.seed_inventory' if category == 'Seed' else 'views.tree_seedlings_inventory'))
            
    return render_template('manage_inventory.html', user=current_user)

@views.route('/request-seeds-form', methods=['GET', 'POST'])
@login_required
def request_seeds_form():
    if request.method == 'POST':
        # 1. Handle the Site Photo Upload
        image_file = request.files.get('site_photo')
        image_filename = None
        
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            # Create a unique filename to prevent overwriting
            unique_filename = f"user_{current_user.id}_seeds_{filename}"
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            image_file.save(os.path.join(upload_folder, unique_filename))
            image_filename = unique_filename

        # 2. Collect Metadata for concatenated description
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        group_name = request.form.get('group_name', 'N/A')
        req_type = request.form.get('requesterType')
        phone = request.form.get('phone')
        province = request.form.get('province')
        city = request.form.get('city')
        barangay = request.form.get('barangay')
        area_type = request.form.get('areaType')
        intended_use = ", ".join(request.form.getlist('intendedUse'))
        plan_desc = request.form.get('plan_desc')

        detailed_info = (
            f"Requester: {first_name} {last_name} ({req_type})\n"
            f"Group: {group_name}\nContact: {phone}\n"
            f"Location: {barangay}, {city}, {province}\n"
            f"Area Type: {area_type}\nIntended Use: {intended_use}\n"
            f"Plan: {plan_desc}"
        )

        # 3. Process each selected crop
        selected_crop_ids = request.form.getlist('crops')
        if not selected_crop_ids:
            flash('Please select at least one crop.', category='error')
            return redirect(url_for('views.request_seeds_form'))

        for seed_id in selected_crop_ids:
            seed_item = InventoryItem.query.get(seed_id)
            if not seed_item:
                continue
            
            qty_str = request.form.get(f'qty_{seed_id}')
            qty = int(qty_str) if (qty_str and qty_str.isdigit()) else 1
            
            # Stock Deduction
            if seed_item.stock_quantity >= qty:
                seed_item.stock_quantity -= qty
            else:
                qty = seed_item.stock_quantity
                seed_item.stock_quantity = 0
            
            # Create the Request record
            new_req = ServiceRequest(
                user_id=current_user.id,
                item_name=seed_item.name,
                service_type='Seed',
                quantity_requested=qty,
                planting_site_desc=detailed_info,
                image_filename=image_filename  # Make sure this field exists in your Model
            )
            db.session.add(new_req)
        
        db.session.commit()
        flash('Your seed request has been submitted successfully!', category='success')
        return redirect(url_for('views.status'))
    
    seeds = InventoryItem.query.filter(InventoryItem.category == 'Seed', InventoryItem.stock_quantity > 0).all()
    return render_template('request-form-seeds.html', user=current_user, seeds=seeds)

@views.route('/request-seedlings-form', methods=['GET', 'POST'])
@login_required
def request_seedlings_form():
    if request.method == 'POST':
        # 1. Handle the Site Photo Upload
        image_file = request.files.get('site_photo')
        image_filename = None
        
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            unique_filename = f"user_{current_user.id}_trees_{filename}"
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            image_file.save(os.path.join(upload_folder, unique_filename))
            image_filename = unique_filename

        # 2. Collect Metadata
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        group_name = request.form.get('group_name', 'N/A')
        req_type = request.form.get('requesterType')
        phone = request.form.get('phone')
        province = request.form.get('province')
        city = request.form.get('city')
        barangay = request.form.get('barangay')
        area_type = request.form.get('areaType')
        intended_use = ", ".join(request.form.getlist('intendedUse'))
        plan_desc = request.form.get('plan_desc')

        detailed_info = (
            f"Requester: {first_name} {last_name} ({req_type})\n"
            f"Group: {group_name}\nContact: {phone}\n"
            f"Location: {barangay}, {city}, {province}\n"
            f"Area Type: {area_type}\nIntended Purpose: {intended_use}\n"
            f"Plan: {plan_desc}"
        )

        # 3. Process selected seedlings
        selected_item_ids = request.form.getlist('seedlings')
        if not selected_item_ids:
            flash('Please select at least one seedling type.', category='error')
            return redirect(url_for('views.request_seedlings_form'))

        for item_id in selected_item_ids:
            tree_item = InventoryItem.query.get(item_id)
            if not tree_item:
                continue
            
            qty_str = request.form.get(f'qty_{item_id}')
            qty = int(qty_str) if (qty_str and qty_str.isdigit()) else 1
            
            # Stock Deduction
            if tree_item.stock_quantity >= qty:
                tree_item.stock_quantity -= qty
            else:
                qty = tree_item.stock_quantity
                tree_item.stock_quantity = 0
            
            new_req = ServiceRequest(
                user_id=current_user.id,
                item_name=tree_item.name,
                service_type='Seedling',
                quantity_requested=qty,
                planting_site_desc=detailed_info,
                image_filename=image_filename
            )
            db.session.add(new_req)
        
        db.session.commit()
        flash('Your seedling request has been submitted successfully!', category='success')
        return redirect(url_for('views.status'))
    
    seedlings = InventoryItem.query.filter(InventoryItem.category == 'Seedling', InventoryItem.stock_quantity > 0).all()
    return render_template('request-form-seedlings.html', user=current_user, seedlings=seedlings)


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
            'description': request.form.get('description'),
            'latitude': request.form.get('latitude'),
            'longitude': request.form.get('longitude')
        }
        return redirect(url_for('views.launch_initiative2'))
    return render_template('launch_initiative1.html', user=current_user)

@views.route('/launch-initiative-2', methods=['GET', 'POST'])
@login_required
def launch_initiative2():
    if request.method == 'POST':
        part1 = session.get('init_part1', {})
        
        # --- NEW IMAGE HANDLING LOGIC ---
        image_file = request.files.get('event_image')
        filename = 'default_event.png' # Fallback
        
        if image_file and image_file.filename and allowed_file(image_file.filename):
            original_filename = secure_filename(image_file.filename)
            # Create a unique name to avoid conflicts
            filename = f"user_{current_user.id}_{int(datetime.utcnow().timestamp())}_{original_filename}"
            
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            image_file.save(os.path.join(upload_folder, filename))
        # --------------------------------

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
            image_filename=filename, # Use the saved filename here
            status='Pending',
            latitude=part1.get('latitude'),
            longitude=part1.get('longitude')
        )
        db.session.add(new_initiative)
        db.session.commit()
        session.pop('init_part1', None)
        flash('Initiative submitted for approval!', category='success')
        return redirect(url_for('views.status'))
    return render_template('launch_initiative2.html', user=current_user)
    return render_template('launch_initiative2.html', user=current_user)

@views.route('/api/events')
def api_events():
    """
    Returns JSON data for all approved initiatives for the map.
    """
    initiatives = Initiative.query.filter_by(status='Approved').all()
    events_data = []
    
    for event in initiatives:
        # Default coords (Naga City) if missing
        lat = event.latitude if event.latitude else 13.6192
        lng = event.longitude if event.longitude else 123.1859
        
        events_data.append({
            'id': event.id,
            'title': event.title,
            'image_url': event.image_url,
            'org_name': event.org_name if event.org_name else 'Community Event',
            'location': f"{event.city}",
            'lat': lat,
            'lng': lng
        })
        
    return jsonify(events_data)
# --- Admin Controls ---

@views.route('/add-initiative', methods=['POST'])
@login_required
def add_initiative():
    if current_user.role not in ['Admin_LGU', 'Superadmin']:
        flash('Unauthorized action.', category='error')
        return redirect(url_for('views.admin_dashboard'))

    # Handle Image Upload
    image_file = request.files.get('image')
    filename = 'default_event.png'
    
    if image_file and image_file.filename and allowed_file(image_file.filename):
        original_filename = secure_filename(image_file.filename)
        filename = f"init_{current_user.id}_{int(datetime.utcnow().timestamp())}_{original_filename}"
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        image_file.save(os.path.join(upload_folder, filename))

    new_initiative = Initiative(
        user_id=current_user.id,
        title=request.form.get('title'),
        event_type=request.form.get('event_type'),
        date=request.form.get('date'),
        time=request.form.get('time'),
        province=request.form.get('province'),
        city=request.form.get('city'),
        address_line1=request.form.get('address_line1'),
        org_name=request.form.get('org_name'),
        description=request.form.get('description'),
        image_filename=filename,
        status='Approved' # Admin created initiatives are auto-approved
    )
    
    try:
        db.session.add(new_initiative)
        db.session.commit()
        flash('Initiative created successfully!', category='success')
    except Exception as e:
        db.session.rollback()
        flash('Error creating initiative.', category='error')
        print(f"Error: {e}")
        
    return redirect(url_for('views.admin_dashboard'))

@views.route('/edit-initiative/<int:id>', methods=['POST'])
@login_required
def edit_initiative(id):
    if current_user.role not in ['Admin_LGU', 'Superadmin']:
        flash('Unauthorized action.', category='error')
        return redirect(url_for('views.admin_dashboard'))
        
    initiative = Initiative.query.get_or_404(id)
    
    initiative.title = request.form.get('title')
    initiative.event_type = request.form.get('event_type')
    initiative.date = request.form.get('date')
    initiative.time = request.form.get('time')
    initiative.province = request.form.get('province')
    initiative.city = request.form.get('city')
    initiative.address_line1 = request.form.get('address_line1')
    initiative.org_name = request.form.get('org_name')
    initiative.description = request.form.get('description')
    
    # Handle Image Upload (Optional Update)
    image_file = request.files.get('image')
    if image_file and image_file.filename and allowed_file(image_file.filename):
        original_filename = secure_filename(image_file.filename)
        filename = f"init_{current_user.id}_{int(datetime.utcnow().timestamp())}_{original_filename}"
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        image_file.save(os.path.join(upload_folder, filename))
        initiative.image_filename = filename # Update filename
        
    try:
        db.session.commit()
        flash('Initiative updated successfully!', category='success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating initiative.', category='error')
        print(f"Error: {e}")
        
    return redirect(url_for('views.admin_dashboard'))

@views.route('/approve-initiative/<int:id>', methods=['POST'])
@login_required
def approve_initiative(id):
    """
    Secured route: Only LGU Admins can approve community initiatives.
    """
    if current_user.role not in ['Admin_LGU', 'Superadmin']:
        flash('Unauthorized: Only LGU Admins and Superadmins can approve initiatives.', category='error')
        return redirect(url_for('views.home'))
    
    initiative = Initiative.query.get_or_404(id)
    initiative.status = 'Approved'
    db.session.commit()
    flash('Initiative Approved!', category='success')
    return redirect(url_for('views.admin_dashboard'))

@views.route('/participate/<int:initiative_id>', methods=['POST'])
@login_required
def participate(initiative_id):
    initiative = Initiative.query.get_or_404(initiative_id)
    
    # 1. Prevent Admins from participating
    if current_user.is_admin:
        return jsonify({'error': 'Admins cannot participate in initiatives.'}), 403
        
    # 2. Prevent Creators from participating in their own event
    if initiative.user_id == current_user.id:
        return jsonify({'error': 'You cannot join your own initiative.'}), 403

    data = request.get_json()
    
    # --- Input Validation ---
    full_name = data.get('full_name', '').strip()
    address = data.get('address', '').strip()
    contact = data.get('contact', '').strip()
    email = data.get('email', '').strip()
    purpose = data.get('purpose', '').strip()

    if not all([full_name, address, contact, email, purpose]):
        return jsonify({'error': 'All fields are required.'}), 400
    
    if "@" not in email or "." not in email:
        return jsonify({'error': 'Please enter a valid email address.'}), 400

    # --- Save to Database ---
    new_participation = Participation(
        user_id=current_user.id,
        initiative_id=initiative_id,
        full_name=full_name,
        address=address,
        contact_number=contact,
        email=email,
        purpose=purpose
    )
    
    db.session.add(new_participation)
    db.session.commit()
    
    return jsonify({'message': 'Success'}), 200

@views.route('/get-participants/<int:id>')
@login_required
def get_participants(id):
    initiative = Initiative.query.get_or_404(id)
    # Security: Only allow the creator or an admin to see the list
    if initiative.user_id != current_user.id and not current_user.is_admin:
        return jsonify([]), 403
    
    registrants = Participation.query.filter_by(initiative_id=id).all()
    return jsonify([{'name': r.full_name, 'email': r.email} for r in registrants])

# --- Auxiliary Page Routes ---

@views.route('/event-view/<int:id>')
@login_required
def event_view(id):
    # Fetch the specific initiative or return a 404 error if it doesn't exist
    event = Initiative.query.get_or_404(id)
    return render_template('event-view.html', event=event, user=current_user)

@views.route('/forum')
@login_required
def forum():
    trending = ForumPost.query.order_by(ForumPost.votes.desc()).limit(3).all()
    recent = ForumPost.query.order_by(ForumPost.date_posted.desc()).all()
    return render_template('forum.html', user=current_user, trending=trending, recent=recent)


@views.route('/forum-post-partial/<int:id>')
@login_required
def forum_post_partial(id):
    post = ForumPost.query.get_or_404(id)
    # Get current user's vote type
    user_vote = PostVote.query.filter_by(user_id=current_user.id, post_id=id).first()
    user_vote_type = user_vote.vote_type if user_vote else None
    
    comments = Comment.query.filter_by(post_id=id, parent_id=None).order_by(Comment.date_posted.desc()).all()
    
    return render_template('components/forum_post_partials.html', 
                           user=current_user, 
                           post=post, 
                           user_vote_type=user_vote_type,
                           comments=comments)


@views.route('/forum-view/<int:id>')
@login_required
def forum_view(id):
    post = ForumPost.query.get_or_404(id)
    # Get current user's vote type for this post
    user_vote = PostVote.query.filter_by(user_id=current_user.id, post_id=id).first()
    user_vote_type = user_vote.vote_type if user_vote else None
    
    comments = Comment.query.filter_by(post_id=id, parent_id=None).order_by(Comment.date_posted.desc()).all()
    return render_template('forum-view.html', 
                           user=current_user, 
                           post=post, 
                           user_vote_type=user_vote_type,
                           comments=comments)

@views.route('/add-comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    content = request.form.get('content')
    parent_id = request.form.get('parent_id') # Will be None for main comments
    
    if content:
        new_comment = Comment(
            content=content,
            user_id=current_user.id,
            post_id=post_id,
            parent_id=parent_id
        )
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment posted!', category='success')
    
    return redirect(url_for('views.forum_view', id=post_id))

@views.route('/create-post', methods=['POST'])
@login_required
def create_post():
    title = request.form.get('title')
    content = request.form.get('content')
    category = request.form.get('category')
    
    # 1. Get the image file from the request
    image = request.files.get('image')
    
    if not title or not content:
        flash('Title and content are required!', category='error')
        return redirect(url_for('views.forum'))

    if category == 'News' and not current_user.is_admin:
        flash('Unauthorized: Only admins can post News.', category='error')
        return redirect(url_for('views.forum'))

    image_filename = None

    # 2. Process the image if it exists
    if image and image.filename != '':
        # Define and ensure the upload path exists
        upload_path = os.path.join(current_app.root_path, 'static', 'uploads')
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)

        # Generate a unique filename to avoid collisions
        original_filename = secure_filename(image.filename)
        extension = os.path.splitext(original_filename)[1]
        image_filename = f"{uuid.uuid4().hex}{extension}"
        
        # Save the file to the disk
        image.save(os.path.join(upload_path, image_filename))

    # 3. Save to Database
    new_post = ForumPost(
        title=title, 
        content=content, 
        category=category, 
        user_id=current_user.id,
        image_filename=image_filename # This column must exist in your ForumPost model
    )
    
    try:
        db.session.add(new_post)
        db.session.commit()
        flash('Post created successfully!', category='success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while creating the post.', category='error')
        print(f"Error: {e}")



    source = request.form.get('source')
    if source == 'dashboard':
        return redirect(url_for('views.admin_dashboard', view='forum'))

    return redirect(url_for('views.forum'))

@views.route('/delete-post/<int:id>', methods=['POST'])
@login_required
def delete_post(id):
    post = ForumPost.query.get_or_404(id)
    
    # Check ownership or Superadmin
    if current_user.id != post.user_id and current_user.role != 'Superadmin':
        flash('You do not have permission to delete this post.', category='error')
        return redirect(url_for('views.forum_view', id=id))

    try:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted successfully.', category='success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the post.', category='error')
        print(f"Error: {e}")

    source = request.args.get('source')
    if source == 'dashboard':
        return redirect(url_for('views.admin_dashboard', view='forum'))

    return redirect(url_for('views.forum'))

@views.route('/vote-post/<int:post_id>', methods=['POST'])
@login_required
def vote_post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    data = request.get_json()
    vote_type = data.get('vote_type') # 'up' or 'down'
    
    # Check if this user has already voted on this post
    existing_vote = PostVote.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    # Logic: 
    # 1. If no vote exists: Create new vote.
    # 2. If same vote exists: Remove it (toggle off).
    # 3. If opposite vote exists: Change the type and update total.
    
    change_in_total = 0
    new_status = None # 'up', 'down', or None
    
    if not existing_vote:
        # Create new vote
        new_vote = PostVote(user_id=current_user.id, post_id=post_id, vote_type=vote_type)
        db.session.add(new_vote)
        change_in_total = 1 if vote_type == 'up' else -1
        new_status = vote_type
    else:
        if existing_vote.vote_type == vote_type:
            # Toggle off (Remove existing vote)
            change_in_total = -1 if vote_type == 'up' else 1
            db.session.delete(existing_vote)
            new_status = None
        else:
            # Switch vote type (e.g., from up to down)
            # If switching up -> down: total goes down by 2 (+1 becomes -1)
            # If switching down -> up: total goes up by 2 (-1 becomes +1)
            change_in_total = -2 if vote_type == 'down' else 2
            existing_vote.vote_type = vote_type
            new_status = vote_type

    post.votes += change_in_total
    db.session.commit()
    
    return jsonify({
        'votes': post.votes,
        'status': new_status
    })


@views.route('/event-map')
@login_required
def event_map():
    return render_template('event-map.html')