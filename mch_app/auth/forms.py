from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    """Formulário de Login com Flask-WTF."""
    
    email = StringField('Email', 
        validators=[
            DataRequired(message="O email é obrigatório."), 
            Email(message="Por favor, insira um email válido.")
        ],
        render_kw={'placeholder': 'seuemail@churras.com'})
    
    password = PasswordField('Senha', 
        validators=[
            DataRequired(message="A senha é obrigatória."),
            Length(min=6, message="A senha deve ter pelo menos 6 caracteres.")
        ],
        render_kw={'placeholder': '••••••••'})
    
    remember_me = BooleanField('Lembrar de mim')
    
    submit = SubmitField('Entrar')
