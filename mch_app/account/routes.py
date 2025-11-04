from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from mch_app import db
from . import account
from .forms import UpdateAccountForm
import stripe

@account.route('/my_account', methods=['GET', 'POST'])
@login_required
def my_account():
    """Route to view and edit account details."""
    form = UpdateAccountForm()
    
    if form.validate_on_submit():
        # Update user data
        current_user.name = form.name.data
        current_user.email = form.email.data.lower()
        current_user.phone = form.phone.data
        current_user.building_block = form.building_block.data
        current_user.apartment_number = form.apartment_number.data
        
        try:
            db.session.commit()
            
            # Atualiza o cliente no Stripe
            stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
            stripe.Customer.modify(
                current_user.stripe_customer_id,
                name=current_user.name,
                email=current_user.email,
                phone=current_user.phone
            )
            
            flash('Sua conta foi atualizada com sucesso!', 'success')
            return redirect(url_for('account.my_account'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating account: {e}")
            flash(f'Erro ao atualizar a conta: {e}', 'danger')

    elif request.method == 'GET':
        # Populate form with current user data
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.phone.data = current_user.phone
        form.building_block.data = current_user.building_block
        form.apartment_number.data = current_user.apartment_number
        
    return render_template('account/account.html', title='Minha Conta', form=form)

