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
from SSI7X.AuthUsers import ValidaToken,AutenticacionUsuarios
import SSI7X.Static.config_DB as dbConf # @UnresolvedImport   
import SSI7X.Static.config as conf  # @UnresolvedImport 
import jwt #@UnresolvedImport
import time
from SSI7X.ValidacionSeguridad import ValidacionSeguridad  # @UnresolvedImport

class Acceso(Form):
    dscrpcn_prgnta = StringField(labels.lbl_prgnta,[validators.DataRequired(message=errors.ERR_NO_PRGTA)])
    #dscrpcn_rspsta= StringField(labels.lbl_prgnta,[validators.DataRequired(message=errors.ERR_NO_RSPSTA)])
    #username = StringField(labels.lbl_lgn,[validators.DataRequired(message=errors.ERR_NO_INGSA_USRO)]) 
    #password = StringField(labels.lbl_cntrsna,[validators.DataRequired(message=errors.ERR_NO_INGRSA_CNTRSNA)])
    
class Preguntas(Resource):
    C = ConnectDB() 
    Utils = Utils()
    def post(self):
        u=Acceso(request.form)
        if not u.validate():
            return self.Utils.nice_json({"error":u.errors},400)

        ln_opcn_mnu = request.form["id_mnu"]
        fecha_act = time.ctime()
        token = request.headers['Authorization']
        validacionSeguridad = ValidacionSeguridad()
        val = validacionSeguridad.Principal(token,ln_opcn_mnu)
        print("-------------------")
        print(val)
        print("-------------------")
        if val:
            print(ln_opcn_mnu)
            DatosUsuarioToken = jwt.decode(token, conf.SS_TKN_SCRET_KEY, 'utf-8')
            print(DatosUsuarioToken['lgn'])
            datosUsuario = validacionSeguridad.ObtenerDatosUsuario(DatosUsuarioToken['lgn'])[0]
            print(datosUsuario)
            arrayValues={}
            arrayvalues2={}
            arrayvalues3={}
            arrayValues['dscrpcn']=request.form['dscrpcn_prgnta']
            arrayValues['fcha_crcn']=str(fecha_act)
            arrayValues['fcha_mdfccn']=str(fecha_act)
            arrayValues['id_lgn_crcn_ge']=str(datosUsuario['id_lgn_ge'])
            arrayValues['id_lgn_mdfccn_ge']=str(datosUsuario['id_lgn_ge'])    
            id = self.crearPregunta(arrayValues)
            print (id)
            return self.Utils.nice_json({"error":"NULL"},200)
            '''id_pregunta_seguridad = self.crearPregunta(arrayValues)
            arrayvalues2['id_prgnta_sgrdd']=str(id_pregunta_seguridad)
            arrayvalues2['id_lgn_crcn_ge']=str(id_lgn_prfl_scrsl)
            arrayvalues2['id_lgn_mdfccn_ge']=str(id_lgn_prfl_scrsl)
            arrayvalues2['fcha_crcn']=str(fecha_act)
            arrayvalues2['fecha_mdfccn']=str(fecha_act)
            arrayvalues2['id_lgn_ge']=str(id_lgn_prfl_scrsl)
            #self.crearPreguntaGe(arrayvalues2)
            id_pregunta_seguridad_ge=self.crearPreguntaGe(arrayvalues2)
            arrayvalues3['rspsta']=request.form['dscrpcn_rspsta']
            arrayvalues3['id_prgnta_sgrdd_ge']=str(id_pregunta_seguridad_ge)
            arrayvalues3['id_lgn_accso']=str(id_lgn_prfl_scrsl)
            self.crearRespuestaPreguntaSeguridad(arrayvalues3) 
            print("2")        '''
        return self.Utils.nice_json({"error":"Sin autorizacion"},400) 
        
    def crearPregunta(self,objectValues):
        return self.C.queryInsert(dbConf.DB_SHMA+".tbpreguntas_seguridad", objectValues,'id')        
    
    def crearPreguntaGe(self,objectValues):
        return self.C.queryInsert(dbConf.DB_SHMA+".tbpreguntas_seguridad_ge", objectValues,'id')  
    
    def crearRespuestaPreguntaSeguridad(self,objectValues):
        return self.C.queryInsert(dbConf.DB_SHMA+".tbrespuestas_preguntas_seguridad", objectValues,'id')  
