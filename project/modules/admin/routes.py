import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_security import login_required, roles_required, current_user
from project.models import User
import logging
from project import db, userDataStore

admin = Blueprint('admin', __name__)

@admin.route('/usuarios')
@login_required
@roles_required('Admin')
def Usuarios():
    usuarios = User.query.all()
    return render_template('/usuarios.html', usuarios=usuarios)

@admin.route('/cambiarRol', methods=['POST'])
@login_required
@roles_required('Admin')
def cambiarRol():
    logging.basicConfig(filename='app.log',level=logging.NOTSET)
    ahora = datetime.datetime.now()
    if request.method == 'POST':
        email = request.form['email']
        rol = request.form['rol']
        if rol == 'Admin':
            rol = userDataStore.find_role('Admin')
        elif rol == 'Cocina':
            rol = userDataStore.find_role('Cocina')
        elif rol == 'Trabajador':
            rol = userDataStore.find_role('Trabajador')
        else:
            rol = userDataStore.find_role('Cliente')
        
        user = User.query.filter_by(email=email).first()
        user.roles = []
        user.roles.append(rol)
        db.session.commit()
        logging.info("El usuario: "+ current_user.email +" ha cambiado el rol del usuario: "+ email +" a: "+ str(rol) +" el: "+ ahora.strftime("%d/%m/%Y") + " a las: " + ahora.strftime("%H:%M:%S"))
        return redirect(url_for('admin.Usuarios'))