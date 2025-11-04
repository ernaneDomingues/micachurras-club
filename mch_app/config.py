import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
basedir = os.path.abspath(os.path.dirname(__file__))
# O .env está um nível acima da pasta 'mch_app'
load_dotenv(os.path.join(basedir, '..', '.env')) 

class Config:
    """Configuração base (comum a todos os ambientes)"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma-chave-secreta-muito-dificil-de-adivinhar'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações do Stripe
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    # IDs dos Planos/Preços do Stripe (Individuais)
    STRIPE_PRICE_ID_AVULSO = os.environ.get('STRIPE_PRICE_ID_AVULSO')
    STRIPE_PRICE_ID_MENSAL = os.environ.get('STRIPE_PRICE_ID_MENSAL')
    STRIPE_PRICE_ID_ANUAL = os.environ.get('STRIPE_PRICE_ID_ANUAL')

    # IDs dos Planos/Preços do Stripe (Casal)
    STRIPE_PRICE_ID_AVULSO_CASAL = os.environ.get('STRIPE_PRICE_ID_AVULSO_CASAL')
    STRIPE_PRICE_ID_MENSAL_CASAL = os.environ.get('STRIPE_PRICE_ID_MENSAL_CASAL')

class DevelopmentConfig(Config):
    """Configuração de Desenvolvimento"""
    DEBUG = True
    # Usa SQLite para desenvolvimento local, um nível acima da pasta 'mch_app'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '..', 'mch_app_dev.db')

class ProductionConfig(Config):
    """Configuração de Produção"""
    DEBUG = False
    # Usa a URL do banco de dados do Neon (ou outro PostgreSQL)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # Adicionar outras configurações de produção (ex: logging) aqui

# Dicionário para selecionar a configuração por nome (corrige bug anterior)
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

