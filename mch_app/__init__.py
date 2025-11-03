from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .config import config_by_name # Importa nossas configs

# Cria instâncias das extensões (ainda não ligadas ao app)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
# Se o usuário não estiver logado, redireciona para a rota 'auth.login'
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


def create_app(config_name='default'):
    """
    Esta é a App Factory.
    Ela cria e configura a instância do app Flask.
    """
    app = Flask(__name__)
    
    # 1. Carrega a configuração (Dev ou Prod)
    app.config.from_object(config_by_name[config_name])

    # 2. Inicializa as extensões com o app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # 3. Registra os Blueprints (nossos módulos)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth') # Rotas /auth/login, etc.
    
    # 4. Importa os modelos (para o Flask-Migrate saber)
    # Temos que fazer isso aqui depois que 'db' for criado
    from . import models

    # 5. Retorna o app pronto
    return app
