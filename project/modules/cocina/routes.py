import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_security import login_required, roles_accepted, current_user
from flask_security.utils import login_user, logout_user   
from project.models import Pan, MateriaPrima, IngredientePan, ordenCocina
import base64
from project import db, userDataStore
import logging

cocina = Blueprint('cocina', __name__)

@cocina.route('/Cocina')
@login_required
@roles_accepted('Cocina','Admin')
def Cocina():
    panes = Pan.query.filter_by(estatus=1).all()
    return render_template('cocina.html', panes=panes)

@cocina.route('/Cocinar', methods=['GET', 'POST'])
@login_required
@roles_accepted('Cocina','Admin')
def Cocinar():
    logging.basicConfig(filename='app.log',level=logging.NOTSET)
    ahora = datetime.datetime.now()
    if request.method == 'POST':
        id = request.form['txtId']
        cantidad = request.form['txtCantidad']
        now = datetime.datetime.now()
        newOrden = ordenCocina(id_pan=id, cantidad=cantidad, fecha=now, estatus="Pendiente")        
        db.session.add(newOrden)
        db.session.commit()
        logging.info('El usuario:'+ current_user.email  +' agregó una orden de cocina el: ' + ahora.strftime("%d/%m/%Y") + ' a las: ' + ahora.strftime("%H:%M:%S"))
        return redirect(url_for('cocina.OrdenesCocina'))

    id = request.args.get('id')
    pan = Pan.query.filter_by(id=id).first()
    ingredientes = IngredientePan.query.filter_by(id_pan=id).all()
    materias = MateriaPrima.query.all()
    return render_template('cocinar.html', pan=pan, ingredientes=ingredientes, materias=materias)

@cocina.route('/Panes')
@login_required
@roles_accepted('Cocina','Admin')
def Panes():
    panes = Pan.query.filter_by(estatus=1).all()
    return render_template('panes.html', panes=panes)

@cocina.route('/NuevoPan', methods=['GET', 'POST'])
@login_required
@roles_accepted('Cocina','Admin')
def NuevoPan():
    logging.basicConfig(filename='app.log',level=logging.NOTSET)
    ahora = datetime.datetime.now()
    if request.method == 'POST':
        try:
            nombre = request.form['txtNombre']
            precio = request.form['txtPrecio']
            descripcion = request.form['txtDescripcion']
            cantLote = request.form['txtCantidad']
            receta = request.form['txtReceta']
            img = request.files['imgPan']
            img64 = base64.b64encode(img.read())

            newPan = Pan(nombre=nombre, inventario=0, precio=precio, descripcion=descripcion, receta=receta, cantidadLote=cantLote, estatus=1, imagen=img64)
            db.session.add(newPan)
            db.session.commit()
            logging.info('El usuario:'+ current_user.email  +' agregó el pan: '+ nombre +' el: ' + ahora.strftime("%d/%m/%Y") + ' a las: ' + ahora.strftime("%H:%M:%S"))
            return redirect(url_for('cocina.Panes'))
        except Exception as e:
            flash('Ocurrió un error al agregar el pan: ' + str(e), 'error')
            return redirect(url_for('cocina.NuevoPan'))

    return render_template('agregarPan.html')

@cocina.route('/ModificarPan', methods=['GET', 'POST'])
@login_required
@roles_accepted('Cocina','Admin')
def ModificarPan():
    logging.basicConfig(filename='app.log',level=logging.NOTSET)
    ahora = datetime.datetime.now()
    if request.method == 'POST':
        id = request.form['txtId']
        nombre = request.form['txtNombre']
        precio = request.form['txtPrecio']
        descripcion = request.form['txtDescripcion']
        cantLote = request.form['txtCantidad']
        receta = request.form['txtReceta']
        img = request.files['imgPan']
        img64 = base64.b64encode(img.read())

        pan = Pan.query.filter_by(id=id).first()
        pan.nombre = nombre
        pan.precio = precio
        pan.descripcion = descripcion
        pan.cantidadLote = cantLote
        pan.receta = receta

        if img.filename != '':
            pan.imagen = img64

        db.session.commit()
        logging.info('El usuario:'+ current_user.email  +' modificó el pan: '+ nombre +' el: ' + ahora.strftime("%d/%m/%Y") + ' a las: ' + ahora.strftime("%H:%M:%S"))
        return redirect(url_for('cocina.Panes'))

    id = request.args.get('id')
    pan = Pan.query.filter_by(id=id).first()
    return render_template('modificarPan.html', pan=pan)

@cocina.route('/EliminarPan', methods=['GET', 'POST'])
@login_required
@roles_accepted('Cocina','Admin')
def EliminarPan():
    logging.basicConfig(filename='app.log',level=logging.NOTSET)
    ahora = datetime.datetime.now()
    if request.method == 'POST':
        id = request.form['txtId']
        pan = Pan.query.filter_by(id=id).first()
        pan.estatus = 0
        db.session.commit()
        logging.info('El usuario:'+ current_user.email  +' desactivó el pan: '+ pan.nombre +' el: ' + ahora.strftime("%d/%m/%Y") + ' a las: ' + ahora.strftime("%H:%M:%S"))
        return redirect(url_for('cocina.Panes'))

    id = request.args.get('id')
    pan = Pan.query.filter_by(id=id).first()
    return render_template('eliminarPan.html', pan=pan)


@cocina.route('/MateriaPrima')
@login_required
@roles_accepted('Cocina','Admin')
def MateriasPrimas():
    materias = MateriaPrima.query.all()
    materiasOrdenadas = sorted(materias, key=lambda x: x.nombre)
    return render_template('materiaPrima.html', materias=materiasOrdenadas)

@cocina.route('/NuevaMateria', methods=['GET', 'POST'])
@login_required
@roles_accepted('Cocina','Admin')
def NuevaMateria():
    logging.basicConfig(filename='app.log',level=logging.NOTSET)
    ahora = datetime.datetime.now()
    if request.method == 'POST':
        nombre = request.form['txtNombre']
        unidad = request.form['txtUnidad']
        inventario = request.form['txtInventario']

        newMateria = MateriaPrima(nombre=nombre, unidad=unidad, inventario=inventario)
        db.session.add(newMateria)
        db.session.commit()
        logging.info('El usuario:'+ current_user.email  +' agregó la materia prima: '+ nombre +' el: ' + ahora.strftime("%d/%m/%Y") + ' a las: ' + ahora.strftime("%H:%M:%S"))
        return redirect(url_for('cocina.MateriasPrimas'))
    
    return render_template('agregarMateria.html')

@cocina.route('/MermarMateria', methods=['POST'])
@login_required
@roles_accepted('Cocina','Admin')
def MermarMateria():
    logging.basicConfig(filename='app.log',level=logging.NOTSET)
    ahora = datetime.datetime.now()
    id = request.form['txtId']
    merma = request.form['txtMerma']
    materia = MateriaPrima.query.filter_by(id=id).first()
    materia.inventario -= float(merma)
    db.session.commit()
    logging.info('El usuario:'+ current_user.email  +' mermó: '+ merma +''+materia.unidad+ ' de '+ materia.nombre+' el: ' + ahora.strftime("%d/%m/%Y") + ' a las: ' + ahora.strftime("%H:%M:%S"))
    return redirect(url_for('cocina.MateriasPrimas'))

@cocina.route('/IngredientesPan', methods=['GET', 'POST'])
@login_required
@roles_accepted('Cocina','Admin')
def IngredientesPan():
    logging.basicConfig(filename='app.log',level=logging.NOTSET)
    ahora = datetime.datetime.now()
    id = request.args.get('id')
    pan = Pan.query.filter_by(id=id).first()
    materias = MateriaPrima.query.all()
    ingredientes = IngredientePan.query.filter_by(id_pan=id).all()
    materiasOrdneadas = sorted(materias, key=lambda materia: materia.nombre)
    for ingrediente in ingredientes:
        for materia in materias:
            if ingrediente.id_materia == materia.id:
                ingrediente.nombre = materia.nombre
                ingrediente.unidad = materia.unidad

    if request.method == 'POST':
        idPan = request.form['txtIdPan']
        idMateria = request.form['txtIdMateria']
        cantidad = request.form['txtCantidad']
        ingredientesExistente = IngredientePan.query.filter_by(id_pan=idPan, id_materia=idMateria).first()
        if ingredientesExistente is None:
            newIngrediente = IngredientePan(id_pan=idPan, id_materia=idMateria, cantidad=cantidad)
            db.session.add(newIngrediente)
            db.session.commit()
        else:
            ingredientesExistente.cantidad = cantidad
            db.session.commit()
        logging.info('El usuario:'+ current_user.email  +' modificó los ingredientes del pan: '+ idPan +' el: ' + ahora.strftime("%d/%m/%Y") + ' a las: ' + ahora.strftime("%H:%M:%S"))
        return redirect(url_for('cocina.IngredientesPan', id=idPan))
    return render_template('ingredientesPan.html', pan=pan, materias=materiasOrdneadas, ingredientes=ingredientes)

@cocina.route('/EliminarIngrediente', methods=['POST'])
@login_required
@roles_accepted('Cocina','Admin')
def EliminarIngrediente():
    id = request.form['txtId']
    ingrediente = IngredientePan.query.filter_by(id=id).first()
    db.session.delete(ingrediente)
    db.session.commit()
    return redirect(url_for('cocina.IngredientesPan', id=ingrediente.id_pan))

@cocina.route('/OrdenesCocina')
@login_required
@roles_accepted('Cocina','Admin')
def OrdenesCocina():
    ordenes = ordenCocina.query.all()
    panes = Pan.query.all()
    pendientes = False
    for orden in ordenes:
        if orden.estatus == "Pendiente" or orden.estatus == "Procesando":
            pendientes = True
        fecha = orden.fecha
        fechaDepurada = fecha.strftime("%d/%m/%Y") +" - "+ fecha.strftime("%H:%M")
        orden.fecha = fechaDepurada

    for pan in panes:
        for orden in ordenes:
            if pan.id == orden.id_pan:
                orden.total = pan.cantidadLote * orden.cantidad

    ordenes.reverse()
    return render_template('ordenesCocina.html', ordenes=ordenes, panes=panes, pendientes=pendientes)

@cocina.route('/ProcesarOrden', methods=['POST'])
@login_required
@roles_accepted('Cocina','Admin')
def ProcesarOrden():
    logging.basicConfig(filename='app.log',level=logging.NOTSET)
    ahora = datetime.datetime.now()
    id = request.form['txtId']
    orden = ordenCocina.query.filter_by(id=id).first()
    ingredientes = IngredientePan.query.filter_by(id_pan=orden.id_pan).all()
    materias = MateriaPrima.query.all()
    for ingrediente in ingredientes:
        for materia in materias:
            if ingrediente.id_materia == materia.id:
                if ingrediente.cantidad * orden.cantidad > materia.inventario:
                    flash('No hay suficiente ${{materia.nombre}} para la orden', 'error')
                    return redirect(url_for('cocina.OrdenesCocina'))
                else:
                    materia.inventario -= ingrediente.cantidad * orden.cantidad
                    orden.estatus = "Procesando"
                    logging.info('El usuario:'+ current_user.email  +' procesó la orden: '+ str(orden.id) +' el: ' + ahora.strftime("%d/%m/%Y") + ' a las: ' + ahora.strftime("%H:%M:%S"))
                    db.session.commit()

    return redirect(url_for('cocina.OrdenesCocina'))

@cocina.route('/CompletarOrden', methods=['POST'])
@login_required
@roles_accepted('Cocina','Admin')
def CompletarOrden():
    logging.basicConfig(filename='app.log',level=logging.NOTSET)
    ahora = datetime.datetime.now()
    id = request.form['txtId']
    orden = ordenCocina.query.filter_by(id=id).first()
    pan = Pan.query.filter_by(id=orden.id_pan).first()
    pan.inventario += pan.cantidadLote * orden.cantidad
    orden.estatus = "Completada"
    db.session.commit()
    logging.info('El usuario:'+ current_user.email  +' completó la orden: '+ str(orden.id) +' el: ' + ahora.strftime("%d/%m/%Y") + ' a las: ' + ahora.strftime("%H:%M:%S"))
    return redirect(url_for('cocina.OrdenesCocina'))

@cocina.route('/CancelarOrden', methods=['POST'])
@login_required
@roles_accepted('Cocina','Admin')
def CancelarOrden():
    ahora = datetime.datetime.now()
    logging.basicConfig(filename='app.log',level=logging.NOTSET)
    id = request.form['txtId']
    orden = ordenCocina.query.filter_by(id=id).first()
    orden.estatus = "Cancelada"
    db.session.commit()
    logging.info('El usuario:'+ current_user.email  +' canceló la orden: '+ str(orden.id) +' el: ' + ahora.strftime("%d/%m/%Y") + ' a las: ' + ahora.strftime("%H:%M:%S"))
    return redirect(url_for('cocina.OrdenesCocina'))