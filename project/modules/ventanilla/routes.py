import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_security import login_required, roles_accepted, current_user
from project.models import User, Pan, carritoVentanilla, ventaLocal, Pan_VentaL
from project import db
import logging

ventanilla = Blueprint('ventanilla', __name__)

@ventanilla.route('/Ventanilla')
@login_required
@roles_accepted('Admin', 'Trabajador')
def Ventanilla():
    panes = Pan.query.filter_by(estatus=1).all()
    carrito = carritoVentanilla.query.all()
    panesCarrito =[]
    total = 0
    for item in carrito:
        pan = Pan.query.filter_by(id=item.id_pan).first()
        pan.cantidad = item.cantidad
        pan.total = item.total
        total += pan.total
        panesCarrito.append(pan)
    
    return render_template('ventanilla.html', panes=panes, panesCarrito=panesCarrito, total=total)

@ventanilla.route('/addCarritoV', methods=['POST'])
@login_required
@roles_accepted('Admin', 'Trabajador')
def addCarrito():
    id_pan = request.form['txtId']
    cantidad = request.form['txtCant']
    panExist = carritoVentanilla.query.filter_by(id_pan=id_pan).first()
    pan = Pan.query.filter_by(id=id_pan).first()
    vd = 0
    if panExist:
        panExist.cantidad = cantidad
        panExist.total = pan.precio * int(panExist.cantidad)
        db.session.commit()
        vd = 1
        
    if vd == 0:
        total = pan.precio * int(cantidad)
        carrito = carritoVentanilla(id_pan=id_pan, cantidad=cantidad, total=total)
        db.session.add(carrito)
        db.session.commit()
    return redirect(url_for('ventanilla.Ventanilla'))

@ventanilla.route('/removeFromCarritoV')
@login_required
@roles_accepted('Admin', 'Trabajador')
def deleteCarrito():
    id_pan = request.args.get('id')
    carrito = carritoVentanilla.query.filter_by(id_pan=id_pan).first()
    db.session.delete(carrito)
    db.session.commit()

    return redirect(url_for('ventanilla.Ventanilla'))

@ventanilla.route('/confirmarVenta', methods=['POST'])
@login_required
@roles_accepted('Admin', 'Trabajador')
def confirmarVenta():
    logging.basicConfig(filename='app.log',level=logging.NOTSET)
    ahora = datetime.datetime.now()
    carrito = carritoVentanilla.query.all()
    panes = []
    total = 0
    for item in carrito:
        pan = Pan.query.filter_by(id=item.id_pan).first()
        if pan.inventario < item.cantidad:
            flash("No hay suficiente cantidad de "+pan.nombre+" en inventario", "error")
            return redirect(url_for('ventanilla.Ventanilla'))
        else:
            pan.inventario = pan.inventario - item.cantidad
            db.session.commit()
        pan.cantidad = item.cantidad
        pan.total = item.total
        panes.append(pan)
        total += pan.total
    
    now = datetime.datetime.now()
    venta = ventaLocal(fecha=now, total=total)
    db.session.add(venta)
    db.session.commit()

    vent = ventaLocal.query.order_by(ventaLocal.id.desc()).first()
    
    for item in panes:
        panVenta = Pan_VentaL(id_venta=vent.id, id_pan=item.id, cantidad=item.cantidad, total=item.total)
        db.session.add(panVenta)
        db.session.commit()
    
    for item in carrito:
        db.session.delete(item)
        db.session.commit()

    logging.info("Venta realizada en ventanilla por "+current_user.email+" el "+ahora.strftime("%d/%m/%Y")+" a las "+ahora.strftime("%H:%M"))
    return redirect(url_for('ventanilla.Ventanilla'))


@ventanilla.route('/HistorialVentas')
@login_required
@roles_accepted('Admin', 'Trabajador')
def HistorialVentas():
    ventas = ventaLocal.query.all()
    panesVentas = Pan_VentaL.query.all()
    pans = Pan.query.all()
    panes = []
    
    for venta in ventas:
        for pan in panesVentas:
            if venta.id == pan.id_venta:
                for p in pans:
                    if pan.id_pan == p.id:
                        nPan = {"id":p.id, "nombre":p.nombre, "precio":p.precio, "cantidad":pan.cantidad, "venta":venta.id}
                        panes.append(nPan)

    for venta in ventas:
        fecha = venta.fecha
        fechaDepurada = fecha.strftime("%d/%m/%Y") +" - "+ fecha.strftime("%H:%M")
        venta.fecha = fechaDepurada

    ventas.reverse()
    return render_template('historialVentas.html', ventas=ventas, panes=panes)
        