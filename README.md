# 🧩 Flask App - Guia de Execução

Este guia apresenta os passos necessários para configurar e executar a aplicação Flask localmente.

---

## ⚙️ Pré-requisitos

- [Python 3.10+](https://www.python.org/downloads/windows/) instalado
- Terminal (CMD, PowerShell ou Terminal do VS Code)
- Git (opcional)

---

## 📦 Instalação e Configuração

### 1️⃣ Instalar o Python

Acesse o link abaixo e instale a versão mais recente do Python para Windows:

👉 [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)

> ✅ **Importante:** durante a instalação, marque a opção **"Add Python to PATH"**.

---

## 2️⃣ Estrutura de Diretórios

Certifique-se de que os seguintes diretórios e arquivos existam no projeto:

📁 tere-verde-online/
├── app.py  
├── static/  
│ └── uploads/ ← Crie essa pasta  
├── instance/  
│ └── database.db ← Crie esse arquivo vazio  
└── ...  
  
---
  
## 3️⃣ Criar e ativar ambiente virtual

No terminal, dentro da pasta do projeto, execute:

```bash
py -m venv venv
venv\Scripts\activate
```
  
---
  
## 4️⃣ Instalar dependências

Com o ambiente virtual ativado, instale os pacotes necessários:

```bash
pip install Flask Flask-SQLAlchemy Flask-Login Werkzeug
```
  
---
  
## 5️⃣ Criar usuário administrador

Ainda com o ambiente virtual ativado, entre no shell interativo do Python:

```bash
python
```

No terminal Python digite cada um dos comandos:

```python
from app import app, db, Admin
app.app_context().push()
db.create_all()
admin = Admin(username='admin')
admin.set_password('Senha da sua escolha')
db.session.add(admin)
db.session.commit()
exit()
```
  
---
  
### 6️⃣ Executar o servidor 

No terminal (com o ambiente virtual ativado), rode:

```bash
python app.py
```

Depois disso abra o navegador e acesse:

```cpp
http://127.0.0.1:5000
```
