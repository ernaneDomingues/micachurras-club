from flask import render_template
from . import main

@main.route('/')
@main.route('/index')
def index():
    """Route for the homepage."""
    return render_template('index.html', title='Início')

