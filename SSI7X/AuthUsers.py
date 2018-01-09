import hashlib, os

from flask import session
from flask_restful import request, Resource
from wtforms import Form, validators, StringField
from SSI7X.Static.ConnectDB import ConnectDB  # @UnresolvedImport
from SSI7X.Static.Utils import Utils  # @UnresolvedImport
import SSI7X.Static.errors as errors  # @UnresolvedImport
import SSI7X.Static.config as conf  # @UnresolvedImport

class UsuarioAcceso(Form):
    usro = StringField('Nombre de usuario',[validators.DataRequired(message=errors.ERR_NO_02)])
    cntrsna = StringField('Cntrasenna de usuario',[validators.DataRequired(message=errors.ERR_NO_03)])
    
class UsroCmbioCntrsna(Form):
    cntrsna = StringField('Cntrasenna de usuario',[validators.DataRequired(message=errors.ERR_NO_03)])
    cntrsna_nva = StringField('Nueva contrasenna',[validators.DataRequired(message=errors.ERR_NO_04),validators.Length(min=conf.PW_MN_SIZE,message=errors.ERR_NO_06),validators.Regexp('(?=.*\d)',message=errors.ERR_NO_08),validators.Regexp('(?=.*[A-Z])',message=errors.ERR_NO_07)])
    tkn = StringField('el token', [validators.DataRequired(message='Falta el token'),validators.Length(min=conf.SS_TKN_SIZE,message=errors.ERR_NO_05)])
    
class AutenticacionUsuarios(Resource):
    def post(self):
        u = UsuarioAcceso(request.form)
        utils = Utils()
        if not u.validate():
            return utils.nice_json({"status":"Error","error":u.errors,"user":"null"})
        
        c = ConnectDB()
        md5= hashlib.md5(request.form['cntrsna'].encode('utf-8')).hexdigest() 
        cursor = c.querySelect(conf.DB_SHMA +'.tblogins', 'lgn,cntrsna', "lgn='"+ request.form['usro']+ "' and  cntrsna='"+md5+"'")
        data=[]
        if cursor :
            session['logged_in'] = True
            token = os.urandom(24)
            session['token'] = str(token).encode(encoding='utf_8', errors='strict')
            data.append({"logged_in":session['logged_in'],"token":token})
            return utils.nice_json({"status":"OK","error":"null","session":str(data)})
        else:
            session['logged_in'] = False
            data.append({"logged_in":session['logged_in'],"token":''})
            return utils.nice_json({"status":"Error","error":errors.ERR_NO_01,"session":str(data)})
class CmboCntrsna(Resource):
    def post(self):
        u = UsroCmbioCntrsna(request.form)
        utils = Utils()
        
        if not u.validate():
            return utils.nice_json({"status":"Error","error":u.errors,"user":"null"})
        