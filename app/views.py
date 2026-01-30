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

@views.route('/request-seeds')
def request_seeds():
    return render_template('request_seeds.html')

@views.route('/request-seedlings')
def request_seedlings():
    return render_template('request_seedlings.html')

@views.route('/events')
def events():
    return render_template('events.html')

@views.route('/forum')
def forum():
    return render_template('forum.html')