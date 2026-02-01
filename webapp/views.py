from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('home.html')

@views.route('/launch-initiative-1')
def launch_initiative1():
    return render_template('launch_initiative1.html')

@views.route('/launch-initiative-2')
def launch_initiative2():
    return render_template('launch_initiative2.html')

@views.route('/seed-inventory')
def seed_inventory():
    return render_template('inventory-seeds.html')

@views.route('/tree-seedlings-inventory')
def tree_seedlings_inventory():
    return render_template('inventory-tree-seedlings.html')

@views.route('/events')
def events():
    return render_template('events.html')

@views.route('/forum')
def forum():
    return render_template('forum.html')

@views.route('/event-view')
def event_view():
    return render_template('event-view.html')

@views.route('/forum-view')
def forum_view():
    return render_template('forum-view.html')


@views.route('/event-map')
def event_map():
    return render_template('event-map.html')

@views.route('/status')
def status():
    return render_template('status.html')

@views.route('/about-ecoservice-seeds')
def about_ecoservice_seeds():
    return render_template('ecoservice-about-seeds.html')

@views.route('/about-ecoservice-seedlings')
def about_ecoservice_seedlings():
    return render_template('ecoservice-about-seedlings.html')

@views.route('/request-seeds-form')
def request_seeds_form():
    return render_template('request-form-seeds.html')

@views.route('/request-seedlings-form')
def request_seedlings_form():
    return render_template('request-form-seedlings.html')

@views.route('/ecoservices')
def ecoservices():
    return render_template('ecoservices.html')

@views.route('/feature-view')
def feature_view():
    return render_template('feature-view.html')