import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_security import login_required
from flask_security.utils import login_user, logout_user   
from project.models import User
from project import db, userDataStore
import logging

auth = Blueprint('auth', __name__, url_prefix='/security')

@auth.route('/login')
def Login():
    return render_template('/security/login.html')

@auth.route("/login", methods=["POST"])
def Login_post():
    logging.basicConfig(filename='app.log',level=logging.NOTSET)
    ahora = datetime.datetime.now()
    email = request.form.get("email")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash('El usuario y/o la contraseña son incorrectos.')
        logging.warning('Error al iniciar sesion con el correo: ' + email + ' el: ' + ahora.strftime("%d/%m/%Y") + ' a las: ' + ahora.strftime("%H:%M:%S"))
        return redirect(url_for('auth.Login'))
    
    login_user(user, remember=remember)
    logging.info('Inicio de sesion con el correo: ' + email + ' el: ' + ahora.strftime("%d/%m/%Y") + ' a las: ' + ahora.strftime("%H:%M:%S"))
    return redirect(url_for('main.index'))

@auth.route('/register')
def Registro():
    return render_template('/security/register.html')

@auth.route("/register", methods=["POST"])
def Registro_post():
    logging.basicConfig(filename='app.log',level=logging.NOTSET)
    ahora = datetime.datetime.now()

    email = request.form.get("email")
    name = request.form.get("name")
    password = request.form.get("password")
    direccion = request.form.get("direccion")
    telefono = request.form.get("telefono")

    if not email or not name or not password:
        flash('Por favor, rellene todos los campos.')
        return redirect(url_for('auth.Registro'))

    user = User.query.filter_by(email=email).first()

    if user:
        flash('El correo electronico ya existe, intente con otro')
        return redirect(url_for('auth.Registro'))

    userDataStore.create_user(name=name, email=email, password=generate_password_hash(password, method='sha256'), direccion=direccion, telefono=telefono)
    db.session.commit()

    logging.info('Registro de cuenta con el correo: ' + email + ' el: ' + ahora.strftime("%d/%m/%Y") + ' a las: ' + ahora.strftime("%H:%M:%S"))
    return redirect(url_for('auth.Login'))

@auth.route('/logout')
@login_required
def Logout():
    logout_user()
    return redirect(url_for('main.index'))
