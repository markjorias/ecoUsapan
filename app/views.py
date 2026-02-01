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
    return render_template('seed_inventory.html')

@views.route('/tree-seedlings-inventory')
def tree_seedlings_inventory():
    return render_template('tree_seedlings_inventory.html')

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

@views.route('/seeds-view')
def seeds_view():
    return render_template('seeds-view.html')

@views.route('/seedlings-view')
def seedlings_view():
    return render_template('seedlings-view.html')

@views.route('/event-map')
def event_map():
    return render_template('event-map.html')

@views.route('/status')
def status():
    return render_template('status.html')

@views.route('/about-ecoservice-seeds')
def about_ecoservice_seeds():
    return render_template('about-ecoservice-seeds.html')

@views.route('/about-ecoservice-seedlings')
def about_ecoservice_seedlings():
    return render_template('about-ecoservice-seedlings.html')

@views.route('/request-seeds-form')
def request_seeds_form():
    return render_template('request-seeds-form.html')

@views.route('/request-seedlings-form')
def request_seedlings_form():
    return render_template('request-seedlings-form.html')

@views.route('/ecoservices')
def ecoservices():
    return render_template('ecoservices.html')