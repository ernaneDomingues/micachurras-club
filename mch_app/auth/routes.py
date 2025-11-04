from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user
from mch_app import db
from . import auth
from .forms import LoginForm, RegistrationForm
from mch_app.models import User
import stripe

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Login route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is None or not user.check_password(form.password.data):
            flash('Email ou senha inválidos.', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        flash('Login realizado com sucesso!', 'success')
        
        # Redirect to the next page if it exists
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.index')
        return redirect(next_page)
        
    return render_template('auth/login.html', title='Login', form=form)

@auth.route('/logout')
def logout():
    """Logout route."""
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Registration route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Set Stripe API key
            stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
            
            # Create a new Customer object in Stripe
            customer = stripe.Customer.create(
                name=form.name.data,
                email=form.email.data.lower(),
                phone=form.phone.data
            )
            
            # Create new user in local database
            user = User(
                name=form.name.data,
                email=form.email.data.lower(),
                birth_date=form.birth_date.data,
                phone=form.phone.data,
                building_block=form.building_block.data,
                apartment_number=form.apartment_number.data,
                stripe_customer_id=customer.id  # Save the Stripe Customer ID
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Cadastro realizado com sucesso! Faça o login.', 'success')
            return redirect(url_for('auth.login'))
        
        except stripe.error.StripeError as e:
            db.session.rollback()
            current_app.logger.error(f"Stripe error during registration: {e}")
            flash(f'Erro ao criar cliente de pagamento: {e}', 'danger')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Generic error during registration: {e}")
            flash(f'Erro ao registrar: {e}', 'danger')
            
    return render_template('auth/register.html', title='Registrar', form=form)

