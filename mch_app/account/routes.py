from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from mch_app import db
from . import account
from .forms import UpdateAccountForm
# Importar o Stripe se for gerenciar o portal do cliente
import stripe

@account.route('/my_account', methods=['GET', 'POST'])
@login_required
def my_account():
    """Rota para visualizar e editar os dados da conta."""
    form = UpdateAccountForm()
    
    if form.validate_on_submit():
        # Atualiza os dados do usuário
        current_user.name = form.name.data
        current_user.email = form.email.data.lower()
        current_user.phone = form.phone.data
        current_user.building_block = form.building_block.data
        current_user.apartment_number = form.apartment_number.data
        
        try:
            db.session.commit()
            flash('Sua conta foi atualizada com sucesso!', 'success')
            return redirect(url_for('account.my_account'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar a conta: {e}', 'danger')

    elif request.method == 'GET':
        # Preenche o formulário com os dados atuais do usuário
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.phone.data = current_user.phone
        form.building_block.data = current_user.building_block
        form.apartment_number.data = current_user.apartment_number
        
    return render_template('account/account.html', title='Minha Conta', form=form)

