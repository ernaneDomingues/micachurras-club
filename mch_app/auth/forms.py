from flask_wtf import FlaskForm
# 1. IMPORTAR NOVOS CAMPOS E VALIDATORS
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from mch_app.models import Usuario
# 2. IMPORTAR DATE/DATETIME PARA VALIDAÇÃO
from datetime import date

class LoginForm(FlaskForm):
    """Formulário de Login com Flask-WTF."""
    email = StringField('Email', 
        validators=[
            DataRequired(message="O email é obrigatório."), 
            Email(message="Por favor, insira um email válido.")
        ],
        render_kw={'placeholder': 'seuemail@churras.com'})
    
    password = PasswordField('Senha', 
        validators=[DataRequired(message="A senha é obrigatória.")],
        render_kw={'placeholder': '••••••••'})
        
    remember_me = BooleanField('Lembrar de mim')
    
    submit = SubmitField('Entrar')


class RegistrationForm(FlaskForm):
    """Formulário de Registro com Flask-WTF."""
    
    nome = StringField('Nome', 
        validators=[DataRequired(message="O nome é obrigatório.")],
        render_kw={'placeholder': 'Seu nome completo'})
        
    email = StringField('Email', 
        validators=[
            DataRequired(message="O email é obrigatório."), 
            Email(message="Por favor, insira um email válido.")
        ],
        render_kw={'placeholder': 'seuemail@churras.com'})
    
    # 3. ADICIONAR NOVOS CAMPOS
    data_nascimento = DateField('Data de Nascimento', 
        validators=[DataRequired(message="A data de nascimento é obrigatória.")],
        format='%Y-%m-%d') # Formato 'AAAA-MM-DD' esperado do HTML

    telefone = StringField('Telefone / WhatsApp',
        validators=[DataRequired(message="O telefone é obrigatório.")],
        render_kw={'placeholder': '(11) 99999-8888'})

    bloco = SelectField('Bloco', 
        choices=[
            ('', '--- Selecione seu Bloco ---'),
            ('A', 'Bloco A - Lírio'),
            ('B', 'Bloco B - Jasmin'),
            ('C', 'Bloco C - Hortênsia'),
            ('D', 'Bloco D - Azaleia')
        ],
        validators=[DataRequired(message="Selecione o seu bloco.")])

    apartamento = StringField('Apartamento',
        validators=[DataRequired(message="O número do apartamento é obrigatório.")],
        render_kw={'placeholder': 'Ex: 101'})
    # FIM DOS NOVOS CAMPOS
    
    password = PasswordField('Senha', 
        validators=[
            DataRequired(message="A senha é obrigatória."),
            Length(min=8, message="A senha deve ter pelo menos 8 caracteres.")
        ],
        render_kw={'placeholder': '••••••••'})
    
    password2 = PasswordField('Confirme a Senha', 
        validators=[
            DataRequired(message="A confirmação de senha é obrigatória."),
            EqualTo('password', message='As senhas devem ser iguais.')
        ],
        render_kw={'placeholder': '••••••••'})
    
    submit = SubmitField('Criar Conta')

    # Validador customizado para checar se o email já existe no banco
    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('Este email já está em uso. Por favor, escolha outro.')

    # 4. ADICIONAR VALIDADOR DE IDADE
    def validate_data_nascimento(self, data_nascimento):
        if data_nascimento.data:
            hoje = date.today()
            idade = hoje.year - data_nascimento.data.year - \
                    ((hoje.month, hoje.day) < (data_nascimento.data.month, data_nascimento.data.day))
            if idade < 18:
                raise ValidationError('Você deve ser maior de 18 anos para se registrar.')

