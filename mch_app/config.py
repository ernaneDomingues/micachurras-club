import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env (especialmente a URL do Neon)
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '..', '.env')) # Sobe um nível para achar o .env

class Config:
    """Configurações base do app."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'voce-nunca-vai-adivinhar'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Configuração de Desenvolvimento (local, com SQLite)"""
    DEBUG = True
    # Define o banco de dados local como SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '..', 'mch_app_dev.db')

class ProductionConfig(Config):
    """Configuração de Produção (online, com Neon/PostgreSQL)"""
    DEBUG = False
    # Pega a URL do banco de dados do Neon do arquivo .env
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # Nota: A URL do Neon/PostgreSQL começa com 'postgresql://...'

# Um dicionário para facilitar a seleção da config
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
