import os
from mch_app import create_app, db
from mch_app.models import User, Event, Subscription, RSVP
from flask_migrate import Migrate

# Detecta a configuração (development ou production)
config_name = os.getenv('FLASK_CONFIG', 'development')
app = create_app(config_name)

# Configura o Flask-Migrate
migrate = Migrate(app, db)

# Adiciona o contexto do shell para 'flask shell'
@app.shell_context_processor
def make_shell_context():
    """
    Permite acesso fácil a modelos no shell do Flask
    (use `flask shell`)
    """
    return dict(db=db, User=User, Event=Event, Subscription=Subscription, RSVP=RSVP)

if __name__ == '__main__':
    app.run()

