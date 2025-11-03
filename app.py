import os
from mch_app import create_app

# Pega a configuração do ambiente (default 'development')
config_name = os.getenv('FLASK_CONFIG') or 'default'

# Cria o app usando a Factory
app = create_app(config_name)

if __name__ == '__main__':
    app.run(debug=True)
