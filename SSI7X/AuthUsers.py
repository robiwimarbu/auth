import hashlib,socket,json # @UnresolvedImport
from IPy import IP
from flask import make_response # @UnresolvedImpor
from flask_restful import request, Resource
from wtforms import Form, validators, StringField
from SSI7X.Static.ConnectDB import ConnectDB  # @UnresolvedImport
from SSI7X.Static.Utils import Utils  # @UnresolvedImport
from SSI7X.Static.Ldap_connect import Conexion_ldap # @UnresolvedImport
from urllib.parse import urlparse
import SSI7X.Static.errors as errors  # @UnresolvedImport
import SSI7X.Static.labels as labels  # @UnresolvedImport
import SSI7X.Static.config as conf  # @UnresolvedImport
import SSI7X.Static.config_DB as dbConf # @UnresolvedImport
from user_agents import parse 
import jwt #@UnresolvedImport
from _codecs import decode

class UsuarioAcceso(Form):
    username = StringField(labels.lbl_nmbr_usrs,[validators.DataRequired(message=errors.ERR_NO_INGSA_USRO)])
    password = StringField(labels.lbl_cntrsna_usrs,[validators.DataRequired(message=errors.ERR_NO_INGRSA_CNTRSNA)])
    
class UsroCmbioCntrsna(Form):
    cntrsna = StringField(labels.lbl_cntrsna_usrs,[validators.DataRequired(message=errors.ERR_NO_INGRSA_CNTRSNA)])
    cntrsna_nva = StringField(labels.lbl_nva_cntrsna,[validators.DataRequired(message=errors.ERR_NO_DB_INGRSR_NVA_CNTRSNA),validators.Length(min=conf.PW_MN_SIZE,message=errors.ERR_NO_MNM_CRCTRS),validators.Regexp('(?=.*\d)',message=errors.ERR_NO_MNMO_NMRO),validators.Regexp('(?=.*[A-Z])',message=errors.ERR_NO_MNMO_MYSCLA)])
    tkn = StringField('el token', [validators.DataRequired(message='Falta el token'),validators.Length(min=conf.SS_TKN_SIZE,message=errors.ERR_NO_TKN_INVLDO)])
    
class AutenticacionUsuarios(Resource):
    C = ConnectDB()
    Utils = Utils()
    def post(self):
        ingreso=False
        u = UsuarioAcceso(request.form)
        if not u.validate():
            return self.Utils.nice_json({"error":u.errors},400)
        IpUsuario = IP(socket.gethostbyname(socket.gethostname()))
        if IpUsuario.iptype() == 'PUBLIC':
            md5= hashlib.md5(request.form['password'].encode('utf-8')).hexdigest() 
            Cursor = self.C.querySelect(dbConf.DB_SHMA +'.tblogins', 'lgn,cntrsna', "lgn='"+ request.form['username']+ "' and  cntrsna='"+md5+"'")
            if Cursor :
                if type(self.validaUsuario(request.form['username'])) is dict:
                    ingreso=True                  
                else:
                    return self.validaUsuario(request.form['username'])
            else:
                ingreso               
        elif IpUsuario.iptype() == 'PRIVATE':
            Cldap = Conexion_ldap()
            VerificaConexion = Cldap.Conexion_ldap(request.form['username'], request.form['password'])
            if VerificaConexion :
                if type(self.validaUsuario(request.form['username'])) is dict:
                    ingreso=True                  
                else:
                    error = str(self.validaUsuario(request.form['username']))
                    return self.Utils.nice_json({"error":error},400)    
            else:
                ingreso                 
                
        if  ingreso:
            data = json.loads(json.dumps(self.ObtenerDatosUsuario(request.form['username'])[0], indent=2))
            token = jwt.encode(data, conf.SS_TKN_SCRET_KEY, algorithm='HS256').decode('utf-8')
            arrayValues={}
            device=self.DetectarDispositivo() 
            arrayValues['ip']=str(IpUsuario)
            arrayValues['dspstvo_accso']=str(device)
            arrayValues['id_lgn_ge']=str(data['id_lgn_ge'])
            self.InsertGestionAcceso(arrayValues)
            response = make_response( '{"access_token":"'+str(token)+'"}',200)
            response.headers['Content-type'] = "application/json"
            response.headers['charset']="utf-8"
            response.headers["Access-Control-Allow-Origin"]= "*"
            response.headers["Set-cookie"]=str(token)
            return response
        else:
            return self.Utils.nice_json({"error":errors.ERR_NO_USRO_CNTSN_INVLD},400)
                
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
                             " lgn_ge.id as id_lgn_ge, " \
                             " lgn.lgn as lgn " \
                             " from ssi7x.tblogins_ge lgn_ge " \
                             " left join ssi7x.tblogins lgn on lgn.id = lgn_ge.id_lgn " \
                             " left join ssi7x.tbempleados_une emplds_une on emplds_une.id_lgn_accso_ge = lgn_ge.id " \
                             " left join ssi7x.tbempleados emplds on emplds.id = emplds_une.id_empldo " \
                             " left join ssi7x.tbprestadores prstdr on prstdr.id_lgn_accso_ge = lgn_ge.id " \
                             " where lgn.lgn = '"+usuario+"'")
        return cursor
    
            
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
        
    def DetectarDispositivo(self):
            str_agente = request.headers.get('User-Agent')
            dispositivo_usuario = parse(str_agente)
            return dispositivo_usuario
        
    def InsertGestionAcceso(self,objectValues):
        self.C.queryInsert(dbConf.DB_SHMA+".tbgestion_accesos", objectValues)        


class  MenuDefectoUsuario(Resource):
    def post(self): 
        valida_token = ValidaToken()
        AutenticaUsuarios = AutenticacionUsuarios()
        token = request.headers['Authorization']
        if token:
            valida_token = valida_token.ValidacionToken(token) 
            C = ConnectDB()
            if valida_token :
                DatosUsuario = jwt.decode(token, conf.SS_TKN_SCRET_KEY, 'utf-8')
                id_lgn_prfl_scrsl = AutenticaUsuarios.validaUsuario(DatosUsuario['lgn'])
                
                if type(id_lgn_prfl_scrsl) is not dict:
                    return id_lgn_prfl_scrsl
                
                Cursor = C.queryFree(" select "\
                                    " c.dscrpcn as text , "\
                                    " b.id_mnu as id ,"\
                                    " c.id_mnu as parentid ,"\
                                    " c.lnk "\
                                    " FROM ssi7x.tblogins_perfiles_menu a INNER JOIN "\
                                    " ssi7x.tbmenu_ge b on a.id_mnu_ge=b.id INNER JOIN "\
                                    " ssi7x.tbmenu c ON b.id_mnu = c.id "\
                                    " where a.estdo=true "\
                                    " and b.estdo=true "\
                                    " and a.id_lgn_prfl_scrsl = "+str(id_lgn_prfl_scrsl['id_prfl_scrsl'])+" ORDER BY "\
                                    " cast(c.ordn as integer)")
                if Cursor :    
                    data = json.loads(json.dumps(Cursor, indent=2))
                    return AutenticaUsuarios.Utils.nice_json(data,200)
                else:
                    return AutenticaUsuarios.Utils.nice_json({"error":errors.ERR_NO_USRO_SN_MNU},400)
            else:
                return AutenticaUsuarios.Utils.nice_json({"error":errors.ERR_NO_SN_SSN},400)
            
        else:
            return AutenticaUsuarios.Utils.nice_json({"error":errors.ERR_NO_SN_PRMTRS},400)
        
        
class CmboCntrsna(Resource):
    def post(self):
        u = UsroCmbioCntrsna(request.form)
        if not u.validate():
            return self.Utils.nice_json({"status":"Error","error":u.errors,"user":"null"})
        
class BusquedaImagenUsuario(Resource):
    C = ConnectDB()
    Utils = Utils()
   
    def post(self):
        lc_url = request.url
        lc_prtcl = urlparse(lc_url)    
        Cursor = self.C.queryFree(" select "\
                                 " id ,"\
                                 " lgn ,"\
                                 " fto_usro,"\
                                 " nmbre_usro, "\
                                 " estdo "\
                                 " from ssi7x.tblogins where lgn = '"+str(request.form['username'])+"'")
        if Cursor :
            data = json.loads(json.dumps(Cursor[0], indent=2))
            if data['estdo']:
                if data['fto_usro']:
                    return self.Utils.nice_json({"fto_usro":lc_prtcl.scheme+'://'+conf.SV_HOST+':'+str(conf.SV_PORT)+'/static/img/'+data['fto_usro']},200)
                else:
                    return self.Utils.nice_json({"fto_usro":"null"},200)
            else:
                return self.Utils.nice_json({"error":errors.ERR_NO_TNE_PRFL,lc_prtcl.scheme+'://'+"fto_usro":conf.SV_HOST+':'+str(conf.SV_PORT)+'/static/img/'+data['fto_usro']},200)
        else:
            return self.Utils.nice_json({"error":errors.ERR_NO_TNE_PRMTDO_ACCDR},400)
        
class ValidaToken(Resource):
    Utils = Utils()
    def ValidacionToken(self,token):
        try:
            decode = jwt.decode(token, conf.SS_TKN_SCRET_KEY, 'utf-8')
            return True
        except jwt.exceptions.ExpiredSignatureError:
            return  False     
        