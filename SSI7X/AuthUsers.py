from flask import session
from flask_restful import request, Resource
from wtforms import Form, validators, StringField
from SSI7X.Static.Utils import Utils
from SSI7X.Static.ConnectDB import ConnectDB

import hashlib,os

class UsuarioAcceso(Form):
    usro = StringField('Nombre de usuario',[validators.DataRequired(message="Debe ingresar su usuario")])
    cntrsna = StringField('Cntrasenna de usuario',[validators.DataRequired(message="Debe ingresar su contrasenna")])

class AutenticacionUsuarios(Resource):
    def post(self):
        u = UsuarioAcceso(request.form)
        utils = Utils()
        if not u.validate():
            return utils.nice_json({"status":"Error","error":u.errors,"user":"null"})
        
        c = ConnectDB()
        md5= hashlib.md5(request.form['cntrsna'].encode('utf-8')).hexdigest() 
        print(md5)
        cursor = c.querySelect('ssi.tblogins', 'lgn,cntrsna', "lgn='"+ request.form['usro']+ "' and  cntrsna='"+md5+"'")
        
        if cursor[0][0]!= '':
            session['logged_in'] = True
        else:
            session['logged_in'] = False
        
        token = os.urandom(12)
        print(token)
        session['token'] = str(token)
        data=[]
        data.append({"logged_in":session['logged_in'],"token":token})
        return utils.nice_json({"status":"OK","error":"null","session":str(data)})