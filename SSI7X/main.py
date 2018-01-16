import os
from flask import Flask, Blueprint
from flask_cors import CORS
from flask_restful import Api
import SSI7X.Static.config as conf  # @UnresolvedImport
from SSI7X.AuthUsers import CmboCntrsna,AutenticacionUsuarios,MenuDefectoUsuario



#ruta para las aciones de home.
auth = Blueprint('login', __name__)

#ruta para las imagenes
images = Blueprint('images', __name__, static_folder='/img')

app = Flask(__name__)

#To Do:Verificar la seguridad del cors  
# commit luis
CORS(app)

api = Api( auth, prefix="/api")
api.add_resource(AutenticacionUsuarios,'/auth')
api.add_resource(CmboCntrsna,'/cambio_password')
api.add_resource(MenuDefectoUsuario,'/menu')


if __name__ == '__main__':
    app.register_blueprint(auth)
    app.register_blueprint(images)
    
    app.secret_key = os.urandom(conf.SS_TKN_SIZE)
    app.run( conf.SV_HOST,conf.SV_PORT,conf.ST_DEBUG)