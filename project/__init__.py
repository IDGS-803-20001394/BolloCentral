import os
from flask import Flask, redirect, render_template, url_for
from flask_login import LoginManager
from flask_security import Security, SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
from .models import User, Role
userDataStore = SQLAlchemyUserDatastore(db, User, Role)

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://BolloCentral:123456@localhost:3306/BolloCentral'
    app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
    app.config['SECURITY_PASSWORD_SALT'] = 'secretsalt'

    app.config['DEBUG']=True
    app.config['SCRET_KEY']="CLAVESECRETACHIDA"
    csrf=CSRFProtect()

    csrf.init_app(app)
    db.init_app(app)

    @app.before_request
    def create_all():
        db.create_all()

    security = Security(app, userDataStore)

    LoginManager.login_view = '/security/login'
    @app.errorhandler(404)
    def no_encontrada(e):
        return render_template('404.html'), 404
    @app.errorhandler(401)
    def no_logges(e):
        return redirect(url_for('auth.Login'))

    from.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .modules.auth.routes import auth
    app.register_blueprint(auth)

    from .modules.admin.routes import admin
    app.register_blueprint(admin)

    from .modules.cllientes.routes import clientes
    app.register_blueprint(clientes)

    from .modules.cocina.routes import cocina
    app.register_blueprint(cocina)

    from .modules.proveedores.routes import proveedores
    app.register_blueprint(proveedores)

    from .modules.envios.routes import envios
    app.register_blueprint(envios)

    from .modules.ventanilla.routes import ventanilla
    app.register_blueprint(ventanilla)

    from .modules.estadisticas.routes import estadisticas
    app.register_blueprint(estadisticas)


    return app