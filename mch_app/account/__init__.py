from flask import Blueprint

# Define o Blueprint 'account'
account = Blueprint('account', __name__)

# Importa as rotas e formulários no final
from . import routes, forms

