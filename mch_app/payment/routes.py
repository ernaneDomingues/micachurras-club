from flask import render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from mch_app import db
from mch_app.models import User, Subscription
from . import payment
import stripe
import json
from datetime import datetime

@payment.route('/plans')
@login_required
def plans():
    """Exibe a página de planos de assinatura."""
    return render_template('payment/planos.html', title='Planos')

@payment.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    """Cria uma sessão de checkout no Stripe."""
    try:
        plan_id = request.form.get('plan_id')
        
        # Carrega os IDs dos planos do config
        price_ids = {
            # Planos Individuais
            'avulso': current_app.config['STRIPE_PRICE_ID_AVULSO'],
            'mensal': current_app.config['STRIPE_PRICE_ID_MENSAL'],
            'anual': current_app.config['STRIPE_PRICE_ID_ANUAL'],
            
            # Planos Casal
            'avulso_casal': current_app.config['STRIPE_PRICE_ID_AVULSO_CASAL'],
            'mensal_casal': current_app.config['STRIPE_PRICE_ID_MENSAL_CASAL'],
        }
        
        price_id_stripe = price_ids.get(plan_id)
        
        if not price_id_stripe:
            flash('Plano inválido selecionado.', 'danger')
            return redirect(url_for('payment.plans'))
            
        # Define o modo de pagamento (avulso vs. assinatura)
        payment_mode = 'subscription' if plan_id in ['mensal', 'anual', 'mensal_casal'] else 'payment'

        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        
        checkout_session = stripe.checkout.Session.create(
            customer=current_user.stripe_customer_id,
            # Deixa o Stripe decidir os métodos de pagamento (PIX, Cartão, Boleto)
            # com base no seu Dashboard: https://dashboard.stripe.com/account/payments/settings
            payment_method_types=None, 
            line_items=[{
                'price': price_id_stripe,
                'quantity': 1,
            }],
            mode=payment_mode,
            success_url=url_for('payment.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('payment.cancel', _external=True),
            # Guarda o ID do plano e do usuário para usar no webhook
            metadata={
                'user_id': current_user.id,
                'plan_name': plan_id
            }
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        current_app.logger.error(f"Erro ao criar sessão do Stripe: {e}")
        flash(f'Erro ao conectar com o sistema de pagamento: {e}', 'danger')
        return redirect(url_for('payment.plans'))

@payment.route('/manage-subscription', methods=['POST'])
@login_required
def manage_subscription():
    """Redireciona o usuário para o Portal do Cliente do Stripe."""
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    try:
        session = stripe.billing_portal.Session.create(
            customer=current_user.stripe_customer_id,
            return_url=url_for('account.my_account', _external=True)
        )
        return redirect(session.url, code=303)
    except Exception as e:
        current_app.logger.error(f"Erro ao criar portal do cliente Stripe: {e}")
        flash(f'Erro ao acessar o portal de assinaturas: {e}', 'danger')
        return redirect(url_for('account.my_account'))

@payment.route('/success')
@login_required
def success():
    """Página de sucesso pós-pagamento."""
    # A lógica de atualização do usuário está no webhook
    flash('Pagamento realizado com sucesso!', 'success')
    return render_template('payment/sucesso.html', title='Sucesso')

@payment.route('/cancel')
@login_required
def cancel():
    """Página de cancelamento de pagamento."""
    flash('O pagamento foi cancelado ou falhou.', 'warning')
    return render_template('payment/cancelado.html', title='Cancelado')

@payment.route('/webhook-stripe', methods=['POST'])
def webhook_stripe():
    """Webhook para receber eventos do Stripe."""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = current_app.config['STRIPE_WEBHOOK_SECRET']
    
    if not endpoint_secret:
        current_app.logger.error("STRIPE_WEBHOOK_SECRET não está configurado.")
        abort(500)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Payload inválido
        current_app.logger.warning(f"Webhook com payload inválido: {e}")
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        # Assinatura inválida
        current_app.logger.warning(f"Webhook com assinatura inválida: {e}")
        return 'Invalid signature', 400

    # --- Processa os eventos ---
    
    # Evento: Pagamento de assinatura bem-sucedido (criada ou renovada)
    if event['type'] == 'invoice.paid':
        session_data = event['data']['object']
        stripe_customer_id = session_data.get('customer')
        stripe_subscription_id = session_data.get('subscription')
        
        # Pega o nome do plano dos metadados (se não estiver, pega da linha de item)
        plan_name = session_data.get('lines', {}).get('data', [{}])[0].get('metadata', {}).get('plan_name')
        if not plan_name and session_data.get('metadata'):
            plan_name = session_data.metadata.get('plan_name')

        if stripe_customer_id:
            user = User.query.filter_by(stripe_customer_id=stripe_customer_id).first()
            if user:
                user.subscription_status = 'ativo'
                user.stripe_subscription_id = stripe_subscription_id
                
                # Atualiza ou cria o registro de assinatura
                sub = Subscription.query.filter_by(user_id=user.id).first()
                if not sub:
                    sub = Subscription(user_id=user.id)
                
                sub.plan_name = plan_name or 'desconhecido'
                sub.status = 'ativo'
                sub.start_date = datetime.utcnow()
                # Pega a data de fim do período do Stripe (convertendo de timestamp)
                if session_data.get('period_end'):
                    sub.end_date = datetime.fromtimestamp(session_data.period_end)
                
                db.session.add(sub)
                db.session.commit()
                current_app.logger.info(f"Assinatura ativada para {user.email}")
    
    # Evento: Assinatura cancelada ou período finalizado
    elif event['type'] == 'customer.subscription.deleted' or event['type'] == 'customer.subscription.updated':
        session_data = event['data']['object']
        stripe_customer_id = session_data.get('customer')
        
        # Se a assinatura for cancelada ou não estiver mais ativa
        if session_data.status != 'active':
            user = User.query.filter_by(stripe_customer_id=stripe_customer_id).first()
            if user:
                user.subscription_status = 'inativo'
                sub = Subscription.query.filter_by(user_id=user.id).first()
                if sub:
                    sub.status = 'inativo'
                db.session.commit()
                current_app.logger.info(f"Assinatura desativada para {user.email}")

    # Evento: Pagamento único (Passe Avulso) bem-sucedido
    elif event['type'] == 'checkout.session.completed':
        session_data = event['data']['object']
        if session_data.mode == 'payment':
            stripe_customer_id = session_data.get('customer')
            user_id = session_data.get('metadata', {}).get('user_id')
            plan_name = session_data.get('metadata', {}).get('plan_name')
            
            # Aqui você adicionaria a lógica para o passe avulso
            # Ex: Criar um RSVP para o próximo evento
            current_app.logger.info(f"Pagamento avulso recebido do user_id {user_id} para o plano {plan_name}")
            # (Lógica futura de RSVP)
            
    else:
        current_app.logger.info(f"Evento Stripe não tratado: {event['type']}")

    return 'OK', 200

