from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .config import config_by_name # Importa nosso dicionário de configs
from datetime import datetime

# Inicializa as extensões (ainda não vinculadas a um app)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Configura o Flask-Login
# Para onde o usuário será redirecionado se tentar acessar uma página protegida
login_manager.login_view = 'auth.login'
# Mensagem mostrada ao ser redirecionado
login_manager.login_message = 'Por favor, faça o login para acessar esta página.'
login_manager.login_message_category = 'info' # Categoria para 'flash'

def create_app(config_name='default'):
    """
    Fábrica de Aplicações (App Factory).
    Cria e configura a instância do aplicativo Flask.
    """
    app = Flask(__name__)
    
    # Carrega a configuração (DevelopmentConfig ou ProductionConfig)
    app.config.from_object(config_by_name[config_name])

    # Inicializa as extensões com o app
    db.init_app(app)
    migrate.init_app(app, db) # Vincula o migrate ao app e ao db
    login_manager.init_app(app)

    # --- Registro dos Blueprints ---
    
    # Blueprint Principal (páginas estáticas)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Blueprint de Autenticação (login, registro)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # Blueprint de Conta (edição de perfil)
    from .account import account as account_blueprint
    app.register_blueprint(account_blueprint, url_prefix='/account')

    # Blueprint de Pagamento (Stripe)
    from .payment import payment as payment_blueprint
    app.register_blueprint(payment_blueprint, url_prefix='/payment')

    # --- Context Processor ---
    @app.context_processor
    def inject_current_year():
        """Injeta o ano atual em todos os templates."""
        return {'current_year': datetime.utcnow().year}

    return app

