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
