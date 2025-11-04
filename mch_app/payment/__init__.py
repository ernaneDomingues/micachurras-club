from flask import Blueprint

# Define o Blueprint 'payment'
payment = Blueprint('payment', __name__)

# Importa as rotas no final
from . import routes

