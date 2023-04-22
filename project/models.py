from .import db
from flask_security import UserMixin, RoleMixin

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    telefono = db.Column(db.String(10), nullable=False)
    direccion = db.Column(db.String(255), nullable=False)

class Pan(db.Model):
    __tablename__ = 'pan'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    inventario = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)
    cantidadLote = db.Column(db.Integer, nullable=False)
    imagen = db.Column(db.Text)
    receta = db.Column(db.Text)
    estatus = db.Column(db.Integer, nullable=False)

class MateriaPrima(db.Model):
    __tablename__ = 'materia_prima'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    inventario = db.Column(db.Float, nullable=False)
    unidad = db.Column(db.String(10), nullable=False)

class IngredientePan(db.Model):
    __tablename__ = 'ingrediente_pan'
    id = db.Column(db.Integer, primary_key=True)
    id_pan = db.Column(db.Integer, db.ForeignKey('pan.id'))
    id_materia = db.Column(db.Integer, db.ForeignKey('materia_prima.id'))
    cantidad = db.Column(db.Float, nullable=False)

class Proveedor(db.Model):
    __tablename__ = 'proveedor'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(10), nullable=False)
    empresa = db.Column(db.String(255), nullable=False)
    direccion = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    producto = db.Column(db.Integer, db.ForeignKey('materia_prima.id'))
    costoProducto = db.Column(db.Float, nullable=False)
    estatus = db.Column(db.Integer, nullable=False)


class Provision(db.Model):
    __tablename__ = 'provision'
    id = db.Column(db.Integer, primary_key=True)
    id_proveedor = db.Column(db.Integer, db.ForeignKey('proveedor.id'))
    id_materia = db.Column(db.Integer, db.ForeignKey('materia_prima.id'))
    cantidad = db.Column(db.Integer, nullable=False)
    costoTotal = db.Column(db.Float, nullable=False)
    fechaPedido = db.Column(db.DateTime, nullable=False)
    fechaEntrega = db.Column(db.DateTime)
    estatus = db.Column(db.String(255), nullable=False)

class Carrito(db.Model):
    __tablename__= 'carrito'
    id = db.Column(db.Integer, primary_key=True)
    id_pan = db.Column(db.Integer, db.ForeignKey('pan.id'))
    id_usuario = db.Column(db.Integer, db.ForeignKey('user.id'))
    cantidad = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)

class Pedido(db.Model):
    __tablename__ = 'pedido'
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('user.id'))
    fecha = db.Column(db.DateTime, nullable=False)
    direccion = db.Column(db.String(255), nullable=False)
    total = db.Column(db.Float, nullable=False)
    estatus = db.Column(db.String(255), nullable=False)

class Pan_Pedido(db.Model):
    __tablename__ = 'pan_pedido'
    id = db.Column(db.Integer, primary_key=True)
    id_pan = db.Column(db.Integer, db.ForeignKey('pan.id'))
    id_pedido = db.Column(db.Integer, db.ForeignKey('pedido.id'))
    cantidad = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)

class ventaLocal(db.Model):
    __tablename__ = 'venta_local'
    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)

class Pan_VentaL(db.Model):
    __tablename__ = 'pan_ventaL'
    id = db.Column(db.Integer, primary_key=True)
    id_pan = db.Column(db.Integer, db.ForeignKey('pan.id'))
    id_venta = db.Column(db.Integer, db.ForeignKey('venta_local.id'))
    cantidad = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)

class carritoVentanilla(db.Model):
    __tablename__= 'carritoVentanilla'
    id = db.Column(db.Integer, primary_key=True)
    id_pan = db.Column(db.Integer, db.ForeignKey('pan.id'))
    cantidad = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)

class ordenCocina(db.Model):
    __tablename__ = 'orden_cocina'
    id = db.Column(db.Integer, primary_key=True)
    id_pan = db.Column(db.Integer, db.ForeignKey('pan.id'))
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    estatus = db.Column(db.String(255), nullable=False)