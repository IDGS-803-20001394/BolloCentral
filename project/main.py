from flask import Blueprint, render_template, request, flash
import logging


logging.basicConfig(filename='app.log',level=logging.INFO)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/Contactanos', methods=['GET', 'POST'])
def Contactanos():
    if request.method == 'POST':
        flash('Gracias por tu mensaje, pronto nos pondremos en contacto contigo', 'success')
    return render_template('contactanos.html')

