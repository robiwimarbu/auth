from SSI7X.Static.ConnectDB import ConnectDB  # @UnresolvedImport
from SSI7X.Static.Utils import Utils  # @UnresolvedImport
from flask_restful import request, Resource
from wtforms import Form, validators, StringField
import SSI7X.Static.labels as labels # @UnresolvedImport
from SSI7X.ValidacionSeguridad import ValidacionSeguridad  # @UnresolvedImport
import SSI7X.Static.errors as errors  # @UnresolvedImport
import SSI7X.Static.config_DB as dbConf # @UnresolvedImport
import jwt
import SSI7X.Static.config as conf  # @UnresolvedImport

##clase de llamado para validar datos desde labels
class DatosPerfil(Form):
    cdgo = StringField(labels.lbl_cdgo_prfl,[validators.DataRequired(message=errors.ERR_NO_Cdgo)])
    dscrpcn = StringField(labels.lbl_dscrpcn_prfl,[validators.DataRequired(message=errors.ERR_NO_Dscrpcn)])
    
class CrearPerfil(Resource):
    Utils = Utils()
    lc_cnctn = ConnectDB()
    def post(self):
        lob_rspsta = DatosPerfil(request.form)
        print(lob_rspsta)
        if not lob_rspsta.validate(): 
            return self.Utils.nice_json({"error":lob_rspsta.errors},400)
        
        ln_opcn_mnu = request.form["id_mnu"]
        token = request.headers['Authorization']
        validacionSeguridad = ValidacionSeguridad()
        
        if validacionSeguridad.Principal(token, ln_opcn_mnu):
            arrayValues={}
            #arrayValues['id_lgn_ge']=str(data['id_lgn_ge'])
            #arrayValues['id_lgn_ge']=str(data['id_lgn_ge'])
            self.InsertGestionAcceso(arrayValues)
                        
        else:
            return self.Utils.nice_json({"error":"null"},400)