# app.py

import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# --- CONFIGURAÇÃO DA APLICAÇÃO ---
app = Flask(__name__)
# Chave secreta para segurança das sessões
app.config['SECRET_KEY'] = '!:\G"pZ1rvqk:GQck*yl-EGlKE(L8=UR|TUi6qMkmhL|T]5T,9bmJO=)9xVAfqi'
# Configuração do caminho do banco de dados
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Redireciona usuários não logados para a tela de login
login_manager.login_message = 'Por favor, faça o login para acessar esta página.'

# --- MODELOS DO BANCO DE DADOS (SQLAlchemy) ---

# Modelo para Administradores
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        # Gera um hash seguro para a senha e o armazena
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # Verifica se a senha fornecida corresponde ao hash armazenado
        return check_password_hash(self.password_hash, password)

# Modelo para Eventos (pode ser adaptado para trilhas, temporadas, etc.)
class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data_evento = db.Column(db.DateTime, nullable=False)
    local = db.Column(db.String(100))
    disponivel = db.Column(db.Boolean, default=True, nullable=False)

# Função para carregar o usuário da sessão
@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# --- ROTAS PÚBLICAS (VISITANTES) ---

@app.route('/')
def index():
    # Exibe a página inicial
    return render_template('index.html')

@app.route('/eventos')
def eventos():
    # Busca todos os eventos disponíveis no banco de dados
    eventos_disponiveis = Evento.query.filter_by(disponivel=True).order_by(Evento.data_evento.asc()).all()
    return render_template('eventos.html', eventos=eventos_disponiveis)

# --- ROTAS DE AUTENTICAÇÃO E ADMINISTRAÇÃO ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            login_user(admin)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    # Painel que lista todos os eventos para edição
    todos_eventos = Evento.query.order_by(Evento.data_evento.desc()).all()
    return render_template('admin_dashboard.html', eventos=todos_eventos)

# --- CRUD (Create, Read, Update, Delete) PARA EVENTOS ---

@app.route('/admin/evento/novo', methods=['GET', 'POST'])
@login_required
def novo_evento():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        # Converte a string da data do formulário para um objeto datetime
        data_evento_str = request.form['data_evento']
        data_evento = datetime.strptime(data_evento_str, '%Y-%m-%dT%H:%M')
        local = request.form['local']
        disponivel = 'disponivel' in request.form

        novo = Evento(titulo=titulo, descricao=descricao, data_evento=data_evento, local=local, disponivel=disponivel)
        db.session.add(novo)
        db.session.commit()
        flash('Evento criado com sucesso!', 'success')
        return redirect(url_for('admin_dashboard'))
        
    # Passa um evento vazio e a ação para o template
    return render_template('edit_evento.html', evento=None, acao='Novo')

@app.route('/admin/evento/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_evento(id):
    evento = Evento.query.get_or_404(id)
    if request.method == 'POST':
        evento.titulo = request.form['titulo']
        evento.descricao = request.form['descricao']
        data_evento_str = request.form['data_evento']
        evento.data_evento = datetime.strptime(data_evento_str, '%Y-%m-%dT%H:%M')
        evento.local = request.form['local']
        evento.disponivel = 'disponivel' in request.form
        
        db.session.commit()
        flash('Evento atualizado com sucesso!', 'success')
        return redirect(url_for('admin_dashboard'))

    # Passa o evento existente e a ação para o template
    return render_template('edit_evento.html', evento=evento, acao='Editar')

@app.route('/admin/evento/deletar/<int:id>', methods=['POST'])
@login_required
def deletar_evento(id):
    evento = Evento.query.get_or_404(id)
    db.session.delete(evento)
    db.session.commit()
    flash('Evento deletado com sucesso!', 'danger')
    return redirect(url_for('admin_dashboard'))

# --- INICIALIZAÇÃO DO APP ---
if __name__ == '__main__':
    with app.app_context():
        # Cria as tabelas do banco de dados se não existirem
        db.create_all()
    app.run(debug=True) # debug=True apenas para desenvolvimento