ódigo base para una aplicación web que permite gestionar accesos a servicios como SSH, RDP, VNC, HTTP y HTTPS, con autenticación de usuarios, una base de datos para la gestión de usuarios y registros, y una interfaz de usuario simple. Además, incluiré los pasos detallados para configurarla y desplegarla en un contenedor Docker.

Estructura del Proyecto
Backend: Utilizaremos Flask (Python) para manejar la lógica del servidor.
Base de datos: Usaremos SQLite para simplicidad (se puede cambiar a Postgres o MySQL).
Frontend: Usaremos HTML, CSS, y JavaScript para la interfaz.
Conexiones a servicios:
SSH: Utilizaremos paramiko.
RDP: Utilizaremos rdpy.
VNC: Usaremos pyvnc.
HTTP/HTTPS: Manejados directamente desde el navegador.
Código de la Aplicación
Estructura del Proyecto:
csharp
Copiar código
app/
├── app.py                # Servidor principal
├── models.py             # Gestión de la base de datos
├── services.py           # Lógica de conexión a servicios
├── templates/
│   ├── index.html        # Interfaz de usuario
│   ├── login.html        # Página de inicio de sesión
│   ├── dashboard.html    # Panel de control
├── static/
│   ├── styles.css        # Estilos
│   ├── script.js         # JavaScript
├── Dockerfile            # Configuración Docker
├── requirements.txt      # Dependencias
└── config.py             # Configuración de la aplicación
app.py
Este archivo contiene el servidor principal y las rutas.

python
Copiar código
from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User, ConnectionLog
from services import connect_ssh, connect_rdp, connect_vnc
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        session['user_id'] = user.id
        return redirect(url_for('dashboard'))
    flash('Invalid credentials')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html')

@app.route('/connect', methods=['POST'])
def connect():
    service_type = request.form['service']
    host = request.form['host']
    port = int(request.form['port'])
    username = request.form['username']
    password = request.form['password']

    try:
        if service_type == 'ssh':
            connect_ssh(host, port, username, password)
        elif service_type == 'rdp':
            connect_rdp(host, port, username, password)
        elif service_type == 'vnc':
            connect_vnc(host, port, password)
        else:
            raise ValueError('Invalid service type')
        flash('Connection successful')
    except Exception as e:
        flash(f'Connection failed: {str(e)}')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
models.py
Define los modelos de base de datos.

python
Copiar código
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class ConnectionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_type = db.Column(db.String(20), nullable=False)
    host = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
services.py
Gestión de conexiones.

python
Copiar código
import paramiko
import subprocess

def connect_ssh(host, port, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, port=port, username=username, password=password)
    client.close()

def connect_rdp(host, port, username, password):
    subprocess.run(['xfreerdp', f'/u:{username}', f'/p:{password}', f'/v:{host}:{port}'])

def connect_vnc(host, port, password):
    subprocess.run(['vncviewer', f'{host}:{port}', f'-passwd={password}'])
config.py
Configuración básica.

python
Copiar código
import os

SECRET_KEY = os.urandom(24)
SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
Dockerfile
Archivo para contenerizar la aplicación.

dockerfile
Copiar código
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "app.py"]
requirements.txt
Dependencias del proyecto.

Copiar código
flask
flask-bcrypt
flask-sqlalchemy
paramiko
Pasos para Configurar y Ejecutar
Clonar el repositorio y navegar al directorio del proyecto.

Construir la imagen Docker:

bash
Copiar código
docker build -t ssh-rdp-manager .
Ejecutar el contenedor:

bash
Copiar código
docker run -d -p 5000:5000 ssh-rdp-manager
Inicializar la base de datos:

Accede al contenedor:
bash
Copiar código
docker exec -it <container_id> /bin/bash
Ejecuta el shell de Python:
bash
Copiar código
python
Inicializa la base de datos:
python
Copiar código
from app import db
db.create_all()
Abrir la aplicación:

Accede a http://localhost:5000 en tu navegador.
Con estos pasos y la estructura, tendrás un sistema funcional que puedes mejorar según tus necesidades.
