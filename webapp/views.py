from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from flask_login import login_required, current_user
from .models import Initiative, ServiceRequest, Participation, InventoryItem
from . import db
from datetime import datetime
import os
from werkzeug.utils import secure_filename
views = Blueprint('views', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@views.route('/')
@login_required
def home():
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
    # Role-based dashboard filtering
    if current_user.role == 'Admin_LGU':
        initiatives = Initiative.query.all()
        requests = ServiceRequest.query.all()
        is_admin_view = True
    elif current_user.role == 'Admin_DA':
        initiatives = []
        requests = ServiceRequest.query.filter_by(service_type='Seed').all()
        is_admin_view = True
    elif current_user.role == 'Admin_DENR':
        initiatives = []
        requests = ServiceRequest.query.filter_by(service_type='Seedling').all()
        is_admin_view = True
    else:
        initiatives = Initiative.query.filter_by(user_id=current_user.id).all()
        requests = ServiceRequest.query.filter_by(user_id=current_user.id).all()
        is_admin_view = False

    return render_template('status.html', initiatives=initiatives, requests=requests, user=current_user, is_admin_view=is_admin_view)

@views.route('/update-request-status/<int:id>', methods=['POST'])
@login_required
def update_request_status(id):
    if not current_user.is_admin:
        return redirect(url_for('views.home'))
        
    req = ServiceRequest.query.get_or_404(id)
    new_status = request.form.get('status')
    old_status = req.status
    
    # Logic for Reverting Stock if Declined
    # We only revert if it's changing TO Declined from something else
    if new_status == 'Declined' and old_status != 'Declined':
        # Find the item in inventory
        item = InventoryItem.query.filter_by(
            name=req.item_name, 
            category=req.service_type
        ).first()
        
        if item:
            item.stock_quantity += req.quantity_requested
            db.session.add(item)
            flash(f'Request declined. {req.quantity_requested} units added back to {item.name} stock.', category='info')
    
    # Logic if changing FROM Declined back to something else (e.g. accidentally declined)
    elif old_status == 'Declined' and new_status != 'Declined':
        item = InventoryItem.query.filter_by(
            name=req.item_name, 
            category=req.service_type
        ).first()
        
        if item:
            if item.stock_quantity >= req.quantity_requested:
                item.stock_quantity -= req.quantity_requested
                db.session.add(item)
            else:
                flash(f'Cannot change status. Not enough stock to re-reserve this item.', category='error')
                return redirect(url_for('views.status'))

    req.status = new_status
    db.session.commit()
    flash(f'Request status updated to {new_status}.', category='success')
    return redirect(url_for('views.status'))

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
    return render_template('about-ecoservice-seeds.html')

@views.route('/about-seedlings')
@login_required
def about_ecoservice_seedlings():
    return render_template('about-ecoservice-seedlings.html')

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
        
    return render_template('seed_inventory.html', items=items, user=current_user, search_query=q)

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
        
    return render_template('tree_seedlings_inventory.html', items=items, user=current_user, search_query=q)

@views.route('/edit-item/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_item(id):
    item = InventoryItem.query.get_or_404(id)
    
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
        return redirect(url_for('views.seed_inventory' if item.category == 'Seed' else 'views.tree_seedlings_inventory'))

    return render_template('manage_inventory.html', item=item, user=current_user)

@views.route('/manage-inventory', methods=['GET', 'POST'])
@login_required
def manage_inventory():
    if current_user.role not in ['Admin_DA', 'Admin_DENR', 'Admin_LGU']:
        flash('Unauthorized.', category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        stock = request.form.get('stock')
        description = request.form.get('description')
        
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
    return render_template('request-seeds-form.html', user=current_user, seeds=seeds)

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
    return render_template('request-seedlings-form.html', user=current_user, seedlings=seedlings)


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