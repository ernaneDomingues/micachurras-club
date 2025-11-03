from flask import render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from mch_app import db
from . import payment
from mch_app.models import User, Subscription
import stripe
from datetime import datetime

@payment.route('/plans')
@login_required
def plans():
    """Mostra a página de seleção de planos."""
    return render_template('payment/planos.html', title='Nossos Planos')

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
            
            # --- NOVOS PLANOS CASAL ---
            'avulso_casal': current_app.config['STRIPE_PRICE_ID_AVULSO_CASAL'],
            'mensal_casal': current_app.config['STRIPE_PRICE_ID_MENSAL_CASAL'],
            # (Você pode adicionar um 'anual_casal' aqui no futuro)
        }
        
        price_id_stripe = price_ids.get(plan_id)
        if not price_id_stripe:
            flash('Plano inválido selecionado.', 'danger')
            return redirect(url_for('payment.plans'))
            
        # Define o modo de pagamento (avulso vs. assinatura)
        payment_mode = 'subscription' if plan_id in ['mensal', 'anual', 'mensal_casal'] else 'payment'

        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        
        session = stripe.checkout.Session.create(
            customer=current_user.stripe_customer_id,
            #
            # --- ATUALIZAÇÃO ---
            # Removemos a linha 'payment_method_types'
            # O Stripe agora mostrará automaticamente os métodos
            # que você ativou no seu Dashboard (Cartão, Boleto, PIX, etc.)
            #
            line_items=[{
                'price': price_id_stripe,
                'quantity': 1,  # A 'quantity' é 1, pois o PREÇO do Stripe já é para o casal
            }],
            mode=payment_mode,
            success_url=url_for('payment.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('payment.cancel', _external=True),
            # Habilita o portal do cliente
            customer_update={'name': 'auto', 'address': 'auto'},
        )
        return redirect(session.url, code=303)
    
    except Exception as e:
        # Adiciona um log do erro para debugging
        current_app.logger.error(f"Erro ao criar sessão Stripe: {e}")
        flash(f'Erro ao criar sessão de pagamento: {e}', 'danger')
        return redirect(url_for('payment.plans'))

@payment.route('/manage-subscription', methods=['POST'])
@login_required
def manage_subscription():
    """Redireciona o usuário para o Portal do Cliente Stripe."""
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    
    try:
        session = stripe.billing_portal.Session.create(
            customer=current_user.stripe_customer_id,
            return_url=url_for('account.my_account', _external=True)
        )
        return redirect(session.url, code=303)
    except Exception as e:
        # Adiciona um log do erro para debugging
        current_app.logger.error(f"Erro ao acessar portal Stripe: {e}")
        flash(f'Erro ao acessar o portal de assinaturas: {e}', 'danger')
        return redirect(url_for('account.my_account'))


@payment.route('/success')
@login_required
def success():
    """Página de sucesso após o pagamento."""
    # O Webhook é a forma segura de atualizar o BD,
    # mas podemos dar um feedback imediato (otimista) aqui.
    session_id = request.args.get('session_id')
    if not session_id:
        flash('Sessão de pagamento inválida.', 'warning')
        return redirect(url_for('main.index'))
    
    # Você poderia buscar a sessão aqui para dar um feedback mais rico,
    # mas vamos manter simples por enquanto.
    flash('Pagamento realizado com sucesso! Bem-vindo ao clube.', 'success')
    return render_template('payment/sucesso.html', title='Sucesso')

@payment.route('/cancel')
@login_required
def cancel():
    """Página de cancelamento de pagamento."""
    flash('O processo de pagamento foi cancelado.', 'warning')
    return render_template('payment/cancelado.html', title='Cancelado')

@payment.route('/webhook-stripe', methods=['POST'])
def stripe_webhook():
    """Ouve os eventos do Stripe (pagamentos, assinaturas)."""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = current_app.config['STRIPE_WEBHOOK_SECRET']

    if not endpoint_secret:
        current_app.logger.error("STRIPE_WEBHOOK_SECRET não está configurado.")
        return abort(500)
        
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

    # --- Manipula os eventos do Stripe ---
    
    try:
        # Evento: Sessão de checkout concluída
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            customer_id = session.get('customer')
            subscription_id = session.get('subscription')
            
            user = User.query.filter_by(stripe_customer_id=customer_id).first()
            if not user:
                current_app.logger.error(f"Webhook: Usuário não encontrado para customer_id {customer_id}")
                return 'User not found', 404

            if subscription_id:
                # É uma assinatura
                sub_data = stripe.Subscription.retrieve(subscription_id)
                plan_nickname = sub_data.get('items', {}).get('data', [{}])[0].get('price', {}).get('nickname')
                
                # Deleta assinatura antiga se houver
                Subscription.query.filter_by(user_id=user.id).delete()
                
                # Cria nova assinatura
                new_sub = Subscription(
                    user_id=user.id,
                    plan_name=plan_nickname or 'Assinatura', # Usa o 'Nickname' do plano no Stripe
                    status='ativo',
                    start_date=datetime.fromtimestamp(sub_data.current_period_start),
                    end_date=datetime.fromtimestamp(sub_data.current_period_end)
                )
                db.session.add(new_sub)
                
                # Atualiza o status do usuário
                user.stripe_subscription_id = subscription_id
                user.subscription_status = 'ativo'
                
            else:
                # É um pagamento avulso (RSVP)
                # TODO: Implementar lógica de RSVP para pagamento avulso
                # Ex: Encontrar o evento, criar um RSVP
                current_app.logger.info(f"Pagamento avulso recebido de {user.email}. Lógica de RSVP pendente.")
                pass

            db.session.commit()

        # Evento: Fatura paga (renovação de assinatura)
        elif event['type'] == 'invoice.paid':
            invoice = event['data']['object']
            customer_id = invoice.get('customer')
            subscription_id = invoice.get('subscription')

            user = User.query.filter_by(stripe_customer_id=customer_id).first()
            if user and subscription_id:
                sub = Subscription.query.filter_by(user_id=user.id).first()
                if sub:
                    sub_data = stripe.Subscription.retrieve(subscription_id)
                    sub.status = 'ativo'
                    sub.start_date = datetime.fromtimestamp(sub_data.current_period_start)
                    sub.end_date = datetime.fromtimestamp(sub_data.current_period_end)
                    user.subscription_status = 'ativo'
                    db.session.commit()

        # Evento: Falha na fatura (assinatura vencida)
        elif event['type'] == 'invoice.payment_failed':
            invoice = event['data']['object']
            customer_id = invoice.get('customer')
            
            user = User.query.filter_by(stripe_customer_id=customer_id).first()
            if user:
                user.subscription_status = 'inativo' # ou 'vencido'
                sub = Subscription.query.filter_by(user_id=user.id).first()
                if sub:
                    sub.status = 'inativo'
                db.session.commit()
        
        else:
            current_app.logger.info(f"Webhook recebido (não manipulado): {event['type']}")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao processar webhook {event['type']}: {e}")
        return f'Erro interno no processamento do webhook: {e}', 500

    return 'OK', 200


