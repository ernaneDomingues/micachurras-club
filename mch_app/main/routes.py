from flask import render_template
from . import main

@main.route('/')
@main.route('/index')
def index():
    """Rota para a página inicial."""
    return render_template('index.html', title='Início')
