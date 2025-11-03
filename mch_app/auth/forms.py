from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from mch_app.models import User
from datetime import date

class LoginForm(FlaskForm):
    """Formulário de Login."""
    email = StringField('Email', validators=[DataRequired(message="O email é obrigatório."), Email(message="Email inválido.")])
    password = PasswordField('Senha', validators=[DataRequired(message="A senha é obrigatória.")])
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')

class RegistrationForm(FlaskForm):
    """Formulário de Registro."""
    name = StringField('Nome Completo', validators=[DataRequired(message="O nome é obrigatório.")])
    email = StringField('Email', validators=[DataRequired(message="O email é obrigatório."), Email(message="Email inválido.")])
    birth_date = DateField('Data de Nascimento', validators=[DataRequired(message="A data de nascimento é obrigatória.")], format='%Y-%m-%d')
    phone = StringField('Telefone (WhatsApp)', validators=[DataRequired(message="O telefone é obrigatório.")])
    
    building_block = SelectField(
        'Bloco',
        choices=[
            ('', 'Selecione seu bloco...'),
            ('A', 'Bloco A - Lírio'),
            ('B', 'Bloco B - Jasmin'),
            ('C', 'Bloco C - Hortênsia'),
            ('D', 'Bloco D - Azaleia')
        ],
        validators=[DataRequired(message="Selecione um bloco.")]
    )
    apartment_number = StringField('Nº do Apartamento', validators=[
        DataRequired(message="O número do apartamento é obrigatório."),
        Length(min=2, max=4, message="Apartamento deve ter de 2 a 4 dígitos.")
    ])
    
    password = PasswordField('Senha', validators=[
        DataRequired(message="A senha é obrigatória."),
        Length(min=8, message="A senha deve ter pelo menos 8 caracteres.")
    ])
    password2 = PasswordField(
        'Repetir Senha', validators=[
            DataRequired(message="Repita a senha."),
            EqualTo('password', message='As senhas não conferem.')
        ])
    submit = SubmitField('Registrar')

    def validate_email(self, email):
        """Verifica se o email já está cadastrado."""
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('Este email já está cadastrado. Por favor, use um email diferente.')

    def validate_birth_date(self, birth_date):
        """Verifica se o usuário é maior de 18 anos."""
        today = date.today()
        age = today.year - birth_date.data.year - \
              ((today.month, today.day) < (birth_date.data.month, birth_date.data.day))
        if age < 18:
            raise ValidationError('Você deve ser maior de 18 anos para se registrar.')

