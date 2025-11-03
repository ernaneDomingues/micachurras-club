from flask import Blueprint

# Cria o Blueprint
main = Blueprint('main', __name__)

# Importa as rotas deste Blueprint
# (colocamos no fim para evitar importação circular)
from . import routes
