from mch_app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
# 1. IMPORTAR DATE, DATETIME, ETC.
from datetime import date, datetime

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(256))
    data_nascimento = db.Column(db.Date)
    telefone = db.Column(db.String(20))
    bloco = db.Column(db.String(50))
    apartamento = db.Column(db.String(10))
    
    # --- RELACIONAMENTOS ATIVADOS ---
    
    # Campo para o ID do cliente no Stripe (MUITO IMPORTANTE)
    stripe_customer_id = db.Column(db.String(120), unique=True, index=True)
    
    # Um usuário pode ter UMA assinatura
    assinatura = db.relationship('Assinatura', backref='assinante', uselist=False, lazy='joined')
    
    # Um usuário pode ter VÁRIAS inscrições (para eventos avulsos)
    inscricoes = db.relationship('Inscricao', backref='participante', lazy='dynamic')
    # --- FIM DOS RELACIONAMENTOS ---

    def set_password(self, password):
# ... (código existente)...
    def check_password(self, password):
# ... (código existente)...

    def __repr__(self):
        return f'<Usuario {self.nome}>'

# --- NOVOS MODELOS ---

class Evento(db.Model):
    """Modelo para um churrasco (um evento no cronograma)."""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    data = db.Column(db.DateTime, nullable=False, index=True)
    local = db.Column(db.String(200))
    descricao = db.Column(db.Text)
    
    # Preços do Stripe (para facilitar a busca)
    # Preço do evento avulso
    stripe_price_id_avulso = db.Column(db.String(120)) 
    
    status = db.Column(db.String(50), default='Agendado') # Agendado, Realizado, Cancelado
    
    # Relacionamento: Quem se inscreveu neste evento
    inscritos = db.relationship('Inscricao', backref='evento', lazy='dynamic')

    def __repr__(self):
        return f'<Evento {self.nome} em {self.data}>'


class Assinatura(db.Model):
    """Controla as assinaturas (mensal/anual) dos usuários."""
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False, unique=True)
    
    # ID da assinatura no Stripe (ex: sub_...)
    stripe_subscription_id = db.Column(db.String(120), unique=True, index=True)
    # ID do plano/preço que o usuário assinou (ex: price_...)
    stripe_price_id = db.Column(db.String(120))
    
    # Status da assinatura (ex: 'active', 'canceled', 'past_due')
    status = db.Column(db.String(50), default='incomplete')
    
    plano = db.Column(db.String(50)) # 'mensal' ou 'anual'
    
    # Data que a assinatura expira (Stripe nos informa)
    data_expiracao = db.Column(db.DateTime)
    
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Assinatura {self.usuario_id} - {self.status}>'


class Inscricao(db.Model):
    """Controla os pagamentos AVULSOS para um evento específico."""
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    evento_id = db.Column(db.Integer, db.ForeignKey('evento.id'), nullable=False)
    
    # ID do Pagamento no Stripe (ex: pi_...)
    stripe_payment_intent_id = db.Column(db.String(120), unique=True, index=True)
    
    status_pagamento = db.Column(db.String(50), default='pending') # 'pending', 'succeeded', 'failed'
    
    data_pagamento = db.Column(db.DateTime)
    valor = db.Column(db.Float)

    def __repr__(self):
        return f'<Inscricao {self.usuario_id} no Evento {self.evento_id}>'

