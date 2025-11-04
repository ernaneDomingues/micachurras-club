from mch_app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    """Callback do Flask-Login para carregar um usuário pelo ID."""
    return db.session.get(User, int(user_id))

class User(UserMixin, db.Model):
    """Modelo de Usuário."""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(256))
    birth_date = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String(20))
    building_block = db.Column(db.String(50)) # Ex: "A"
    apartment_number = db.Column(db.String(10))
    
    # --- Campos do Stripe ---
    stripe_customer_id = db.Column(db.String(120), unique=True, index=True)
    stripe_subscription_id = db.Column(db.String(120), unique=True, index=True)
    subscription_status = db.Column(db.String(50), default='inativo') # Ex: inativo, ativo, pendente

    # --- Relacionamentos ---
    # `uselist=False` define um relacionamento um-para-um
    subscription = db.relationship('Subscription', back_populates='user', uselist=False, cascade="all, delete-orphan")
    rsvps = db.relationship('RSVP', back_populates='user', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.name} ({self.email})>'

    def set_password(self, password):
        """Gera e armazena o hash da senha."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se a senha fornecida corresponde ao hash."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_subscribed(self):
        """Propriedade para verificar se o usuário tem uma assinatura ativa."""
        return self.subscription_status == 'ativo'

class Event(db.Model):
    """Modelo de Evento (O Churrasco)."""
    __tablename__ = 'event'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='Agendado') # Ex: Agendado, Realizado, Cancelado
    price_single_ticket = db.Column(db.Float, default=139.90)

    # --- Relacionamentos ---
    rsvps = db.relationship('RSVP', back_populates='event', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Event {self.description} em {self.date}>'

class Subscription(db.Model):
    """Modelo de Assinatura (Pagamento Recorrente)."""
    __tablename__ = 'subscription'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    plan_name = db.Column(db.String(50)) # Ex: Mensal, Anual, Mensal Casal
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime) # Data de fim do período de cobrança
    status = db.Column(db.String(50), default='ativo') # Ex: ativo, cancelado, pendente

    # --- Relacionamentos ---
    user = db.relationship('User', back_populates='subscription')

    def __repr__(self):
        return f'<Subscription {self.user.name} - {self.plan_name}>'

class RSVP(db.Model):
    """Modelo de Confirmação de Presença (RSVP)."""
    __tablename__ = 'rsvp'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False, index=True)
    payment_status = db.Column(db.String(50), default='Pendente') # Ex: Pago, Pendente, Isento (assinante)
    confirmed_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- Relacionamentos ---
    user = db.relationship('User', back_populates='rsvps')
    event = db.relationship('Event', back_populates='rsvps')

    def __repr__(self):
        return f'<RSVP {self.user.name} @ {self.event.description}>'

