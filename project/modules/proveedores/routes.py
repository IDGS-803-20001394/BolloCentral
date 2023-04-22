import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_security import login_required, roles_accepted, current_user
from project.models import User, Proveedor, MateriaPrima, Provision
from project import db
import logging

proveedores = Blueprint('proveedores', __name__)

@proveedores.route('/Proveedores')
@login_required
@roles_accepted('Admin', 'Trabajador')
def Proveedores():
    proveedores = Proveedor.query.filter_by(estatus=1).all()
    materias = MateriaPrima.query.all()
    return render_template('proveedores.html', proveedores=proveedores, materias=materias)

@proveedores.route('/NuevoProveedor', methods=['GET', 'POST'])
@login_required
@roles_accepted('Admin', 'Trabajador')
def NuevoProveedor():
    logging.basicConfig(filename='app.log',level=logging.NOTSET)
    ahora = datetime.datetime.now()
    materias = MateriaPrima.query.all()
    materias.sort(key=lambda x: x.nombre)
    if request.method == 'POST':
        nombre = request.form['txtNombre']
        telefono = request.form['txtTelefono']
        empresa = request.form['txtEmpresa']
        producto = request.form['txtProducto']
        precio = request.form['txtPrecio']
        direccion = request.form['txtDirección']
        correo = request.form['txtCorreo']

        newProveedor = Proveedor(nombre=nombre, telefono=telefono, empresa=empresa, producto=producto, costoProducto=precio, direccion=direccion, email=correo, estatus=1)
        db.session.add(newProveedor)
        db.session.commit()
        logging.info("El usuario: "+ current_user.email +" ha agregado el nuevo proveedor: "+ nombre +" el: "+ ahora.strftime("%d/%m/%Y") + " a las: " + ahora.strftime("%H:%M:%S"))
        return redirect(url_for('proveedores.Proveedores'))

    return render_template('agregarProveedor.html', materias=materias)

@proveedores.route('/ModificarProveedor', methods=['GET', 'POST'])
@login_required
@roles_accepted('Admin', 'Trabajador')
def ModificarProveedor():
    logging.basicConfig(filename='app.log',level=logging.NOTSET)
    ahora = datetime.datetime.now()
    materias = MateriaPrima.query.all()
    if request.method == 'POST':
        id = request.form['txtId']
        nombre = request.form['txtNombre']
        telefono = request.form['txtTelefono']
        empresa = request.form['txtEmpresa']
        producto = request.form['txtProducto']
        direccion = request.form['txtDirección']
        correo = request.form['txtCorreo']
        precio = request.form['txtPrecio']

        proveedor = Proveedor.query.filter_by(id=id).first()
        proveedor.nombre = nombre
        proveedor.telefono = telefono
        proveedor.empresa = empresa
        proveedor.producto = producto
        proveedor.direccion = direccion
        proveedor.costoProducto = precio
        proveedor.email = correo
        db.session.commit()
        logging.info("El usuario: "+ current_user.email +" ha modificado el proveedor: "+ nombre +" el: "+ ahora.strftime("%d/%m/%Y") + " a las: " + ahora.strftime("%H:%M:%S"))
        return redirect(url_for('proveedores.Proveedores'))

    id = request.args.get('id')
    proveedor = Proveedor.query.filter_by(id=id).first()
    return render_template('modificarProveedor.html', proveedor=proveedor, materias=materias)

@proveedores.route('/EliminarProveedor', methods=['GET', 'POST'])
@login_required
@roles_accepted('Admin', 'Trabajador')
def EliminarProveedor():
    logging.basicConfig(filename='app.log',level=logging.NOTSET)
    ahora = datetime.datetime.now()
    if request.method == 'POST':
        id = request.form['txtId']
        proveedor = Proveedor.query.filter_by(id=id).first()
        proveedor.estatus = 0
        db.session.commit()
        logging.info("El usuario: "+ current_user.email +" ha desactivado el proveedor: "+ proveedor.nombre +" el: "+ ahora.strftime("%d/%m/%Y") + " a las: " + ahora.strftime("%H:%M:%S"))
        return redirect(url_for('proveedores.Proveedores'))

    id = request.args.get('id')
    proveedor = Proveedor.query.filter_by(id=id).first()
    materias = MateriaPrima.query.all()
    return render_template('eliminarProveedor.html', proveedor=proveedor, materias=materias)

@proveedores.route('/RealizarProvision', methods=['GET', 'POST'])
@login_required
@roles_accepted('Admin', 'Trabajador')
def ComprarProvisiones():
    id = request.args.get('id')
    proveedor = Proveedor.query.filter_by(id=id).first()
    materia = MateriaPrima.query.filter_by(id=proveedor.producto).first()
    if request.method == 'POST':
        id = request.args.get('id')
        cantidad = request.form['txtCantidad']
        proveedor = Proveedor.query.filter_by(id=id).first()
        materia = MateriaPrima.query.filter_by(id=proveedor.producto).first()
        total = proveedor.costoProducto * int(cantidad)
        total = round(total, 2)
        return render_template('confirmarProvision.html', proveedor=proveedor, materia=materia, cantidad=cantidad, total=total)
    
    return render_template('comprarProvisiones.html', proveedor=proveedor, materia=materia)

@proveedores.route('/ConfirmarPedido', methods=['POST'])
@login_required
@roles_accepted('Admin', 'Trabajador')
def ConfirmarPedido():
    logging.basicConfig(filename='app.log',level=logging.NOTSET)
    ahora = datetime.datetime.now()
    id = request.form['txtId']
    cantidad = request.form['txtCantidad']
    proveedor = Proveedor.query.filter_by(id=id).first()
    materia = MateriaPrima.query.filter_by(id=proveedor.producto).first()
    total = proveedor.costoProducto * int(cantidad)
    now = datetime.datetime.now()
    newProvision = Provision(id_proveedor=id, id_materia=proveedor.producto, cantidad=cantidad, costoTotal=total, fechaPedido=now, estatus="Pendiente")
    db.session.add(newProvision)
    db.session.commit()
    logging.info("El usuario: "+ current_user.email +" ha realizado un pedido de: "+ cantidad+""+materia.unidad +" de "+ materia.nombre +" al proveedor: "+ proveedor.nombre +" el: "+ ahora.strftime("%d/%m/%Y") + " a las: " + ahora.strftime("%H:%M:%S"))
    return redirect(url_for('proveedores.Provisiones'))
    
@proveedores.route('/Provisiones')
@login_required
@roles_accepted('Admin', 'Trabajador')
def Provisiones():
    provisiones = Provision.query.all()
    proveedores = Proveedor.query.all()
    materias = MateriaPrima.query.all()
    pendientes = False
    for provision in provisiones:
        if provision.estatus == "Pendiente":
            pendientes = True
            break
        fecha1 = provision.fechaPedido
        fechaDepurada1 = fecha1.strftime("%d/%m/%Y")
        provision.fechaPedido = fechaDepurada1
        fecha2 = provision.fechaEntrega
        if fecha2 != None:
            fechaDepurada2 = fecha2.strftime("%d/%m/%Y")
            provision.fechaEntrega = fechaDepurada2
    
    return render_template('provisiones.html', provisiones=provisiones, proveedores=proveedores, materias=materias,  pendientes=pendientes)

@proveedores.route('/recibirProvision')
@login_required
@roles_accepted('Admin', 'Trabajador')
def RecibirProvision():
    logging.basicConfig(filename='app.log',level=logging.NOTSET)
    ahora = datetime.datetime.now()
    id = request.args.get('id')
    provision = Provision.query.filter_by(id=id).first()
    provision.estatus = "Recibido"
    provision.fechaEntrega = datetime.datetime.now()
    materia = MateriaPrima.query.filter_by(id=provision.id_materia).first()
    materia.inventario = materia.inventario + provision.cantidad
    db.session.commit()
    logging.info("El usuario: "+ current_user.email +" ha confirmado el recibimiento del pedido de: "+ str(provision.cantidad)+""+materia.unidad +" de "+ materia.nombre +" al proveedor: "+ str(provision.id_proveedor) +" el: "+ ahora.strftime("%d/%m/%Y") + " a las: " + ahora.strftime("%H:%M:%S"))
    return redirect(url_for('proveedores.Provisiones'))