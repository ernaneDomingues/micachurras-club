from . import auth
from flask import render_template, redirect, url_for, flash
from .forms import LoginForm # <-- 1. IMPORTAR O NOVO FORMULÁRIO
from mch_app.models import Usuario # (Vamos precisar para verificar o login)
from flask_login import login_user, logout_user, current_user # (Vamos usar em breve)

@auth.route('/login', methods=['GET', 'POST']) # <-- 2. ACEITAR MÉTODOS GET E POST
def login():
    # Se o usuário já estiver logado, não pode ver a página de login
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    form = LoginForm() # <-- 3. CRIAR A INSTÂNCIA DO FORMULÁRIO
    
    if form.validate_on_submit():
        # Lógica de login real
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        
        # Verifica se o usuário existe e se a senha está correta
        if usuario is None or not usuario.check_password(form.password.data):
            flash('Email ou senha inválidos.', 'danger') # 'danger' para uma categoria de erro
            return redirect(url_for('auth.login'))
            
        # Se deu certo, faz o login do usuário
        login_user(usuario, remember=form.remember_me.data)
        flash('Login realizado com sucesso!', 'success') # 'success' para categoria de sucesso
        
        # Redireciona para a página principal
        return redirect(url_for('main.index'))
    
    # 4. PASSAR O FORMULÁRIO PARA O TEMPLATE (para o método GET)
    return render_template('auth/login.html', title='Login', form=form)

@auth.route('/register')
def register():
    # (A lógica de registro virá aqui)
    return "Página de Registro (em breve)"

@auth.route('/logout')
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('main.index'))

