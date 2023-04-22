import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user
from flask_security import login_required
from project.models import User, Pan, Carrito, Pedido, Pan_Pedido
from project import db
import logging

clientes = Blueprint('clientes', __name__)

@clientes.route('/Catalogo')
@login_required
def Catalogo():
    panes = Pan.query.filter_by(estatus=1).all()
    return render_template('catalogo.html', panes=panes)

@clientes.route('/addCarrito', methods=['POST'])
@login_required
def addCarrito():
    id_pan = request.form['txtId']
    cantidad = request.form['txtCant']
    panExist = Carrito.query.filter_by(id_usuario=current_user.id, id_pan=id_pan).first()
    pan = Pan.query.filter_by(id=id_pan).first()
    vd = 0
    if panExist:
        panExist.cantidad = cantidad
        panExist.total = pan.precio * int(panExist.cantidad)
        db.session.commit()
        vd = 1
    
    if vd == 0:
        total = pan.precio * int(cantidad)
        carrito = Carrito(id_pan=id_pan, id_usuario=current_user.id, cantidad=cantidad, total=total)
        db.session.add(carrito)
        db.session.commit()
    flash('Se ha agregado el pan al carrito')
    return redirect(url_for('clientes.Catalogo'))

@clientes.route('/Carrito')
@login_required
def Cart():
    carrito = Carrito.query.filter_by(id_usuario=current_user.id).all()
    panes = []
    total = 0
    cantTotal = 0
    envio = 30
    for item in carrito:
        pan = Pan.query.filter_by(id=item.id_pan).first()
        pan.cantidad = item.cantidad
        pan.total = item.total
        panes.append(pan)
        total += pan.total
        cantTotal += pan.cantidad
    
    if cantTotal >= 50 or cantTotal == 0:
        envio = 0
    
    total += envio

    return render_template('carrito.html', panes=panes, total=total, envio=envio)

@clientes.route('/removeFromCarrito')
@login_required
def deleteCarrito():
    id_pan = request.args.get('id')

    carrito = Carrito.query.filter_by(id_usuario=current_user.id, id_pan=id_pan).first()
    db.session.delete(carrito)
    db.session.commit()

    return redirect(url_for('clientes.Cart'))  

@clientes.route('/realizarPedido', methods=['POST'])
@login_required
def Comprar():
    logging.basicConfig(filename='app.log',level=logging.NOTSET)
    ahora = datetime.datetime.now()
    direccion = request.form['txtDireccion']
    carrito = Carrito.query.filter_by(id_usuario=current_user.id).all()
    panes = []
    total = 0
    cantTotal = 0
    for item in carrito:
        pan = Pan.query.filter_by(id=item.id_pan).first()
        pan.cantidad = item.cantidad
        pan.total = item.total
        panes.append(pan)
        total += pan.total
        cantTotal += pan.cantidad
    
    if cantTotal < 50:
        total += 30

    now = datetime.datetime.now()
    pedido = Pedido(id_usuario=current_user.id, fecha=now, total=total, direccion=direccion, estatus='Pendiente')
    db.session.add(pedido)
    db.session.commit()

    ped = Pedido.query.filter_by(id_usuario=current_user.id).order_by(Pedido.id.desc()).first()
    for pan in panes:
        pan_pedido = Pan_Pedido(id_pan=pan.id, id_pedido=ped.id, cantidad=pan.cantidad, total=pan.total)
        db.session.add(pan_pedido)
        db.session.commit()
    
    for item in carrito:
        db.session.delete(item)
        db.session.commit()
        
    logging.info('Pedido realizado por el usuario: '+current_user.email + ' - '+ str(ahora))
    return redirect(url_for('clientes.Pedidos'))
    

@clientes.route('/Pedidos')
@login_required
def Pedidos():
    pedidos = Pedido.query.filter_by(id_usuario=current_user.id).all()
    panesPedidos = Pan_Pedido.query.all()
    pans = Pan.query.all()
    panes = []
    for pedido in pedidos:
        for panPedido in panesPedidos:
            if pedido.id == panPedido.id_pedido:
                for p in pans:
                    if panPedido.id_pan == p.id:
                        nPan = {"id":p.id, "nombre":p.nombre, "precio":p.precio, "cantidad":panPedido.cantidad, "pedido":pedido.id}
                        panes.append(nPan)

    for pedido in pedidos:
        fecha = pedido.fecha
        fechaDepurada = fecha.strftime("%d/%m/%Y") +" - "+ fecha.strftime("%H:%M")
        pedido.fecha = fechaDepurada

    pedidos.reverse()

    return render_template('pedidos.html', pedidos=pedidos, panes=panes)
