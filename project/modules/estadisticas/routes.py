from flask import Blueprint, render_template
from flask_security import login_required, roles_accepted
from project.models import Pan, ordenCocina, Pedido, Pan_Pedido, ventaLocal, Pan_VentaL, Proveedor, MateriaPrima, IngredientePan
from project import db

estadisticas = Blueprint('estadisticas', __name__)

@estadisticas.route('/Estadisticas')
@login_required
@roles_accepted('Trabajador','Admin')
def Estadisticas():
    panes = Pan.query.all()
    ordenes = ordenCocina.query.all()
    pedidos = Pedido.query.all()
    panesP = Pan_Pedido.query.all()
    ventas = ventaLocal.query.all()
    panesV = Pan_VentaL.query.all()
    proveedores = Proveedor.query.all()
    materias = MateriaPrima.query.all()
    ingredientes = IngredientePan.query.all()

    ganTotal = 0
    for pan in panes:
        pan.lotesC = 0
        pan.totalesC = 0
        pan.vendidos = 0
        pan.venta = 0
        pan.costo = 0
        pan.insumos = 0
        pan.utilidad = 0
    
    for materia in materias:
        materia.precio = 0

    for orden in ordenes:
        for pan in panes:
            if orden.id_pan == pan.id:
                if orden.estatus == 'Completada':
                    pan.lotesC += orden.cantidad
                    pan.totalesC += orden.cantidad * pan.cantidadLote

    for pedido in pedidos:
        for pan in panesP:
            if pedido.id == pan.id_pedido:
                if pedido.estatus == 'Entregado':
                    for pan2 in panes:
                        if pan.id_pan == pan2.id:
                            pan2.vendidos += pan.cantidad
                            pan2.venta += pan.total
    
    for venta in ventas:
        for pan in panesV:
            if venta.id == pan.id_venta:
                for pan2 in panes:
                    if pan.id_pan == pan2.id:
                        pan2.vendidos += pan.cantidad
                        pan2.venta += pan.total

    for materia in materias:
        for proveedor in proveedores:
            if materia.id == proveedor.producto:
                materia.precio  = proveedor.costoProducto;
    
    for pan in panes:
        for ingrediente in ingredientes:
            if pan.id == ingrediente.id_pan:
                for materia in materias:
                    if materia.id == ingrediente.id_materia:
                        pan.costo += materia.precio * ingrediente.cantidad
                        pan.costo = round(pan.costo, 2)

    for pan in panes:
        pan.costo = pan.costo/pan.cantidadLote
        pan.costo = round(pan.costo, 2)
        pan.insumos = pan.costo * pan.totalesC
        pan.insumos = round(pan.insumos, 2)
        pan.utilidad = pan.venta - pan.insumos
        pan.utilidad = round(pan.utilidad, 2)
        ganTotal += pan.utilidad
        ganTotal = round(ganTotal, 2)
    
    return render_template('estadisticas.html', panes=panes, total=ganTotal)

