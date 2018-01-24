'''
Created on 22/01/2018

@author: CRISTIAN.BOTINA
'''

from flask_restful import request, Resource
from wtforms import Form, validators, StringField
from SSI7X.Static.ConnectDB import ConnectDB  # @UnresolvedImport
from SSI7X.Static.Utils import Utils  # @UnresolvedImport
import SSI7X.Static.errors as errors  # @UnresolvedImport
import SSI7X.Static.labels as labels  # @UnresolvedImport

class Acceso(Form):
    name = StringField(labels.lbl_nmbr_usrs,[validators.DataRequired(message=errors.ERR_NO_NOBRE)])
    username = StringField(labels.lbl_lgn,[validators.DataRequired(message=errors.ERR_NO_INGSA_USRO)]) 
    password = StringField(labels.lbl_cntrsna,[validators.DataRequired(message=errors.ERR_NO_INGRSA_CNTRSNA)])
    #user_photo = StringField(labels.lbl_cntrsna,[validators.DataRequired(message=errors.ERR_NO_FTO)])

class Usuarios(Resource):
    C = ConnectDB()
    Utils = Utils()

    def post(self):
        print('hello word!')
        u = Acceso(request.form)
        if not u.validate(): 
            return self.Utils.nice_json({"error":u.errors},400)
        
    def ObtenerUsuarios(self,usuario):
        cursor = self.C.queryFree(" select " \
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
                             " end as crro_elctrnco," \
                             " lgn_ge.id as id_lgn_ge, " \
                             " lgn.lgn as lgn " \
                             " from ssi7x.tblogins_ge lgn_ge " \
                             " left join ssi7x.tblogins lgn on lgn.id = lgn_ge.id_lgn " \
                             " left join ssi7x.tbempleados_une emplds_une on emplds_une.id_lgn_accso_ge = lgn_ge.id " \
                             " left join ssi7x.tbempleados emplds on emplds.id = emplds_une.id_empldo " \
                             " left join ssi7x.tbprestadores prstdr on prstdr.id_lgn_accso_ge = lgn_ge.id " \
                             " where lgn.lgn = '"+usuario+"'")
        return cursor
    