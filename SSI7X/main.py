from flask import Flask, Blueprint
from flask_cors import CORS
from flask_restful import Api
import SSI7X.Static.config as conf  # @UnresolvedImport 
from SSI7X.AuthUsers import AutenticacionUsuarios  # @UnresolvedImport
from SSI7X.perfiles import Perfiles # @UnresolvedImport
from SSI7X.Users import Usuarios # @UnresolvedImport
from SSI7X.preguntas import Preguntas# @UnresolvedImport




#ruta para las aciones de home.
auth = Blueprint('login', __name__)

#ruta para las imagenes
images = Blueprint('images', __name__, static_folder='/img')

app = Flask(__name__)
#To Do:Verificar la seguridad del cors  
# commit luis
CORS(app, origins="*", allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],supports_credentials=True)

api = Api( auth, prefix="/api")
api.add_resource(AutenticacionUsuarios,'/auth/<page>')
api.add_resource(Perfiles,'/perfiles/<page>')
api.add_resource(Preguntas,'/preguntasSg/<page>')
api.add_resource(Usuarios,'/users/<page>')


if __name__ == '__main__':
    app.register_blueprint(auth)
    app.register_blueprint(images)
    app.config["SESSION_COOKIE_NAME"]="python_session"
    app.config["SESSION_COOKIE_HTTPONLY"]=False
    app.secret_key = conf.SS_TKN_SCRET_KEY 
    app.run( conf.SV_HOST,conf.SV_PORT,conf.ST_DEBUG)