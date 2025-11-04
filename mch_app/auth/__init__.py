from flask import Blueprint

# Define o Blueprint 'auth'
auth = Blueprint('auth', __name__)

# Importa as rotas e formulários no final
from . import routes, forms
