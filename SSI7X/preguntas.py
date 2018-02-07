'''
Created on 24 ene. 2018

@author: oscar.daza
'''
from flask_restful import request, Resource
from wtforms import Form, validators, StringField
from SSI7X.Static.ConnectDB import ConnectDB  # @UnresolvedImport
from SSI7X.Static.Utils import Utils  # @UnresolvedImport
import SSI7X.Static.errors as errors  # @UnresolvedImport
import SSI7X.Static.labels as labels  # @UnresolvedImport
from SSI7X.AuthUsers import AutenticacionUsuarios 
import SSI7X.Static.config_DB as dbConf # @UnresolvedImport   
import SSI7X.Static.config as conf  # @UnresolvedImport 
import jwt #@UnresolvedImport
import time
from SSI7X.ValidacionSeguridad import ValidacionSeguridad  # @UnresolvedImport
import json # @UnresolvedImport
  # @UnresolvedImport

'''
Declaracion de variables globales
'''
Utils = Utils()
validacionSeguridad = ValidacionSeguridad()
fecha_act = time.ctime()
C = ConnectDB()

class Acceso(Form):
    cdgo = StringField(labels.lbl_cdgo,[validators.DataRequired(message=errors.ERR_NO_CDGO_PRGNTA)])
    dscrpcn = StringField(labels.lbl_prgnta,[validators.DataRequired(message=errors.ERR_NO_PRGTA)])
    #dscrpcn_rspsta= StringField(labels.lbl_prgnta,[validators.DataRequired(message=errors.ERR_NO_RSPSTA)])
    #username = StringField(labels.lbl_lgn,[validators.DataRequired(message=errors.ERR_NO_INGSA_USRO)]) 
    #password = StringField(labels.lbl_cntrsna,[validators.DataRequired(message=errors.ERR_NO_INGRSA_CNTRSNA)])
class ActualizarAcceso(Form):
    id_prgnta_ge = StringField(labels.lbl_nmbr_usrs,[validators.DataRequired(message=errors.ERR_NO_SN_PRMTRS)])
    cdgo = StringField(labels.lbl_lgn,[validators.DataRequired(message=errors.ERR_NO_CDGO_PRGNTA)]) 
    dscrpcn = StringField(labels.lbl_prgnta,[validators.DataRequired(message=errors.ERR_NO_PRGTA)])
  
    
class Preguntas(Resource):
   
  
    def post(self,**kwargs):
       
        if kwargs['page'] == 'listar_preguntasg':
            return self.ObtenerPreguntas()
        elif kwargs['page'] == 'insertar_preguntasg':
            return self.crearPregunta()
        elif kwargs['page'] == 'actualizar_preguntasg':
            return self.ActualizarPreguntas() 
                       
    def crearPregunta(self):
        
        ln_opcn_mnu = request.form["id_mnu"]
        token = request.headers['Authorization']
        validacionSeguridad = ValidacionSeguridad()
        val = validacionSeguridad.Principal(token,ln_opcn_mnu)
        u=Acceso(request.form)
        if not u.validate():
            return self.Utils.nice_json({"error":u.errors},400)
        if val:
            DatosUsuarioToken = jwt.decode(token, conf.SS_TKN_SCRET_KEY, 'utf-8')
            datosUsuario = validacionSeguridad.ObtenerDatosUsuario(DatosUsuarioToken['lgn'])[0]
            arrayValues={}
            arrayValues2={}
            
            arrayValues['cdgo']=request.form['cdgo']
            arrayValues['dscrpcn']=request.form['dscrpcn']
            arrayValues['fcha_crcn']=str(fecha_act)
            arrayValues['fcha_mdfccn']=str(fecha_act)
            arrayValues['id_lgn_crcn_ge']=str(datosUsuario['id_lgn_ge'])
            arrayValues['id_lgn_mdfccn_ge']=str(datosUsuario['id_lgn_ge'])  
            id_prgnta=self.crearPregunta_seguridad(arrayValues,'tbpreguntas_seguridad' )
            #id_pregunta_seguridad=self.C.queryInsert(dbConf.DB_SHMA+".tbpreguntas_seguridad",arrayValues,'id')  
            arrayValues2['id_prgnta_sgrdd']=str(id_prgnta)
            arrayValues2['id_lgn_crcn_ge']=str(datosUsuario['id_lgn_ge'])
            arrayValues2['id_lgn_mdfccn_ge']=str(datosUsuario['id_lgn_ge'])
            arrayValues2['fcha_crcn']=str(fecha_act)
            arrayValues2['fcha_mdfccn']=str(fecha_act)
            arrayValues2['id_lgn_ge']=str(datosUsuario['id_lgn_ge'])
            self.crearPregunta_seguridad(arrayValues2,'tbpreguntas_seguridad_ge')
            return Utils.nice_json({"error":labels.SCCSS_RGSTRO_EXTSO},200)
        #return self.C.queryInsert(dbConf.DB_SHMA+".tbpreguntas_seguridad", objectValues,'id')  
        return Utils.nice_json({"error":errors.ERR_NO_ATRZCN},400)       
    
    def ObtenerPreguntas(self): 
        ln_opcn_mnu = request.form["id_mnu"]
        token = request.headers['Authorization']
        validacionSeguridad = ValidacionSeguridad()
        val = validacionSeguridad.Principal(token,ln_opcn_mnu)
        arrayParametros={}
        arrayParametros['cdgo']=request.form['cdgo'] 
        arrayParametros['dscrpcn']=request.form['dscrpcn']
        prmtrs=''
        if arrayParametros:
            cdgo = arrayParametros['cdgo']
            dscrpcn=arrayParametros['dscrpcn']
            if cdgo:
                prmtrs = prmtrs + "  and a.cdgo like '%" + cdgo+"%'"
            if dscrpcn:
                prmtrs = prmtrs + "  and a.dscrpcn like '%" + dscrpcn + "%' "
        if val:
            Cursor = C.queryFree(" select "\
                                " a.cdgo,a.dscrpcn "\
                                " from "\
                                " ssi7x.tbpreguntas_seguridad a inner join ssi7x.tbpreguntas_seguridad_ge b on "\
                                " a.id=b.id_prgnta_sgrdd "\
                                " where "\
                                " b.estdo = true "\
                                + str(prmtrs) )
            if  Cursor :    
                data = json.loads(json.dumps(Cursor, indent=2))
                return Utils.nice_json(data,200)
            else:
                return Utils.nice_json({"error":errors.ERR_NO_RGSTRS},400)  
        else:
            return Utils.nice_json({"error":errors.ERR_NO_ATRZCN},400)    
    
    def ActualizarPreguntas(self):
        token = request.headers['Authorization']
        ln_opcn_mnu = request.form["id_mnu"]
        validacionSeguridad = ValidacionSeguridad()
        val = validacionSeguridad.Principal(token,ln_opcn_mnu)
        u = ActualizarAcceso(request.form)
        if not u.validate():
            return Utils.nice_json({"error":u.errors},400)
        if val :
            DatosUsuarioToken = jwt.decode(token, conf.SS_TKN_SCRET_KEY, 'utf-8')
            id_lgn_ge_ssn = validacionSeguridad.ObtenerDatosUsuario(DatosUsuarioToken['lgn'])[0]
            print (id_lgn_ge_ssn['id_lgn_ge'])
            arrayValues={}
            arrayValues2={}
            #Actualizo tabla ge
            arrayValues['id']=request.form['id_prgnta_ge']
            arrayValues['fcha_mdfccn']=str(fecha_act)
            arrayValues['id_lgn_mdfccn_ge']=str(id_lgn_ge_ssn['id_lgn_ge'])
            self.PreguntaActualizaRegistro(arrayValues,'tbpreguntas_seguridad_ge')
            #obtengo id_prgnta a partir del id
            Cursor = C.querySelect(dbConf.DB_SHMA +'.tbpreguntas_seguridad_ge', 'id_prgnta_sgrdd', "id="+str(request.form['id_prgnta_ge']))
            if Cursor :
                data = json.loads(json.dumps(Cursor[0], indent=2))
                id_prgnta = data['id_prgnta_sgrdd']
                
            #Actualizo tabla principal
            arrayValues2['id']=id_prgnta
            arrayValues2['cdgo']=request.form['cdgo']
            arrayValues2['dscrpcn']=request.form['dscrpcn'] #pendiente encriptar la contraseña
            arrayValues2['fcha_mdfccn']=str(fecha_act)
            arrayValues2['id_lgn_mdfccn_ge']=str(id_lgn_ge_ssn['id_lgn_ge'])
            
            self.PreguntaActualizaRegistro(arrayValues2,'tbpreguntas_seguridad')
            return Utils.nice_json({"error":labels.SCCSS_ACTLZCN_EXTSA},200) 
        else:
            return Utils.nice_json({"error":errors.ERR_NO_ATRZCN},400)
            
    def crearPregunta_seguridad(self,objectValues,table_name):
        return C.queryInsert(dbConf.DB_SHMA+"."+str(table_name), objectValues,'id')  
    
    def PreguntaActualizaRegistro(self,objectValues,table_name):
        return C.queryUpdate(dbConf.DB_SHMA+"."+str(table_name), objectValues,'id='+str(objectValues['id']))
    