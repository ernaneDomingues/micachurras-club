from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, ValidationError, Length
from flask_login import current_user
from mch_app.models import User

class UpdateAccountForm(FlaskForm):
    """Formulário de Atualização de Conta."""
    name = StringField('Nome Completo', validators=[DataRequired(message="O nome é obrigatório.")])
    email = StringField('Email', validators=[DataRequired(message="O email é obrigatório."), Email(message="Email inválido.")])
    phone = StringField('Telefone (WhatsApp)', validators=[DataRequired(message="O telefone é obrigatório.")])
    
    building_block = SelectField(
        'Bloco',
        choices=[
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
    submit = SubmitField('Atualizar Dados')

    def validate_email(self, email):
        """
        Verifica se o email foi alterado para um que já existe.
        """
        if email.data.lower() != current_user.email:
            user = User.query.filter_by(email=email.data.lower()).first()
            if user:
                raise ValidationError('Este email já está em uso por outra conta.')

