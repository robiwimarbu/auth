from SSI7X.Static.ConnectDB import ConnectDB  # @UnresolvedImport
from SSI7X.Static.Utils import Utils  # @UnresolvedImport
import SSI7X.Static.config_DB as dbConf # @UnresolvedImport
from flask_restful import request, Resource
from wtforms import Form, validators, StringField
from SSI7X.Static import labels
import SSI7X.Static.errors as errors  # @UnresolvedImport


##clase de llamado para validar datos desde labels
class DatosPerfil(Form):
    cdgo = StringField(labels.lbl_cdgo_prfl,[validators.DataRequired(message=errors.ERR_NO_Cdgo)])
    dscrpcn = StringField(labels.lbl_dscrpcn_prfl,[validators.DataRequired(message=errors.ERR_NO_Dscrpcn)])
     
class CrearPerfil(Resource):
    C = ConnectDB()
    Utils = Utils()
    def post(self):
        lob_rspsta = DatosPerfil(request.form)
        print(lob_rspsta)
