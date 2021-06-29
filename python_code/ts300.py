from flask.globals import current_app
from lycia import insertarEnTablaAuxiliar, llamarALycia, GenerarDocumento
from __main__ import app, auth_decorator, required_params, BaseSchema
from marshmallow import fields, validate
from flask import request
import json
import collections
from db_adapter.Database import Database
from helper import CustomJSONEncoder, dividirGlosa
from auth import auth
import logging
from datetime import datetime

db = Database()

############################debería ir {modulo}/{programa}
modulo = "/ts"
programa = "/ParametrosIniciales"
servicio = 'ts300'
funcion = 'main'
#############################################################

###################
# ERRORES
###################

#############################################################

class RegistrarParametrosIniciales(BaseSchema):
    numDocContable = fields.Integer(required=True)
    numMesesLinea = fields.Integer(required=True)
    fecLimpieza = fields.Date(required=True)
    marControlEntregaCheques = fields.String(required=True)
    ctaDocCobrarChequeMn = fields.String(required=True)
    aaDocCobrarChequeMn = fields.Integer(required=True)
    ctaDocCobrarChequeMe = fields.String(required=True)
    aaDocCobrarChequeMe = fields.Integer(required=True)
    ctaPuenteCaja = fields.String(required=True)
    ctaTarjetaCredito = fields.String(required=True)
    ctaDocCobrarDadosBaja = fields.String(required=True)
    ctaDifCambio = fields.String(required=True)
    ccoDifCambio = fields.Integer(required=True)
    tipDocCobrarDadosBaja = fields.Integer(required=True)
    aplDocCobrarDadosBaja = fields.Integer(required=True)

###############################
# ALTA DE REGISTROS
# REGISTRA PARAMETROS INICIALES
###############################
@app.route(modulo + programa + '/Registrar', methods=["POST"])
@auth_decorator()
@required_params(RegistrarParametrosIniciales())
def f1000_altas_ts300():
    resultado = {
        'mensaje': 'Guardado correctamente',
        'status': 200
    }
    
    #db = Database()
    funcion = 'f1000_altas_ts300'
    parametros = []
    operacion = "A"

    try:
        datos = request.json
        item = 1

        print(datos)
        sql_insert = """insert into tsctl (tsctlndoc, tsctlnmes, tsctlflim, tsctlmcec, tsctlcchb, tsctlachb, tsctlcchd, tsctlachd, tsctlcpcj, 
                        tsctlctcr, tsctlcpbj, tsctlcdif, tsctlccos, tsctltbdc, tsctlabdc) values(""" + str(datos['numDocContable']) + """, 
                        """ + str(datos['numMesesLinea']) +  """, '""" + datos['fecLimpieza'] + """', '""" + datos['marControlEntregaCheques'] + """',
                        '""" +  str(datos['ctaDocCobrarChequeMn']) +  """', """ +  str(datos['aaDocCobrarChequeMn']) + """, '""" + str(datos['ctaDocCobrarChequeMe']) +  """',
                        """ + str(datos['aaDocCobrarChequeMe']) + """, '""" + datos['ctaPuenteCaja'] + """', '""" +  str(datos['ctaTarjetaCredito']) + """',
                        '""" + datos['ctaDocCobrarDadosBaja'] + """', '""" + datos['ctaDifCambio'] + """', """ +  str(datos['ccoDifCambio']) + """,
                        """ + str(datos['tipDocCobrarDadosBaja']) + """, """ +  str(datos['aplDocCobrarDadosBaja']) +  """)"""

        print(sql_insert)
        db.conectar()
        db.BEGIN_WORK()
        rsp_insert = db.insertar(sql_insert)

        if rsp_insert == 0:
            mensaje = "No se pudo insertar el registro"
            print('f1000_altas_ts300 mensaje: ', mensaje)
            resultado['status'] = 500
            resultado['mensaje'] = mensaje
        else:
            mensaje = "El registro se inserto correctamente"
            print('f1000_altas_ts300 rsp_insert: ', mensaje)
            resultado['mensaje'] = mensaje
        
        db.COMMIT_WORK()

    except Exception as ex:
        db.ROLLBACK_WORK()
        resultado['status'] = 500
        resultado['mensaje'] = str(ex)
    finally:
        db.desconectar()

    return json.dumps(resultado, cls=CustomJSONEncoder), resultado['status']



###########################
# MODIFICACION DE REGISTROS
###########################
class ModificarParametrosIniciales(BaseSchema):
    numDocContable = fields.Integer(required=True)
    numMesesLinea = fields.Integer(required=True)
    fecLimpieza = fields.Date(required=True)
    marControlEntregaCheques = fields.String(required=True)
    ctaDocCobrarChequeMn = fields.String(required=True)
    aaDoCobrarChequeMn = fields.Integer(required=True)
    ctaDocCobrarChequeMe = fields.String(required=True)
    aaDocCobrarChequeMe = fields.Integer(required=True)
    ctaPuenteCaja = fields.String(required=True)
    ctaTarjetaCredito = fields.String(required=True)
    ctaDocCobrarDadosBaja = fields.String(required=True)
    ctaDifCambio = fields.String(required=True)
    ccoDifCambio = fields.Integer(required=True)
    tipDocCobrarDadosBaja = fields.Integer(required=True)
    aplDocCobrarDadosBaja = fields.Integer(required=True)

@app.route(modulo + programa + '/Modificar', methods=["PUT"])
@auth_decorator()
@required_params(ModificarParametrosIniciales())
def f2000_modificar_ts300():
    resultado = {
        'mensaje': 'Actualizado correctamente',
        'status': 200
    }
    
    #db = Database()
    funcion = 'f2000_modificar_ts300'
    operacion = "M"

    try:
        datos = request.json
        item = 1
        
        sql_update = """update tsctl set tsctlnmes = ?, tsctlflim = ?, tsctlmcec = ?, tsctlcchb = ?, tsctlachb = ?, tsctlcchd = ?, tsctlachd = ?,
                        tsctlcpcj = ?, tsctlctcr = ?, tsctlcpbj = ?, tsctlcdif = ?, tsctlccos = ?, tsctltbdc = ?, tsctlabdc = ?
                        where  tsctlndoc = ?""" 

        print(sql_update)
        parametros = (datos['numMesesLinea'], datos['fecLimpieza'], datos['marControlEntregaCheques'], str(datos['ctaDocCobrarChequeMn']), datos['aaDocCobrarChequeMn'], str(datos['ctaDocCobrarChequeMe']), datos['aaDocCobrarChequeMe'], datos['ctaPuenteCaja'], str(datos['ctaTarjetaCredito']), str(datos['ctaDocCobrarDadosBaja']), datos['ctaDifCambio'], datos['ccoDifCambio'], datos['tipDocCobrarDadosBaja'], datos['aplDocCobrarDadosBaja'], datos['numDocContable'],)
        print(parametros)
        
        db.conectar()
        db.BEGIN_WORK()
        rsp_update = db.actualizar(sql_update, parametros)
        print(rsp_update)

        if rsp_update == 0:
            mensaje = "No se encontro el registro solicitado, numDocContable: " + datos['numDocContable'] 
            print('f2000_modificar_ts300 mensaje: ', mensaje)
            resultado['status'] = 500
            resultado['mensaje'] = mensaje
        else:
            mensaje = "El registro " +  str(datos['numDocContable'])  + " se actualizo correctamente"
            print('f2000_modificar_ts300 rsp_update: ', mensaje)
            resultado['mensaje'] = mensaje


        db.COMMIT_WORK()

        
    except Exception as ex:
        #db.ROLLBACK_WORK()
        resultado['status'] = 500
        resultado['mensaje'] = str(ex)
    finally:
        db.desconectar()

    return json.dumps(resultado, cls=CustomJSONEncoder), resultado['status']

class EliminarParametrosIniciales(BaseSchema):
    numDocContable = fields.Integer(required=True)


##################
# BORRAR REGISTROS
##################
@app.route(modulo + programa + '/Eliminar', methods=["DELETE"])
@auth_decorator()
@required_params(EliminarParametrosIniciales())
def f3000_borrar_ts300():
    
    resultado = {
        'mensaje': 'Eliminado correctamente',
        'status': 200
    }
    
    #db = Database()
    funcion = 'f3000_borrar_ts300'
    parametros = []
    operacion = "E"

    try:
        datos = request.json
        item = 1
        
        sql_delete = "delete tsctl" +  " where tsctlndoc = " + datos['numDocContable']  + ""
        print('f3000_borrar_ts300 sql_delete: ', sql_delete)

        db.conectar()
        rsp_delete = db.eliminar(sql_delete)
        
        print('f3000_borrar_ts300 rsp_delete: ', rsp_delete)

        if rsp_delete == 0:
            mensaje = "No se encontro el registro solicitado, numDocContable: " + datos['numDocContable'] 
            print('f3000_borrar_ts300 mensaje: ', mensaje)
            resultado['status'] = 500
            resultado['mensaje'] = mensaje
        else:
            mensaje = "El registro " +  datos['numDocContable']  + " se elimino correctamente"
            print('f3000_borrar_ts300 rsp_delete: ', mensaje)
            resultado['mensaje'] = mensaje

    except Exception as ex:
        resultado['status'] = 500
        resultado['mensaje'] = str(ex)
    finally:
        db.desconectar()

    return json.dumps(resultado, cls=CustomJSONEncoder), resultado['status']
    
#############################################################

@app.route(modulo + programa + '/Buscar', methods=["GET"])
@auth_decorator()
def f5000_buscar_registro_ts300():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5000_buscar_registro_ts300'

    try:
        ctaDocCobrarChequeMn = None
        aaDocCobrarChequeMn = None
        ctaDocCobrarChequeMe = None
        aaDocCobrarChequeMe = None
        
        if 'ctaDocCobrarChequeMn' in  request.args:
            ctaDocCobrarChequeMn =  request.args.get('ctaDocCobrarChequeMn')
            sql_tsctl = "select * from tsctl where tsctlcchd = " + str(ctaDocCobrarChequeMn) + " order by tsctlcchd"
        elif 'aaDocCobrarChequeMn' in  request.args:
            aaDocCobrarChequeMn =  request.args.get('aaDocCobrarChequeMn')
            sql_tsctl = "select * from tsctl where tsctlachd = '" + aaDocCobrarChequeMn + "' order by tsctlachd"
        elif 'ctaDocCobrarChequeMe' in  request.args:
            ctaDocCobrarChequeMe =  request.args.get('ctaDocCobrarChequeMe')
            sql_tsctl = "select * from tsctl where tsctlcpcj = " + ctaDocCobrarChequeMe + " order by tsctlcpcj"
        elif 'aaDocCobrarChequeMe' in  request.args:
            aaDocCobrarChequeMe =  request.args.get('aaDocCobrarChequeMe')
            sql_tsctl = "select * from tsctl where tsctlctcr = " + aaDocCobrarChequeMe + " order by tsctlctcr"
        else:
            sql_tsctl = "select * from tsctl"

        db.conectar()
        rsp_tsctl = db.query(sql_tsctl)
        ary_tsctl = []
        i = 0
        print('RSP: ', rsp_tsctl)
        for item in rsp_tsctl:
            i_tsctl = collections.OrderedDict()
            print('Fecha: ', item['tsctlflim'])
            if item['tsctlflim'] == None:
                fechaLimpieza = ''
                
            else:
                fechaLimpieza = str(item['tsctlflim'])

            ary_tsctl.append({
                'numDocContable' : str(item['tsctlndoc']).strip(),
                'numMesesLinea' : str(item['tsctlnmes']).strip(),
                'fecLimpieza' : fechaLimpieza,
                'marControlEntregaCheques' : str(item['tsctlmcec']).strip(),
                'ctaDocCobrarChequeMn' : str(item['tsctlcchb']).strip(),
                'aaDocCobrarChequeMn' : str(item['tsctlachb']).strip(),
                'ctaDocCobrarChequeMe' : str(item['tsctlcchd']).strip(),
                'aaDocCobrarChequeMe' : str(item['tsctlachd']).strip(),
                'ctaPuenteCaja' : str(item['tsctlcpcj']).strip(),
                'ctaTarjetaCredito' : str(item['tsctlctcr']).strip(),
                'ctaDocCobrarDadosBaja' : str(item['tsctlcpbj']).strip(),
                'ctaDifCambio' : str(item['tsctlcdif']).strip(),
                'ccoDifCambio' : str(item['tsctlccos']).strip(),
                'tipDocCobrarDadosBaja' : str(item['tsctltbdc']).strip(),
                'aplDocCobrarDadosBaja' : str(item['tsctlabdc']).strip()
            })

        result['parametrosInicialesTsctl'] = ary_tsctl
        result['total'] = len(ary_tsctl)
        result['mensaje'] = "Cargado Correctamente"
        mensaje = json.dumps(ary_tsctl)
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

@app.route(modulo + programa + '/ConsultarTipoDeCuentas', methods=["GET"])
@auth_decorator()
def f5030_buscar_cptcp_ts300():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5030_buscar_cptcp_ts300'

    try:
        codigoTipoCuentas = None
        marcaAplicacionDiferida = None
        claseCuenta = None
        
        if 'codigoTipoCuentas' in  request.args:
            codigoTipoCuentas =  request.args.get('codigoTipoCuentas')
            sql_cptcp = "select * from cptcp where cptcpclsc = 2 and cptcpctcp = " + codigoTipoCuentas
        elif 'marcaAplicacionDiferida' in  request.args:
            marcaAplicacionDiferida =  request.args.get('marcaAplicacionDiferida')
            sql_cptcp = "select * from cptcp where cptcpapld = '" + marcaAplicacionDiferida + "'"
        elif 'claseCuenta' in  request.args:
            claseCuenta =  request.args.get('claseCuenta')
            sql_cptcp = "select * from cptcp where cptcpclsc = " + str(claseCuenta) + ""
        else:
            sql_cptcp = "select * from cptcp"

        db.conectar()
        rsp_cptcp = db.query(sql_cptcp)
        ary_cptcp = []
        i = 0
        print('RSP: ', rsp_cptcp)
        for item in rsp_cptcp:
            i_cptcp = collections.OrderedDict()
            '''print('Fecha: ', item['cptcpflim'])
            if item['cptcpflim'] == None:
                fechaLimpieza = ''
                
            else:
                fechaLimpieza = str(item['cptcpflim'])'''

            ary_cptcp.append({
                'claseCuenta' : str(item['cptcpclsc']).strip(), 
                'codigoTipoCuenta' : str(item['cptcpctcp']).strip(),
                'descripcion' : str(item['cptcpdesc']).strip(),
                'abreviacion' : str(item['cptcpabre']).strip(),
                'cuentaContableBsReg' : str(item['cptcpctai']).strip(),
                'analisisAdicionalBsReg' : str(item['cptcpanai']).strip(),
                'cuentaContableUsReg' : str(item['cptcpctac']).strip(),
                'analsisAdicionalUsReg' : str(item['cptcpanac']).strip(),
                'marcaAplicacionDiferida' : str(item['cptcpapld']).strip(),
                'cuentaContableBsDif' : str(item['cptcpctdi']).strip(),
                'analisisAdicionalBsDif' : str(item['cptcpandi']).strip(),
                'cuentaContableBsDif' : str(item['cptcpctdc']).strip(),
                'analsisAdicionalUsDif' : str(item['cptcpandc']).strip(),
                'centroCosto' : str(item['cptcpccos']).strip()
            })

        result['tipoCuentasCptcp'] = ary_cptcp
        result['total'] = len(ary_cptcp)
        result['mensaje'] = "Cargado Correctamente"
        mensaje = json.dumps(ary_cptcp)
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

@app.route(modulo + programa + '/ConsultarAplicaciones', methods=["GET"])
@auth_decorator()
def f5040_buscar_cpapl_ts300():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5040_buscar_cpapl_ts300'

    try:
        codigoAplicacion = None
        claseCuenta = None
        
        if 'codigoAplicacion' in  request.args:
            codigoAplicacion =  request.args.get('codigoAplicacion')
            sql_cpapl = "select * from cpapl where cpaplclsc = 2 and cpaplcapl = " + str(codigoAplicacion)
        elif 'claseCuenta' in  request.args:
            claseCuenta =  request.args.get('claseCuenta')
            sql_cpapl = "select * from cpapl where cpaplclsc = " + str(claseCuenta) + ""
        else:
            sql_cpapl = "select * from cpapl"

        db.conectar()
        rsp_cpapl = db.query(sql_cpapl)
        ary_cpapl = []
        i = 0
        print('RSP: ', rsp_cpapl)
        for item in rsp_cpapl:
            i_cpapl = collections.OrderedDict()
            
            ary_cpapl.append({
                'claseCuenta' : str(item['cpaplclsc']).strip(), 
                'codigoAplicacion' : str(item['cpaplcapl']).strip(),
                'descripcion' : str(item['cpapldesc']).strip(), 
                'tipoAplicacion' : str(item['cpapltapl']).strip(),
                'cuentaContable' : str(item['cpaplcctb']).strip(),
                'analisisAdicional' : str(item['cpapladic']).strip(),
                'gastoExcento' : str(item['cpaplgexe']).strip()
            })

        result['aplicacionesCpapl'] = ary_cpapl
        result['total'] = len(ary_cpapl)
        result['mensaje'] = "Cargado Correctamente"
        mensaje = json.dumps(ary_cpapl)
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']