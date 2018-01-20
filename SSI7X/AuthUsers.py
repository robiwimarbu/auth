import hashlib, os,socket,json,secrets # @UnresolvedImport
from IPy import IP
from flask import session
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

mySession={}
class UsuarioAcceso(Form):
    username = StringField(labels.lbl_nmbr_usrs,[validators.DataRequired(message=errors.ERR_NO_02)])
    password = StringField(labels.lbl_cntrsna_usrs,[validators.DataRequired(message=errors.ERR_NO_03)])
    
class UsroCmbioCntrsna(Form):
    cntrsna = StringField(labels.lbl_cntrsna_usrs,[validators.DataRequired(message=errors.ERR_NO_03)])
    cntrsna_nva = StringField(labels.lbl_nva_cntrsna,[validators.DataRequired(message=errors.ERR_NO_04),validators.Length(min=conf.PW_MN_SIZE,message=errors.ERR_NO_06),validators.Regexp('(?=.*\d)',message=errors.ERR_NO_08),validators.Regexp('(?=.*[A-Z])',message=errors.ERR_NO_07)])
    tkn = StringField('el token', [validators.DataRequired(message='Falta el token'),validators.Length(min=conf.SS_TKN_SIZE,message=errors.ERR_NO_05)])
    
class AutenticacionUsuarios(Resource):
    C = ConnectDB()
    Utils = Utils()
    def post(self):
        ingreso=False
        u = UsuarioAcceso(request.form)
        #print(request.headers)
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
                #session['logged_in'] = False
                ingreso               
        elif IpUsuario.iptype() == 'PRIVATE':
            Cldap = Conexion_ldap()
            VerificaConexion = Cldap.Conexion_ldap(request.form['username'], request.form['password'])
            if VerificaConexion :
                if self.ObtenerDatosUsuario(request.form['username']):
                    ingreso=True                  
                else:
                    ingreso         
            else:
                ingreso#que doble hp                 
                
        if  ingreso:
            token = secrets.token_hex(conf.SS_TKN_SIZE)
            data = json.loads(json.dumps(self.ObtenerDatosUsuario(request.form['username'])[0], indent=2))
            #session['logged_in'] = True
            mySession[str(token)]=data
            session[str(token)] = data
            print(mySession)
            arrayValues={}
            device=self.DetectarDispositivo() 
            arrayValues['ip']=str(IpUsuario)
            arrayValues['key']=token
            arrayValues['dspstvo_accso']=str(device)
            arrayValues['id_lgn_ge']=str(data['id_lgn_ge'])
            self.InsertGestionAcceso(arrayValues)
            #print(token)
            #print("--------------------------------------")
            return self.Utils.nice_json({"access_token":str(token)},200)
        else:
            session['logged_in'] = False
            return self.Utils.nice_json({"error":errors.ERR_NO_01},400)
                
    def ObtenerDatosUsuario(self,usuario):
        print("obtener "+ usuario )
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
        print(usuario)
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
                return self.Utils.nice_json({"error":errors.ERR_NO_11},400)
        else:
            return self.Utils.nice_json({"error":errors.ERR_NO_10},400)
        
    def DetectarDispositivo(self):
            str_agente = request.headers.get('User-Agent')
            dispositivo_usuario = parse(str_agente)
            return dispositivo_usuario
        
    def InsertGestionAcceso(self,objectValues):
        self.C.queryInsert(dbConf.DB_SHMA+".tbgestion_accesos", objectValues)        


class  MenuDefectoUsuario(Resource):
    def post(self):
        #print(request.form['data'])
        valida_token = ValidaToken()
        AutenticaUsuarios = AutenticacionUsuarios()
        token = request.form['data']
        if token:
            valida_token = valida_token.ValidacionToken(token) 
            C = ConnectDB()
            if valida_token :
                DatosUsuario = mySession.get(token)
                print(DatosUsuario.get('lgn'))
                id_lgn_prfl_scrsl = AutenticaUsuarios.validaUsuario(DatosUsuario.get('lgn'))
               
                Cursor = C.queryFree(" select "\
                                    " b.id_mnu as id ,"\
                                    " c.id_mnu as parent ,"\
                                    " c.dscrpcn , "\
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
                    return AutenticaUsuarios.Utils.nice_json({"error":errors.ERR_NO_14},400)
            else:
                return AutenticaUsuarios.Utils.nice_json({"error":errors.ERR_NO_12},400)
            
        else:
            return AutenticaUsuarios.Utils.nice_json({"error":errors.ERR_NO_13},400)
        
        
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
                    return self.Utils.nice_json({"fto_usro":data['fto_usro']},200)
                    #return self.Utils.nice_json({"fto_usro":lc_prtcl.scheme+'://'+conf.SV_HOST+':'+str(conf.SV_PORT)+'/'+data['fto_usro']},200)
                else:
                    return self.Utils.nice_json({"fto_usro":data['fto_usro']},200)
                    #return self.Utils.nice_json({"fto_usro":"null"},200)
            else:
                return self.Utils.nice_json({"error":errors.ERR_NO_11,"fto_usro":data['fto_usro']},200)
                #return self.Utils.nice_json({"error":errors.ERR_NO_11,lc_prtcl.scheme+'://'+"fto_usro":conf.SV_HOST+':'+str(conf.SV_PORT)+'/'+data['fto_usro']},200)
        else:
            return self.Utils.nice_json({"error":errors.ERR_NO_10},400)
        
class ValidaToken(Resource):
    Utils = Utils()
    def ValidacionToken(self,token):
        if mySession.get(token):
            return True
        else:
            return False     
        