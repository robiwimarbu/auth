import hashlib, os
from IPy import IP
from flask import session
from flask_restful import request, Resource
from wtforms import Form, validators, StringField
from SSI7X.Static.ConnectDB import ConnectDB  # @UnresolvedImport
from SSI7X.Static.Utils import Utils  # @UnresolvedImport
from SSI7X.Static.Ldap_connect import Conexion_ldap 
import SSI7X.Static.errors as errors  # @UnresolvedImport
import SSI7X.Static.labels as labels  # @UnresolvedImport
import SSI7X.Static.config as conf  # @UnresolvedImport
import SSI7X.Static.config_DB as dbConf 
import socket
import json




class UsuarioAcceso(Form):
    username = StringField(labels.lbl_nmbr_usrs,[validators.DataRequired(message=errors.ERR_NO_02)])
    password = StringField(labels.lbl_cntrsna_usrs,[validators.DataRequired(message=errors.ERR_NO_03)])
    
class UsroCmbioCntrsna(Form):
    cntrsna = StringField(labels.lbl_cntrsna_usrs,[validators.DataRequired(message=errors.ERR_NO_03)])
    cntrsna_nva = StringField(labels.lbl_nva_cntrsna,[validators.DataRequired(message=errors.ERR_NO_04),validators.Length(min=conf.PW_MN_SIZE,message=errors.ERR_NO_06),validators.Regexp('(?=.*\d)',message=errors.ERR_NO_08),validators.Regexp('(?=.*[A-Z])',message=errors.ERR_NO_07)])
    tkn = StringField('el token', [validators.DataRequired(message='Falta el token'),validators.Length(min=conf.SS_TKN_SIZE,message=errors.ERR_NO_05)])
    
class AutenticacionUsuarios(Resource):
    def post(self):
        u = UsuarioAcceso(request.form)
        utils = Utils()
        if not u.validate():
            return utils.nice_json({"error":u.errors},400)
        IpUsuario = IP(socket.gethostbyname(socket.gethostname()))
        if IpUsuario.iptype() == 'PUBLIC':
            c = ConnectDB()
            md5= hashlib.md5(request.form['password'].encode('utf-8')).hexdigest() 
            cursor = c.querySelect(dbConf.DB_SHMA +'.tblogins', 'lgn,cntrsna', "lgn='"+ request.form['username']+ "' and  cntrsna='"+md5+"'")
            if cursor :
                session['logged_in'] = True
                token = os.urandom(conf.SS_TKN_SIZE)
                data = json.loads(json.dumps(self.ObtenerDatosUsuario()[0], indent=2))
                session[str(token)] = data
                return utils.nice_json({"access_token":str(token)},200)
            else:
                session['logged_in'] = False
                return utils.nice_json({"error":errors.ERR_NO_01},400)
        elif IpUsuario.iptype() == 'PRIVATE':
            Cldap = Conexion_ldap()
            VerificaConexion = Cldap.Conexion_ldap(request.form['username'], request.form['password'])
            if VerificaConexion :
                session['logged_in'] = True
                token = os.urandom(conf.SS_TKN_SIZE)
                data = json.loads(json.dumps(self.ObtenerDatosUsuario()[0], indent=2))
                session[str(token)] = data
                return utils.nice_json({"access_token":str(token)},200)
            else:
                session['logged_in'] = False
                return utils.nice_json({"error":errors.ERR_NO_01},400)
                
    def ObtenerDatosUsuario(self):
        c = ConnectDB()
        cursor = c.queryFree(" select " \
                             " case when emplds_une.id is not null then "\
                             " concat_ws("\
                             " ' ',"\
                             " emplds.prmr_nmbre,"\
                             " emplds.sgndo_nmbre,"\
                             " emplds.prmr_aplldo,"\
                             " emplds.sgndo_aplldo)"\
                             " else" \
                             " prstdr.nmbre_rzn_scl" \
                             " end as nmbre_cmplto," \
                             " case when emplds_une.id is not null then" \
                             " emplds.crro_elctrnco" \
                             " else" \
                             " prstdr.crro_elctrnco" \
                             " end as crro_elctrnco" \
                             " from ssi7x.tblogins_ge lgn_ge " \
                             " left join ssi7x.tblogins lgn on lgn.id = lgn_ge.id_lgn " \
                             " left join ssi7x.tbempleados_une emplds_une on emplds_une.id_lgn_accso_ge = lgn_ge.id " \
                             " left join ssi7x.tbempleados emplds on emplds.id = emplds_une.id_empldo " \
                             " left join ssi7x.tbprestadores prstdr on prstdr.id_lgn_accso_ge = lgn_ge.id " \
                             " where lgn.lgn = '"+request.form['username']+"'")
        return cursor
            
        
        
        
class CmboCntrsna(Resource):
    def post(self):
        u = UsroCmbioCntrsna(request.form)
        utils = Utils()
        
        if not u.validate():
            return utils.nice_json({"status":"Error","error":u.errors,"user":"null"})
        