'''
Created on 22/01/2018

@author: CRISTIAN.BOTINA
'''
import hashlib,socket,json # @UnresolvedImport
from flask_restful import request, Resource
from wtforms import Form, validators, StringField
import SSI7X.Static.config as conf  # @UnresolvedImport
from SSI7X.Static.ConnectDB import ConnectDB  # @UnresolvedImport
from SSI7X.Static.Utils import Utils  # @UnresolvedImport
import SSI7X.Static.errors as errors  # @UnresolvedImport
import SSI7X.Static.labels as labels  # @UnresolvedImport
import time
import jwt #@UnresolvedImport
from SSI7X.ValidacionSeguridad import ValidacionSeguridad # @UnresolvedImport
import SSI7X.Static.config_DB as dbConf # @UnresolvedImport

lc_cnctn = ConnectDB()
Utils = Utils()
validacionSeguridad = ValidacionSeguridad()

class Acceso(Form):
    name = StringField(labels.lbl_nmbr_usrs,[validators.DataRequired(message=errors.ERR_NO_NOBRE)])
    username = StringField(labels.lbl_lgn,[validators.DataRequired(message=errors.ERR_NO_INGSA_USRO)]) 
    password = StringField(labels.lbl_cntrsna,[validators.DataRequired(message=errors.ERR_NO_INGRSA_CNTRSNA)])
    #user_photo = StringField(labels.lbl_cntrsna,[validators.DataRequired(message=errors.ERR_NO_FTO)])


class Usuarios(Resource):
    def post(self, **kwargs):
        if kwargs['page'] == 'listar_usuarios':
            arrayParametros={}
            arrayParametros['id_lgn_ge']=request.form['id_login_ge'] 
            arrayParametros['lgn']=request.form['login']
            return self.ObtenerUsuarios(arrayParametros)
        elif kwargs['page'] == 'insertar_usuario':
            return self.InsertarUsuarios()
    
    def ObtenerUsuarios(self,parametros):
        prmtrs=''
        if parametros:
            id_lgn_ge = parametros['id_lgn_ge']
            lgn = parametros['lgn']
            if id_lgn_ge:
                prmtrs = prmtrs + "  and a.id = " + id_lgn_ge
            if lgn:
                prmtrs = prmtrs + "  and lgn like '%" + lgn + "%' "
        
        Cursor = lc_cnctn.queryFree(" select "\
                                " a.id, b.lgn, b.nmbre_usro, b.fto_usro "\
                                " from "\
                                " ssi7x.tblogins_ge a inner join ssi7x.tblogins b on "\
                                " a.id_lgn = b.id "\
                                " where "\
                                " a.id_grpo_emprsrl = 2 and a.estdo = true "\
                                + prmtrs +
                                " order by "\
                                " b.lgn")
        if Cursor :    
            data = json.loads(json.dumps(Cursor, indent=2))
            return Utils.nice_json(data,200)
        else:
            return Utils.nice_json({"error":errors.ERR_NO_RGSTRS},400)
        
    def InsertarUsuarios(self):
        token = request.headers['Authorization']
        fcha_actl = time.ctime()
        ln_opcn_mnu = request.form["id_mnu"]
        validacionSeguridad = ValidacionSeguridad()
        val = validacionSeguridad.Principal(token,ln_opcn_mnu)
        
        if val :
            print('opcion menu '+ln_opcn_mnu)
            DatosUsuario = jwt.decode(token, conf.SS_TKN_SCRET_KEY, 'utf-8')
            id_lgn_ge_ssn = validacionSeguridad.validaUsuario(DatosUsuario['lgn'])
            '''
                Aqui insertamos los datos del usuario
            '''
            arrayValues={}
            arrayValues3={}
            arrayValues['lgn']=request.form['login']
            arrayValues['cntrsna']=request.form['password'] #pendiente encriptar la contraseña
            arrayValues['nmbre_usro']=request.form['nombre_usuario']
            arrayValues['fto_usro']=request.form['login'] #pendiente traer imagen
            id_lgn = self.CrearUsuario(arrayValues)
            arrayValues3['id_lgn']=str(id_lgn)
            arrayValues3['fcha_crcn']=str(fcha_actl)
            arrayValues3['fcha_mdfccn']=str(fcha_actl)
            arrayValues3['id_grpo_emprsrl']='2' #pendiente traer esta variable de una cookie
            id_lgn_ge=self.CrearUsuarioGe(arrayValues3)
            print('login',id_lgn_ge)
            '''
            Fin de la insercion de los datos
            '''
        else:
            return Utils.nice_json({"error":errors.ERR_NO_ATRZCN},400)
        
    
    def CrearUsuario(self,objectValues):
        return lc_cnctn.queryInsert(dbConf.DB_SHMA+".tblogins", objectValues,'id')
    
    def CrearUsuarioGe(self,objectValues):
        return lc_cnctn.queryInsert(dbConf.DB_SHMA+".tblogins_ge", objectValues,'id')
    
        