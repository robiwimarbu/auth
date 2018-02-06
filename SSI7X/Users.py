'''
Created on 22/01/2018

@author: CRISTIAN.BOTINA
'''
import json # @UnresolvedImport
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
from SSI7X.Static.UploadFiles import UploadFiles  # @UnresolvedImport
from _overlapped import NULL

lc_cnctn = ConnectDB()
Utils = Utils()
validacionSeguridad = ValidacionSeguridad()

class ActualizarAcceso(Form):
    id_login_ge = StringField(labels.lbl_nmbr_usrs,[validators.DataRequired(message=errors.ERR_NO_SN_PRMTRS)])
    login = StringField(labels.lbl_lgn,[validators.DataRequired(message=errors.ERR_NO_INGSA_USRO)]) 
    password = StringField(labels.lbl_cntrsna,[validators.DataRequired(message=errors.ERR_NO_INGRSA_CNTRSNA)])
    nombre_usuario = StringField(labels.lbl_nmbr_usrs,[validators.DataRequired(message=errors.ERR_NO_INGSA_NMBRE_USRO)])
    #user_photo =  StringField(labels.lbl_cntrsna,[validators.DataRequired(message=errors.ERR_NO_FTO)])

class AcInsertarAcceso(Form):
    login = StringField(labels.lbl_lgn,[validators.DataRequired(message=errors.ERR_NO_INGSA_USRO)]) 
    password = StringField(labels.lbl_cntrsna,[validators.DataRequired(message=errors.ERR_NO_INGRSA_CNTRSNA)])
    nombre_usuario = StringField(labels.lbl_nmbr_usrs,[validators.DataRequired(message=errors.ERR_NO_INGSA_NMBRE_USRO)])
    #user_photo =  StringField(labels.lbl_cntrsna,[validators.DataRequired(message=errors.ERR_NO_FTO)])


class Usuarios(Resource):
    def post(self, **kwargs):
        if kwargs['page'] == 'listar_usuarios':
            arrayParametros={}
            arrayParametros['id_lgn_ge']=request.form['id_login_ge'] 
            arrayParametros['lgn']=request.form['login']
            return self.ObtenerUsuarios(arrayParametros)
        elif kwargs['page'] == 'insertar_usuario':
            return self.InsertarUsuarios()
        elif kwargs['page'] == 'actualizar_usuario':
            return self.ActualzarUsuario()
    
    def ObtenerUsuarios(self,parametros):
        token = request.headers['Authorization']
        ln_opcn_mnu = request.form["id_mnu"]
        validacionSeguridad = ValidacionSeguridad()
        val = validacionSeguridad.Principal(token,ln_opcn_mnu)
        
        
        prmtrs=''
        if parametros:
            id_lgn_ge = parametros['id_lgn_ge']
            lgn = parametros['lgn']
            id_grpo_emprsrl = '2'
            if id_lgn_ge:
                prmtrs = prmtrs + "  and a.id = " + id_lgn_ge
            if lgn:
                prmtrs = prmtrs + "  and lgn like '%" + lgn + "%' "
            if id_grpo_emprsrl:
                prmtrs = prmtrs + "  and id_grpo_emprsrl = " + id_grpo_emprsrl + " "
                
        if val :
            Cursor = lc_cnctn.queryFree(" select "\
                                    " a.id, b.lgn, b.nmbre_usro, b.fto_usro "\
                                    " from "\
                                    " ssi7x.tblogins_ge a inner join ssi7x.tblogins b on "\
                                    " a.id_lgn = b.id "\
                                    " where "\
                                    " a.estdo = true "\
                                    + prmtrs +
                                    " order by "\
                                    " b.lgn")
            if Cursor :    
                data = json.loads(json.dumps(Cursor, indent=2))
                return Utils.nice_json(data,200)
            else:
                return Utils.nice_json({"error":errors.ERR_NO_RGSTRS},400)
        else:
            return Utils.nice_json({"error":errors.ERR_NO_ATRZCN},400)
        
    def InsertarUsuarios(self):
        token = request.headers['Authorization']
        fcha_actl = time.ctime()
        ln_opcn_mnu = request.form["id_mnu"]
        validacionSeguridad = ValidacionSeguridad()
        val = validacionSeguridad.Principal(token,ln_opcn_mnu)
        #Validar los campos requeridos.
        u = AcInsertarAcceso(request.form)
        if not u.validate():
            return Utils.nice_json({"error":u.errors},400)
        
        if val :
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
            id_lgn = self.UsuarioInsertaRegistro(arrayValues,'tblogins')
            arrayValues3['id_lgn']=str(id_lgn)
            arrayValues3['fcha_crcn']=str(fcha_actl)
            arrayValues3['fcha_mdfccn']=str(fcha_actl)
            arrayValues3['id_grpo_emprsrl']='2' #pendiente traer esta variable de una cookie
            id_lgn_ge=self.UsuarioInsertaRegistro(arrayValues3,'tblogins_ge')
            return Utils.nice_json({"error":errors.SCCSS_RGSTRO_EXTSO},200)
            '''
                Fin de la insercion de los datos
            '''
        else:
            return Utils.nice_json({"error":errors.ERR_NO_ATRZCN},400)
    
    def ActualzarUsuario(self):
        token = request.headers['Authorization']
        fcha_actl = time.ctime()
        ln_opcn_mnu = request.form["id_mnu"]
        validacionSeguridad = ValidacionSeguridad()
        val = validacionSeguridad.Principal(token,ln_opcn_mnu)
        Upload = UploadFiles()
        #Validar los campos requeridos.
        u = ActualizarAcceso(request.form)
        if not u.validate():
            return Utils.nice_json({"error":u.errors},400)
        if val :
            DatosUsuario = jwt.decode(token, conf.SS_TKN_SCRET_KEY, 'utf-8')
            id_lgn_ge_ssn = validacionSeguridad.validaUsuario(DatosUsuario['lgn'])
            '''
                Aqui Actualizamos los datos del usuario
            '''
            arrayValues={}
            arrayValues2={}
            #Actualizo tabla ge
            arrayValues2['id']=request.form['id_login_ge']
            arrayValues2['fcha_mdfccn']=str(fcha_actl)
            arrayValues2['id_grpo_emprsrl']='2' #pendiente traer esta variable de una cookie
            self.UsuarioActualizaRegistro(arrayValues2,'tblogins_ge')
            #obtengo id_lgn a partir del id_lgn_ge
            Cursor = lc_cnctn.querySelect(dbConf.DB_SHMA +'.tblogins_ge', 'id_lgn', "id="+str(request.form['id_login_ge']))
            if Cursor :
                data = json.loads(json.dumps(Cursor[0], indent=2))
                id_lgn = data['id_lgn']
            #Actualizo tabla principal
            arrayValues['id']=id_lgn
            arrayValues['lgn']=request.form['login']
            arrayValues['cntrsna']=request.form['password'] #pendiente encriptar la contraseña
            arrayValues['nmbre_usro']=request.form['nombre_usuario']
            arrayValues['fto_usro']=request.form['login'] #pendiente traer imagen
            
            #print(request.files)
            '''
                CARGA DE IMAGEN
            '''
            #guardar la imagen
            resultImageUpload={}
            if 'imge_pth' in request.files:
                nameFile = 'prueba.jpg'
                mFile = UploadFiles(conf.SV_DIR_IMAGES,NULL,True)
                print(request.files)
                print(request.files['imge_pth'])
                resultImageUpload = mFile.upload(request.files['imge_pth'])
                #Check status uploadimage
                if resultImageUpload["status"] == "OK":
                    #update column image on user
                    fullpath = conf.SV_DIR_IMAGES + conf.UTIL_DS + resultImageUpload["namefile"]
                    #lc_cnctn.queryUpdate(conf.TBL_TBUSERS,{"imge_pth":fullpath},"id="+str(id_lgn))
                    #lc_cnctn.queryUpdate(dbConf.DB_SHMA+"."+str(table_name), objectValues,'id='+str(objectValues['id']))
                    return Utils.nice_json({"status":"ok","error":"null","user":str(id_lgn)},200)
                else:
                    return Utils.nice_json({"status":"error","error":"no se pudo guardar la imagen","user":str(id_lgn)},400)
            else:
                return Utils.nice_json({"status":"error","error":"null","user":str(id_lgn)},400)
            '''
                FIN CARGA DE IMAGEN
            '''
            #ACTUALIZACION TABLA LOGINS OK
            self.UsuarioActualizaRegistro(arrayValues,'tblogins')
            return Utils.nice_json({"error":errors.SCCSS_ACTLZCN_EXTSA},200) 
            '''
                Fin de la insercion de los datos
            '''
        else:
            return Utils.nice_json({"error":errors.ERR_NO_ATRZCN},400)
     
    def UsuarioInsertaRegistro(self,objectValues,table_name):
        return lc_cnctn.queryInsert(dbConf.DB_SHMA+"."+str(table_name), objectValues,'id') 
    
    def UsuarioActualizaRegistro(self,objectValues,table_name):
        return lc_cnctn.queryUpdate(dbConf.DB_SHMA+"."+str(table_name), objectValues,'id='+str(objectValues['id']))