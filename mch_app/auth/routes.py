from . import auth
from flask import render_template, redirect, url_for, flash
from .forms import LoginForm, RegistrationForm # <-- 1. IMPORTAR REGISTRATIONFORM
from mch_app.models import Usuario
from flask_login import login_user, logout_user, current_user
from mch_app import db # <-- 2. IMPORTAR A INSTÂNCIA DO BANCO

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    form = LoginForm()
    
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        
        if usuario is None or not usuario.check_password(form.password.data):
            flash('Email ou senha inválidos.', 'danger') 
            return redirect(url_for('auth.login'))
            
        login_user(usuario, remember=form.remember_me.data)
        flash('Login realizado com sucesso!', 'success')
        
        return redirect(url_for('main.index'))
    
    return render_template('auth/login.html', title='Login', form=form)

@auth.route('/register', methods=['GET', 'POST']) # <-- 3. ATUALIZAR ROTA
def register():
    # Se o usuário já estiver logado, não pode ver a página de registro
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    form = RegistrationForm() # <-- 4. USAR O NOVO FORMULÁRIO
    
    if form.validate_on_submit():
        # Cria o novo usuário
        usuario = Usuario(
            nome=form.nome.data,
            email=form.email.data,
            # <-- CAMPOS ADICIONADOS -->
            data_nascimento=form.data_nascimento.data,
            telefone=form.telefone.data,
            bloco=form.bloco.data,
            apartamento=form.apartamento.data
            # <-- FIM DOS CAMPOS ADICIONADOS -->
        )
        usuario.set_password(form.password.data) # <-- 5. SETAR A SENHA (HASH)
        
        # Salvar no banco
        db.session.add(usuario)
        db.session.commit() # <-- 6. SALVAR MUDANÇAS
        
        flash('Conta criada com sucesso! Você já pode fazer o login.', 'success')
        
        # Loga o usuário automaticamente após o registro
        login_user(usuario)
        
        return redirect(url_for('main.index')) # <-- 7. REDIRECIONAR
    
    # Se for GET ou se a validação falhar, renderiza o template
    return render_template('auth/register.html', title='Registro', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('main.index'))


