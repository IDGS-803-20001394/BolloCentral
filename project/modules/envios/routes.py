import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_security import login_required, roles_accepted, current_user
from project.models import User, Pan, Pedido, Pan_Pedido
from project import db
import logging

envios = Blueprint('envios', __name__)

@envios.route('/Envios')
@login_required
@roles_accepted('Admin', 'Trabajador')
def Envios():
    pedidos = Pedido.query.all()
    panesPedidos = Pan_Pedido.query.all()
    pans = Pan.query.all()
    clientes = User.query.all()
    panes = []
    pendientes = False
    for pedido in pedidos:
        if pedido.estatus == "Pendiente" or pedido.estatus == "Procesando" or pedido.estatus == "Enviado":
            pendientes = True
        for panPedido in panesPedidos:
            if pedido.id == panPedido.id_pedido:
                for p in pans:
                    if panPedido.id_pan == p.id:
                        nPan = {"id":p.id, "nombre":p.nombre, "precio":p.precio, "cantidad":panPedido.cantidad, "pedido":pedido.id}
                        panes.append(nPan)
    
    for pedidoD in pedidos:
        fecha = pedidoD.fecha
        fechaDepurada = fecha.strftime("%d/%m/%Y") +" - "+ fecha.strftime("%H:%M")
        pedidoD.fecha = fechaDepurada
        for cliente in clientes:
            if cliente.id == pedidoD.id_usuario:
                pedidoD.cliente = cliente.name
                pedidoD.telefono = cliente.telefono

    pedidos.reverse()
            
    return render_template('envios.html', pedidos=pedidos, panes=panes, pendientes=pendientes)

@envios.route('/ProcesarPedido')
@login_required
@roles_accepted('Admin', 'Trabajador')
def ProcesarPedido():
    logging.basicConfig(filename='app.log',level=logging.NOTSET)
    ahora = datetime.datetime.now()
    idPedido = request.args.get('id')
    pedido = Pedido.query.filter_by(id=idPedido).first()
    panesPedido = Pan_Pedido.query.filter_by(id_pedido=idPedido).all()
    pans = Pan.query.all()

    for panPedido in panesPedido:
        for pan in pans:
            if panPedido.id_pan == pan.id:
                if panPedido.cantidad > pan.inventario:
                    flash('No hay suficiente '+pan.nombre+' para procesar el pedido.', 'danger')
                    return redirect(url_for('envios.Envios'))
                else:
                    pan.inventario = pan.inventario - panPedido.cantidad
                    db.session.commit()

    pedido.estatus = "Procesando"
    db.session.commit()
    logging.warning('El pedido '+idPedido+' fue procesado por '+current_user.email+' el '+ahora.strftime("%d/%m/%Y")+" a las "+ahora.strftime("%H:%M"))
    return redirect(url_for('envios.Envios'))

@envios.route('/EnviarPedido')
@login_required
@roles_accepted('Admin', 'Trabajador')
def EnviarPedido():
    logging.basicConfig(filename='app.log',level=logging.NOTSET)
    ahora = datetime.datetime.now()
    idPedido = request.args.get('id')
    pedido = Pedido.query.filter_by(id=idPedido).first()
    pedido.estatus = "Enviado"
    db.session.commit()
    logging.warning('El pedido '+idPedido+' fue marcado como enviado por '+current_user.email+' el '+ahora.strftime("%d/%m/%Y")+" a las "+ahora.strftime("%H:%M"))
    return redirect(url_for('envios.Envios'))

@envios.route('/EntregarPedido')
@login_required
@roles_accepted('Admin', 'Trabajador')
def EntregarPedido():
    logging.basicConfig(filename='app.log',level=logging.NOTSET)
    ahora = datetime.datetime.now()
    idPedido = request.args.get('id')
    pedido = Pedido.query.filter_by(id=idPedido).first()
    pedido.estatus = "Entregado"
    db.session.commit()
    logging.warning('El pedido '+idPedido+' fue marcado como entregado por '+current_user.email+' el '+ahora.strftime("%d/%m/%Y")+" a las "+ahora.strftime("%H:%M"))
    return redirect(url_for('envios.Envios'))

@envios.route('/CancelarPedido')
@login_required
@roles_accepted('Admin', 'Trabajador')
def CancelarPedido():
    logging.basicConfig(filename='app.log',level=logging.NOTSET)
    ahora = datetime.datetime.now()
    idPedido = request.args.get('id')
    pedido = Pedido.query.filter_by(id=idPedido).first()
    panesPedido = Pan_Pedido.query.filter_by(id_pedido=idPedido).all()
    panes = Pan.query.all()

    if pedido.estatus != "Procesando":
        for panPedido in panesPedido:
            for pan in panes:
                if panPedido.id_pan == pan.id:
                    pan.inventario = pan.inventario + panPedido.cantidad
                    db.session.commit()
    

    pedido.estatus = "Cancelado"
    db.session.commit()
    logging.warning('El pedido '+idPedido+' fue cancelado por '+current_user.email+' el '+ahora.strftime("%d/%m/%Y")+" a las "+ahora.strftime("%H:%M"))
    return redirect(url_for('envios.Envios'))
