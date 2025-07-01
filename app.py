# app.py

import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename # <<< NOVO: Para segurança dos nomes dos arquivos
from datetime import datetime

# --- CONFIGURAÇÃO DA APLICAÇÃO ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Dtqtt3oKMuioU7RcDbj0lmEicC98OHkw5SBBXS7FXQ9lTbbyakOxQUq'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- CONFIGURAÇÃO DE UPLOAD ---
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads') # <<< NOVO
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} # <<< NOVO
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # <<< NOVO

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça o login para acessar esta página.'


# --- FUNÇÃO AUXILIAR PARA VERIFICAR EXTENSÃO DO ARQUIVO ---
def allowed_file(filename): # <<< NOVO
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# --- MODELOS DO BANCO DE DADOS (SQLAlchemy) ---
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data_evento = db.Column(db.DateTime, nullable=False)
    local = db.Column(db.String(100))
    disponivel = db.Column(db.Boolean, default=True, nullable=False)
    imagem_filename = db.Column(db.String(256), nullable=True) # <<< NOVO: Campo para nome da imagem

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


# --- ROTAS PÚBLICAS (VISITANTES) ---
@app.route('/')
def index():
    # Passa os eventos disponíveis para a tela inicial também
    eventos_disponiveis = Evento.query.filter_by(disponivel=True).order_by(Evento.data_evento.asc()).all()
    return render_template('index.html', eventos=eventos_disponiveis)

@app.route('/eventos')
def eventos():
    eventos_disponiveis = Evento.query.filter_by(disponivel=True).order_by(Evento.data_evento.asc()).all()
    return render_template('eventos.html', eventos=eventos_disponiveis)


# --- ROTAS DE AUTENTICAÇÃO E ADMINISTRAÇÃO ---
# ... (rotas de login, logout e admin_dashboard permanecem as mesmas) ...
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
    todos_eventos = Evento.query.order_by(Evento.data_evento.desc()).all()
    return render_template('admin_dashboard.html', eventos=todos_eventos)


# --- CRUD (Create, Read, Update, Delete) PARA EVENTOS ---

@app.route('/admin/evento/novo', methods=['GET', 'POST'])
@login_required
def novo_evento(): # <<< MODIFICADO
    if request.method == 'POST':
        # Processamento do formulário
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        data_evento_str = request.form['data_evento']
        data_evento = datetime.strptime(data_evento_str, '%Y-%m-%dT%H:%M')
        local = request.form['local']
        disponivel = 'disponivel' in request.form
        
        filename = None
        # Processamento do upload da imagem
        if 'imagem' in request.files:
            imagem = request.files['imagem']
            if imagem.filename != '' and allowed_file(imagem.filename):
                filename = secure_filename(imagem.filename)
                imagem.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        novo = Evento(titulo=titulo, descricao=descricao, data_evento=data_evento, local=local, disponivel=disponivel, imagem_filename=filename)
        db.session.add(novo)
        db.session.commit()
        flash('Evento criado com sucesso!', 'success')
        return redirect(url_for('admin_dashboard'))
        
    return render_template('edit_evento.html', evento=None, acao='Novo')

@app.route('/admin/evento/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_evento(id): # <<< MODIFICADO
    evento = Evento.query.get_or_404(id)
    if request.method == 'POST':
        evento.titulo = request.form['titulo']
        evento.descricao = request.form['descricao']
        data_evento_str = request.form['data_evento']
        evento.data_evento = datetime.strptime(data_evento_str, '%Y-%m-%dT%H:%M')
        evento.local = request.form['local']
        evento.disponivel = 'disponivel' in request.form
        
        # Processamento do upload de uma nova imagem
        if 'imagem' in request.files:
            imagem = request.files['imagem']
            if imagem.filename != '' and allowed_file(imagem.filename):
                filename = secure_filename(imagem.filename)
                # Aqui você pode adicionar lógica para deletar a imagem antiga do disco se desejar
                evento.imagem_filename = filename
                imagem.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        db.session.commit()
        flash('Evento atualizado com sucesso!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_evento.html', evento=evento, acao='Editar')

# ... (rota deletar_evento permanece a mesma) ...
@app.route('/admin/evento/deletar/<int:id>', methods=['POST'])
@login_required
def deletar_evento(id):
    evento = Evento.query.get_or_404(id)
    # Adicionar lógica para deletar o arquivo de imagem do disco se ele existir
    if evento.imagem_filename:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], evento.imagem_filename))
        except OSError as e:
            flash(f"Erro ao deletar arquivo de imagem: {e}", "warning")

    db.session.delete(evento)
    db.session.commit()
    flash('Evento deletado com sucesso!', 'danger')
    return redirect(url_for('admin_dashboard'))

# --- INICIALIZAÇÃO DO APP ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)