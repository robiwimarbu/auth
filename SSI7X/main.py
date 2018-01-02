from flask import Flask, Blueprint
from flask_restful import Api
from flask_cors import CORS
import os
from SSI7X.AuthUsers import AutenticacionUsuarios
import SSI7X.Static.config as conf
#ruta para las aciones de home.
auth = Blueprint('login', __name__)

#ruta para las imagenes
images = Blueprint('images', __name__, static_folder='/img')

app = Flask(__name__)

#TODO: Check rules for cors
CORS(app) #ALLOW ALL ORIGN BY ALL ROUTES

api = Api( auth, prefix="/login")
api.add_resource(AutenticacionUsuarios,'/auth')
#QUE PUTAS PASA no se perro!!
if __name__ == '__main__':
    app.register_blueprint(auth)
    app.register_blueprint(images)
    
    app.secret_key = os.urandom(12)
    app.run( conf.SV_HOST,conf.SV_PORT,conf.ST_DEBUG)
    
