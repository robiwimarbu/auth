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
'''
Declaracion de variables globales
'''
C = ConnectDB()
Utils = Utils()
validacionSeguridad = ValidacionSeguridad()
fecha_act = time.ctime()

class Acceso(Form):
    cdgo = StringField(labels.lbl_cdgo,[validators.DataRequired(message=errors.ERR_NO_CDGO_PRGNTA)])
    dscrpcn = StringField(labels.lbl_prgnta,[validators.DataRequired(message=errors.ERR_NO_PRGTA)])
    #dscrpcn_rspsta= StringField(labels.lbl_prgnta,[validators.DataRequired(message=errors.ERR_NO_RSPSTA)])
    #username = StringField(labels.lbl_lgn,[validators.DataRequired(message=errors.ERR_NO_INGSA_USRO)]) 
    #password = StringField(labels.lbl_cntrsna,[validators.DataRequired(message=errors.ERR_NO_INGRSA_CNTRSNA)])
    
class Preguntas(Resource):
  
    def post(self,**kwargs):
       
        if kwargs['page'] == 'listar_preguntasg':
            return self.ObtenerPreguntas()
        elif kwargs['page'] == 'insertar_preguntasg':
            return self.crearPregunta()
            
                       
    def crearPregunta(self):
        u=Acceso(request.form)
        if not u.validate():
            return self.Utils.nice_json({"error":u.errors},400)
        ln_opcn_mnu = request.form["id_mnu"]
        token = request.headers['Authorization']
        validacionSeguridad = ValidacionSeguridad()
        val = validacionSeguridad.Principal(token,ln_opcn_mnu)
        if val:
            print(ln_opcn_mnu)
            DatosUsuarioToken = jwt.decode(token, conf.SS_TKN_SCRET_KEY, 'utf-8')
            datosUsuario = validacionSeguridad.ObtenerDatosUsuario(DatosUsuarioToken['lgn'])[0]
            print(datosUsuario)
            arrayValues={}
            arrayValues2={}
                #arrayvalues3={}
            arrayValues['cdgo']=request.form['cdgo']
            arrayValues['dscrpcn']=request.form['dscrpcn']
            arrayValues['fcha_crcn']=str(fecha_act)
            arrayValues['fcha_mdfccn']=str(fecha_act)
            arrayValues['id_lgn_crcn_ge']=str(datosUsuario['id_lgn_ge'])
            arrayValues['id_lgn_mdfccn_ge']=str(datosUsuario['id_lgn_ge'])  
            id_prgnta=self.crearPregunta(arrayValues,'id')
            #id_pregunta_seguridad=self.C.queryInsert(dbConf.DB_SHMA+".tbpreguntas_seguridad",arrayValues,'id')  
            arrayValues2['id_prgnta_sgrdd']=str(id_prgnta)
            arrayValues2['id_lgn_crcn_ge']=str(datosUsuario['id_lgn_ge'])
            arrayValues2['id_lgn_mdfccn_ge']=str(datosUsuario['id_lgn_ge'])
            arrayValues2['fcha_crcn']=str(fecha_act)
            arrayValues2['fecha_mdfccn']=str(fecha_act)
            arrayValues2['id_lgn_ge']=str(datosUsuario['id_lgn_ge'])
            self.crearPregunta_ge(arrayValues2)
            return self.Utils.nice_json({"error":"Registro Exitoso"},200)
        #return self.C.queryInsert(dbConf.DB_SHMA+".tbpreguntas_seguridad", objectValues,'id')  
        return self.Utils.nice_json({"error":"Sin autorizacion"},400)       
    
    def ObtenerPreguntas(self,parametros):
        u=Acceso(request.form)
        if not u.validate():
            return self.Utils.nice_json({"error":u.errors},400)
        ln_opcn_mnu = request.form["id_mnu"]
        token = request.headers['Authorization']
        validacionSeguridad = ValidacionSeguridad()
        val = validacionSeguridad.Principal(token,ln_opcn_mnu)
        arrayParametros={}
        arrayParametros['cdgo']=request.form['cdgo'] 
        arrayParametros['dscrpcn']=request.form['dscrpcn']
        prmtrs=''
        if parametros:
            cdgo = parametros['cdgo']
            dscrpcn=parametros['dscrpcn']
            if cdgo:
                prmtrs = prmtrs + "  and a.cdgo = " + cdgo
            if dscrpcn:
                prmtrs = prmtrs + "  and a.dscrpcn like '%" + dscrpcn + "%' "
        if val:
            Cursor = C.queryFree(" select "\
                                " a.cdgo,a.dscrpcn "\
                                " from "\
                                " ssi7x.tbpreguntas_seguridad a inner join  ssi7x.tbpreguntas_seguridad_ge b on "\
                                " a.id=b.id_prgnta_sgrdd "\
                                " inner join ssi7x.tblogins_ge c on "\
                                " b.id_lgn_ge=c.id"\
                                " where "\
                                " b.estdo = true "\
                                + prmtrs +
                                " order by "\
                                " a.cdgo")
            if  Cursor :    
                data = json.loads(json.dumps(Cursor, indent=2))
                return Utils.nice_json(data,200)
            else:
                return Utils.nice_json({"error":errors.ERR_NO_RGSTRS},400)  
        else:
            return Utils.nice_json({"error":"Sin Autorizacion"},400)    
    
    def crearPregunta(self,objectValues,table_name):
        return self.C.queryInsert(dbConf.DB_SHMA+"."+str(table_name), objectValues,'id')  
    
    def crearRespuestaPreguntaSeguridad(self,objectValues):
        return self.C.queryInsert(dbConf.DB_SHMA+".tbrespuestas_preguntas_seguridad", objectValues,'id')  
