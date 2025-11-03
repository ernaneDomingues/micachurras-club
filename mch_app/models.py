from mch_app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# O Flask-Login precisa desta função para carregar o usuário da sessão
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario' # Boa prática
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(256))
    
    # Relações (adicionaremos 'Inscricao' e 'Assinatura' depois)
    # inscricoes = db.relationship('Inscricao', backref='participante', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Usuario {self.nome}>'

# (Vamos adicionar os modelos Evento, Inscricao, Assinatura aqui depois)