from _codecs import decode
from flask_restful import Resource
from SSI7X.Static.ConnectDB import ConnectDB  # @UnresolvedImport
from SSI7X.Static.Utils import Utils  # @UnresolvedImport
import SSI7X.Static.errors as errors  # @UnresolvedImport
import SSI7X.Static.config as conf  # @UnresolvedImport
import jwt #@UnresolvedImport
import json # @UnresolvedImport

#clase para manejo de permisos por usuario menu 
class ValidacionSeguridad(Resource):
    Utils = Utils()
    C = ConnectDB()
    def Principal(self,token,id_mnu):
        if not token and id_mnu:
            return False
        DatosUsuario = jwt.decode(token, conf.SS_TKN_SCRET_KEY, 'utf-8')
        if DatosUsuario:
            lo_datos = self.validaUsuario(DatosUsuario['lgn'])
            return self.ValidaOpcionMenu(lo_datos['id_prfl_scrsl'], id_mnu)
        else:
            False
        
    def validaUsuario(self, usuario):
        IdUsuarioGe = json.loads(json.dumps(self.ObtenerDatosUsuario(usuario)[0], indent=2))
        strQuery = "SELECT "\
                    " a.id as id_prfl_scrsl,"\
                    " b.nmbre_scrsl as nmbre_scrsl,"\
                    " c.estdo as estdo "\
                    " FROM ssi7x.tblogins_perfiles_sucursales a"\
                    " left JOIN  ssi7x.tbsucursales b on a.id_scrsl=b.id"\
                    " left join ssi7x.tblogins_ge c on c.id = a.id_lgn_ge"\
                    " WHERE  a.id_lgn_ge = "+str(IdUsuarioGe['id_lgn_ge'])+" and a.mrca_scrsl_dfcto is true"
        Cursor = self.C.queryFree(strQuery)
        
        if Cursor :
            data = json.loads(json.dumps(Cursor[0], indent=2))
            if data['estdo']:
                return data
            else:
                return errors.ERR_NO_USRO_INCTVO
        else:
            return errors.ERR_NO_TNE_PRFL  
         
     
    def ValidacionToken(self,token):
        try:
            decode = jwt.decode(token, conf.SS_TKN_SCRET_KEY, 'utf-8')
            return True
        except jwt.exceptions.ExpiredSignatureError:
            return  False     
    
    def ValidaOpcionMenu(self,id_lgn_prfl_scrsl,id_mnu):
            Cursor =  self.C.queryFree(" select a.id "\
                                 " from ssi7x.tblogins_perfiles_menu a inner join "\
                                     " ssi7x.tblogins_perfiles_sucursales b "\
                                     " on a.id_lgn_prfl_scrsl = b.id inner join "\
                                     " ssi7x.tblogins_ge c on c.id = b.id_lgn_ge inner join "\
                                     " ssi7x.tbmenu_ge d on d.id = a.id_mnu_ge inner join "\
                                     " ssi7x.tbmenu e on e.id = d.id_mnu "\
                                     " where c.estdo=true "\
                                     " and b.estdo=true "\
                                     " and a.estdo=true "\
                                     " and e.id = "+str(id_mnu)+" and a.id_lgn_prfl_scrsl = "+str(id_lgn_prfl_scrsl))                   
            if Cursor:
                return True
            else:
                return False
    
    def ObtenerDatosUsuario(self,usuario):
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
                             " lgn_ge.id as id_lgn_ge," \
                             " lgn.lgn as lgn," \
                             " lgn_ge.id_grpo_emprsrl grpo_emprsrl,"\
                             " prfl_scrsl.id_scrsl,"\
                             " prfl_une.id_undd_ngco undd_ngco "\
                             " from ssi7x.tblogins_ge lgn_ge " \
                             " left join ssi7x.tblogins lgn on lgn.id = lgn_ge.id_lgn " \
                             " left join ssi7x.tbempleados_une emplds_une on emplds_une.id_lgn_accso_ge = lgn_ge.id " \
                             " left join ssi7x.tbempleados emplds on emplds.id = emplds_une.id_empldo " \
                             " left join ssi7x.tbprestadores prstdr on prstdr.id_lgn_accso_ge = lgn_ge.id " \
                             " left join ssi7x.tblogins_perfiles_sucursales  prfl_scrsl on prfl_scrsl.id_lgn_ge = lgn_ge.id"\
                             " left join ssi7x.tbperfiles_une prfl_une on prfl_une.id = prfl_scrsl.id_prfl_une"\
                             " where lgn.lgn = '"+usuario+"' and prfl_scrsl.mrca_scrsl_dfcto = true")
        return cursor