import hashlib, os

from flask import session
from flask_restful import request, Resource
from wtforms import Form, validators, StringField
from SSI7X.Static.ConnectDB import ConnectDB  # @UnresolvedImport
from SSI7X.Static.Utils import Utils  # @UnresolvedImport
import SSI7X.Static.errors as errors


class UsuarioAcceso(Form):
    usro = StringField('Nombre de usuario',[validators.DataRequired(message=errors.ERR_NO_02)])
    cntrsna = StringField('Cntrasenna de usuario',[validators.DataRequired(message=errors.ERR_NO_03)])

class AutenticacionUsuarios(Resource):
    def post(self):
        u = UsuarioAcceso(request.form)
        utils = Utils()
        if not u.validate():
            return utils.nice_json({"status":"Error","error":u.errors,"user":"null"})
        
        c = ConnectDB()
        md5= hashlib.md5(request.form['cntrsna'].encode('utf-8')).hexdigest() 
        cursor = c.querySelect('ssi.tblogins', 'lgn,cntrsna', "lgn='"+ request.form['usro']+ "' and  cntrsna='"+md5+"'")
        data=[]
        if cursor :
            session['logged_in'] = True
            token = os.urandom(24)
            session['token'] = str(token)
            data.append({"logged_in":session['logged_in'],"token":token})
            return utils.nice_json({"status":"OK","error":"null","session":str(data)})
        else:
            session['logged_in'] = False
            data.append({"logged_in":session['logged_in'],"token":''})
            return utils.nice_json({"status":"OK","error":errors.ERR_NO_01,"session":str(data)})