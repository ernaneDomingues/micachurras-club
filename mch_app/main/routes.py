from . import main
from flask import render_template

@main.route('/')
@main.route('/index')
def index():
    # 'index.html' virá da pasta 'mch_app/templates/index.html'
    return render_template('index.html', title='Início')
