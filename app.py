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
