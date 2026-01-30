from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return render_template('home.html')

@bp.route('/launch-initiative1')
def launch_initiative1():
    return render_template('launch_initiative1.html')

@bp.route('/launch-initiative2')
def launch_initiative2():
    return render_template('launch_initiative2.html')
