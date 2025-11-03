from flask import Blueprint

# Define o Blueprint 'main'
main = Blueprint('main', __name__)

# Importa as rotas no final para evitar importação circular
from . import routes