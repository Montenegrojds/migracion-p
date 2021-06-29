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
programa = "/CuentasBancos"
servicio = 'ts302'
funcion = 'main'
#############################################################

###################
# ERRORES
###################
@app.route(modulo + programa + '/ErroresBaseDatos', methods=["GET"])
@auth_decorator()
def f0500_error_gb000():
    l_desc = None
    status = 200
    mensaje = None
    funcion = 'f0500_error_gb000'

    try:
        sql_gberr = "select * from gberr"
        #sql_gberr = "select gberrdesc as l_desc from gberr" WHERE gberrcerr = l_cerr
        db.conectar()
        rsp_gberr = db.query(sql_gberr)
        ary_gberr = []
        i = 0
        print(rsp_gberr)
        for t1 in rsp_gberr:
            i_gberr = collections.OrderedDict()
            i_gberr["value"] = str(t1)
            ary_gberr.append(dict(i_gberr))
        mensaje = json.dumps(ary_gberr)
    except Exception as ex:
        status = 500
        mensaje = str(ex)
        print (mensaje)
    finally:
        db.desconectar()
    return {'status':status, 'mensaje':(mensaje)}


class RegistrarCuentasBancos(BaseSchema):
    numeroBanco = fields.Integer(required=True)
    numeroCuenta = fields.String(required=True)
    unidadNegocio = fields.Integer(required=True)
    moneda = fields.Integer(required=True)
    saldoDisponible = fields.Decimal(required=True)
    sobregiroContratado = fields.Decimal(required=True)
    cuentaContable = fields.String(required=True)
    analisisAdicional = fields.Integer(required=True)
    manejaChequeras = fields.String(required=True)
    marcaLlenadoCheque = fields.String(required=True)
    habilitada = fields.Integer(required=True)

###################
# ALTA DE REGISTROS
###################
@app.route(modulo + programa + '/Registrar', methods=["POST"])
@auth_decorator()
@required_params(RegistrarCuentasBancos())
def f1000_altas_ts302():
    resultado = {
        'mensaje': 'Guardado correctamente',
        'status': 200
    }
    
    #db = Database()
    funcion = 'f1000_altas_ts302'
    parametros = []
    operacion = "A"

    try:
        datos = request.json
        item = 1

        sql_insert = "insert into tsccb (tsccbcbco, tsccbncta, tsccbuneg, tsccbcmon, tsccbsald, tsccbsgro, tsccbcctb, tsccbadic, tsccbmcch, tsccbmlch, tsccbstat) values(" + str(datos['numeroBanco']) + ", '" + str(datos['numeroCuenta']) +  "', " + str(datos['unidadNegocio']) + ", " + str(datos['moneda']) + ", " +  str(datos['saldoDisponible']) + ", " + str(datos['sobregiroContratado']) + ", " +  datos['cuentaContable'] + ", " +  str(datos['analisisAdicional']) + ", '" +  datos['manejaChequeras'] +  "', '" +  datos['marcaLlenadoCheque'] + "', " +   str(datos['habilitada']) + ")"
        
        db.conectar()
        db.BEGIN_WORK()

        rsp_insert = db.insertar(sql_insert)

        if rsp_insert == 0:
            mensaje = "No se pudo insertar el registro"
            print('f1000_altas_ts302 mensaje: ', mensaje)
            resultado['status'] = 500
            resultado['mensaje'] = mensaje
        else:
            mensaje = "El registro se inserto correctamente"
            print('f1000_altas_ts302 rsp_insert: ', mensaje)
            resultado['mensaje'] = mensaje
        
        print(sql_insert)

        if datos['manejaChequeras'] == "N" and datos['marcaLlenadoCheque'] == "S":
            sql_insert = "insert into tsich (tsichcbco, tsichncta, tsichlbco, tsichlmic, tsichplza, tsichfmto) values(" + str(datos['numeroBanco']) + ", " + datos['numeroCuenta'] + ", " + "0" + "0" + ")" 

        '''if g_mcfi == "S":
            if t2.tscbacpry is None:
                t2.tscbacpry == 0
            if t2.tscbacprg is None: 
                t2.tscbacprg == 0
            if t2.tscbacfin is None:
                t2.tscbacfin == 0

            sql_insert = "INSERT INTO tscba"'''

        db.COMMIT_WORK()

        if(datos['numeroCuenta'] is not None):  
            operacion = "M" 
        else:
            operacion = "A"

        
        
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
class ModificarCuentasBancos(BaseSchema):
    numeroBanco = fields.Integer(required=True)
    numeroCuenta = fields.String(required=True)
    unidadNegocio = fields.Integer(required=True)
    moneda = fields.Integer(required=True)
    saldoDisponible = fields.Decimal(required=True)
    sobregiroContratado = fields.Decimal(required=True)
    cuentaContable = fields.String(required=True)
    analisisAdicional = fields.Integer(required=True)
    manejaChequeras = fields.String(required=True)
    marcaLlenadoCheque = fields.String(required=True)
    habilitada = fields.Integer(required=True)

@app.route(modulo + programa + '/Modificar', methods=["PUT"])
@auth_decorator()
@required_params(ModificarCuentasBancos())
def f2000_modificar_ts302():
    resultado = {
        'mensaje': 'Actualizado correctamente',
        'status': 200
    }
    
    #db = Database()
    funcion = 'f2000_modificar_ts302'
    parametros = []
    operacion = "M"

    try:
        datos = request.json
        item = 1
        
        sql_update = "update tsccb set tsccbcbco = " + str(datos['numeroBanco']) + ", tsccbuneg = " + str(datos['unidadNegocio']) + ", tsccbcmon = " + str(datos['moneda']) +  ", tsccbsald = " + str(datos['saldoDisponible']) + ", tsccbsgro = " + str(datos['sobregiroContratado']) + ", tsccbcctb = " + datos['cuentaContable'] + ", tsccbadic = " + str(datos['analisisAdicional']) + ", tsccbmcch = '" + datos['manejaChequeras'] + "', tsccbmlch = '" + datos['marcaLlenadoCheque'] + "', tsccbstat = " + str(datos['habilitada']) + "  where tsccbncta = '" + datos['numeroCuenta']  + "'"
        print(sql_update)

        db.conectar()
        db.BEGIN_WORK()
        rsp_update = db.actualizar(sql_update)
        
        if rsp_update == 0:
            mensaje = "No se encontro el registro solicitado, numeroCuenta: " + datos['numeroCuenta'] 
            print('f2000_modificar_ts302 mensaje: ', mensaje)
            resultado['status'] = 500
            resultado['mensaje'] = mensaje
        else:
            mensaje = "El registro " +  str(datos['numeroCuenta'])  + " se actualizo correctamente"
            print('f2000_modificar_ts302 rsp_update: ', mensaje)
            resultado['mensaje'] = mensaje
        
        print(rsp_update)

        if datos['manejaChequeras'] == "N" and datos['marcaLlenadoCheque'] == "S":
            sql_insert = "insert into tsich (tsichcbco, tsichncta, tsichlbco, tsichlmic, tsichplza, tsichfmto) values(" + str(datos['numeroBanco']) + ", " + datos['numeroCuenta'] + ", " + "0" + "0" + ")" 

        '''if g_mcfi == "S":
            if t2.tscbacpry is None:
                t2.tscbacpry == 0
            if t2.tscbacprg is None: 
                t2.tscbacprg == 0
            if t2.tscbacfin is None:
                t2.tscbacfin == 0

            sql_insert = "INSERT INTO tscba"'''

        db.COMMIT_WORK()

        if(datos['numeroCuenta'] is not None):  
            operacion = "M" 
        else:
            operacion = "A"

        
        
    except Exception as ex:
        db.ROLLBACK_WORK()
        resultado['status'] = 500
        resultado['mensaje'] = str(ex)
    finally:
        db.desconectar()

    return json.dumps(resultado, cls=CustomJSONEncoder), resultado['status']

class EliminarCuentasBancos(BaseSchema):
    numeroCuenta= fields.Integer(required=True)


##################
# BORRAR REGISTROS
##################
@app.route(modulo + programa + '/Eliminar', methods=["DELETE"])
@auth_decorator()
@required_params(EliminarCuentasBancos())
def f3000_borrar_ts302():
    
    resultado = {
        'mensaje': 'Eliminado correctamente',
        'status': 200
    }
    
    #db = Database()
    funcion = 'f3000_borrar_ts302'
    parametros = []
    operacion = "E"

    try:
        datos = request.json
        item = 1
        
        sql_delete = "delete tsccb" +  " where tsccbncta = '" + datos['numeroCuenta']  + "'"
        print(sql_delete)

        db.conectar()
        db.BEGIN_WORK()
        rsp_delete = db.eliminar(sql_delete)
    
        print(rsp_delete)

        print('f3000_borrar_ts302 rsp_delete: ', rsp_delete)

        if rsp_delete == 0:
            mensaje = "No se encontro el registro solicitado, numeroCuenta: " + datos['numeroCuenta'] 
            print('f3000_borrar_ts302 mensaje: ', mensaje)
            resultado['status'] = 500
            resultado['mensaje'] = mensaje
        else:
            print('f3000_borrar_ts302 rsp_delete: ', "El registro " +  datos['numeroCuenta']  + " se elimino correctamente")
        
        

        '''if datos['manejaChequeras'] == "N" and datos['marcaLlenadoCheque'] == "S":
            sql_insert = "insert into tsich (tsichcbco, tsichncta, tsichlbco, tsichlmic, tsichplza, tsichfmto) values(" + str(datos['numeroBanco']) + ", " + datos['numeroCuenta'] + ", " + "0" + "0" + ")" 

        if g_mcfi == "S":
            if t2.tscbacpry is None:
                t2.tscbacpry == 0
            if t2.tscbacprg is None: 
                t2.tscbacprg == 0
            if t2.tscbacfin is None:
                t2.tscbacfin == 0

            sql_insert = "INSERT INTO tscba"'''
        db.COMMIT_WORK()

        if(datos['numeroCuenta'] is not None):  
            operacion = "M" 
        else:
            operacion = "A"

        
        
    except Exception as ex:
        db.ROLLBACK_WORK()
        resultado['status'] = 500
        resultado['mensaje'] = str(ex)
    finally:
        db.desconectar()

    return json.dumps(resultado, cls=CustomJSONEncoder), resultado['status']
    
#############################################################

@app.route(modulo + programa + '/ConsultaDatosCuentas', methods=["GET"])
@auth_decorator()
def f4000_consulta_ts302():
    #Busca datos en la tabla Tscba si no ecuentra busca en la Tsccb Ambas traen cuentas en bancos
    l_cont = -1
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f4000_consulta_ts302'
    try:
        sql_tscba = "select * from tscba"
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_tscba)
        db.conectar()
        rsp_tscba = db.query(sql_tscba)
        print(rsp_tscba)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_tscba)
        db.desconectar()
        array = []

        if rsp_tscba is None:
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, 'Tabla tscba vacia')
            l_cont = 0
            print('Tabla tscba vacia')
        else:
            for item in rsp_tscba:
                print(item)
                l_cont = str(item.l_cont)
                i_tscba = collections.OrderedDict()
                
                array.append({
                        'numeroBanco' : str(item['tscbacbco']).strip(),
                        'numeroCuenta' : str(item['tscbancta']).strip(),
                        'codigoProyecto' : str(item['tscbacpry']).strip(),
                        'codigoPrograma' : str(item['tscbacprg']).strip(),
                        'codigoFinanciador' : str(item['tscbacfin']).strip()
                    })
                result['cuentasEnBancosTscba'] = array
                result['total'] = len(array)

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, l_cont)
        
        if l_cont == 0:
            array = f4050_consulta_ts302()
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, array)
            print("RSP: ", array) 
        '''else:
            print(test)
            result['respuesta'] = rsp
            result['total'] = len(rsp)'''
    
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        logging.info('ERROR : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
    finally:
        logging.info('ERROR : [%s] [%s] [%s]', servicio, funcion, 'finally')
    return json.dumps(array, cls=CustomJSONEncoder), result['status']

#############################################################

@app.route(modulo + programa + '/ConsultaDatosProyecto', methods=["GET"])
@auth_decorator()
def f4001_consulta_ts302():
    #Trae todos los campos de la tabla Tscba Cuentas en Bancos
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f4001_consulta_ts302'
    try:
        sql_tscba = "select * from tscba order by tscbacbco, tscbancta"
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_tscba)
        db.conectar()
        rsp_tscba = db.query(sql_tscba)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_tscba)
        array = []
        i = 0
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_tscba)
        print(rsp_tscba)
        if rsp_tscba is None:
            result['mensaje'] = 'No se encuentran registros'
            result['total'] = 0
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_tscba:
                i_tscba = collections.OrderedDict()
                logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, i_tscba)
                array.append({
                    'numeroBanco' : str(item['tscbacbco']).strip(),
                    'numeroCuenta' : str(item['tscbancta']).strip(),
                    'codigoProyecto' : str(item['tscbacpry']).strip(),
                    'codigoPrograma' : str(item['tscbacprg']).strip(),
                    'codigoFinanciador' : str(item['tscbacfin']).strip()
                })
            result['datosProyectoTscba'] = array
            result['total'] = len(array)
            result['mensaje'] = "Cargado Correctamente"
        
        
        

    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        logging.info('ERROR : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
       
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

@app.route(modulo + programa + '/ConsultaCuentas', methods=["GET"])
@auth_decorator()
def f0202_selec_cursor_ts900():
    #Trae todos los campos de la tabla Tsccb Cuentas en Bancos, puedes filtrar por codigoBanco y codigoCuenta
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f0202_selec_cursor_ts900'
    try:
        codigoBanco = None
        codigoCuenta = None
        
        if 'codigoBanco' in  request.args:
            codigoBanco =  request.args.get('codigoBanco')
            sql_tsccb = "select * from tsccb where tsccbcbco = " + str(codigoBanco) + " order by tsccbcbco, tsccbncta"
        elif 'codigoCuenta' in  request.args:
            codigoCuenta =  request.args.get('codigoCuenta')
            sql_tsccb = "select * from tsccb where tsccbncta = '" + codigoCuenta + "' order by tsccbcbco, tsccbncta"
        else:
            sql_tsccb = "select * from tsccb order by tsccbcbco, tsccbncta"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_tsccb)

        db.conectar()
        rsp_tsccb = db.query(sql_tsccb)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_tsccb)
        array = []
        i = 0
        print(rsp_tsccb)

        if rsp_tsccb is None:
            result['mensaje'] = 'No se encuentran registros'
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_tsccb:
                i_tsccb = collections.OrderedDict()
                #i_tsccb["value"] = str(t1.tsccbcbco) +" - "+ str(t1.tsccbncta)  +" - "+ str(t1.tsccbuneg)
                #i_tsccb["value"] = str(item)
                array.append({
                    'numeroBanco' : str(item['tsccbcbco']).strip(),
                    'numeroCuenta' : str(item['tsccbncta']).strip(),
                    'unidadNegocio' : str(item['tsccbuneg']).strip(),
                    'moneda' : str(item['tsccbcmon']).strip(),
                    'saldoDisponible' : str(item['tsccbsald']).strip(),
                    'sobregiroContratado' : str(item['tsccbsgro']).strip(),
                    'cuentaContable' : str(item['tsccbcctb']).strip(),
                    'analisisAdicional' : str(item['tsccbadic']).strip(),
                    'manejaChequeras' : str(item['tsccbmcch']).strip(),
                    'marcaLlenadoCheque' : str(item['tsccbmlch']).strip(),
                  
                    'habilitada' : str(item['tsccbstat']).strip()
                })
            result['mensaje'] = "Cargado Correctamente"

        result['cuentasBancosTsccb'] = array
        result['total'] = len(array)
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        logging.info('ERROR : [%s] [%s] [%s]', servicio, funcion, mensaje)
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

@app.route(modulo + programa + '/ConsultaCuentasBanco', methods=["GET"])
@auth_decorator()
def f4050_consulta_ts302():
    #Trae todos los campos de la tabla Tsccb Cuentas en Bancos
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f4050_consulta_ts302'

    try:
        #sql_tsccb = "select tsccbcbco, tsccbncta, tsccbuneg from tsccb order by tsccbcbco,tsccbncta"
        sql_tsccb = "select * from tsccb order by tsccbcbco,tsccbncta"
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_tsccb)
        db.conectar()
        rsp_tsccb = db.query(sql_tsccb)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_tsccb)
        array = []
        i = 0
        print(rsp_tsccb)
        if rsp_tsccb is None:
            result['mensaje'] = 'No se encuentran registros'
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_tsccb:
                i_tsccb = collections.OrderedDict()
                #i_tsccb["value"] = str(t1.tsccbcbco) +" - "+ str(t1.tsccbncta)  +" - "+ str(t1.tsccbuneg)
                array.append({
                        'numeroBanco' : str(item['tsccbcbco']).strip(),
                        'numeroCuenta' : str(item['tsccbncta']).strip(),
                        'unidadNegocio' : str(item['tsccbuneg']).strip(),
                        'moneda' : str(item['tsccbcmon']).strip(),
                        'saldoDisponible' : str(item['tsccbsald']).strip(),
                        'sobregiroContratado' : str(item['tsccbsgro']).strip(),
                        'cuentaContable' : str(item['tsccbcctb']).strip(),
                        'analisisAdicional' : str(item['tsccbadic']).strip(),
                        'manejaChequeras' : str(item['tsccbmcch']).strip(),
                        'marcaLlenadoCheque' : str(item['tsccbmlch']).strip(),
                    
                        'habilitada' : str(item['tsccbstat']).strip()
                    })
            result['mensaje'] = "Cargado Correctamente"

        result['cuentasBancosTsccb'] = array
        result['total'] = len(array)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        logging.info('ERROR : [%s] [%s] [%s]', servicio, funcion, mensaje)
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################
@app.route(modulo + programa + '/ConsultaCuentasCompletas', methods=["GET"])
@auth_decorator()
def f4100_consulta_ts302():
    #Cruza la tabla Tscba con la Tsccb, usa FULL OUTER JOIN
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f4100_consulta_ts302'

    try:
        #sql_tsccb_tscba = "SELECT * FROM tsccb  JOIN tscba  ON  tsccbcbco = tscbacbco AND tsccbncta = tscbancta ORDER BY tsccbcbco,tsccbncta"
        sql_tsccb_tscba = "SELECT * FROM tsccb  FULL OUTER JOIN tscba  ON  tsccbcbco = tscbacbco AND tsccbncta = tscbancta ORDER BY tsccbcbco,tsccbncta"
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_tsccb_tscba)
        db.conectar()
        rsp_tsccb_tscba = db.query(sql_tsccb_tscba)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_tsccb_tscba)
        array= []
        i = 0
        print(rsp_tsccb_tscba)
        if rsp_tsccb_tscba is None:
            result['mensaje'] = 'No se encuentran registros'
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_tsccb_tscba:
                i_tsccb = collections.OrderedDict()
                array.append({
                        'numeroBanco' : str(item['tsccbcbco']).strip(),
                        'numeroCuenta' : str(item['tsccbncta']).strip(),
                        'unidadNegocio' : str(item['tsccbuneg']).strip(),
                        'moneda' : str(item['tsccbcmon']).strip(),
                        'saldoDisponible' : str(item['tsccbsald']).strip(),
                        'sobregiroContratado' : str(item['tsccbsgro']).strip(),
                        'cuentaContable' : str(item['tsccbcctb']).strip(),
                        'analisisAdicional' : str(item['tsccbadic']).strip(),
                        'manejaChequeras' : str(item['tsccbmcch']).strip(),
                        'marcaLlenadoCheque' : str(item['tsccbmlch']).strip(),
                        'habilitada' : str(item['tsccbstat']).strip(),
                        'codigoProyecto' : str(item['tscbacpry']).strip(),
                        'codigoPrograma' : str(item['tscbacprg']).strip(),
                        'codigoFinanciador' : str(item['tscbacfin']).strip()
                    })

            result['mensaje'] = "Cargado Correctamente"
            
        result['cuentasTscbaTsccb'] = array
        result['total'] = len(array)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        logging.info('ERROR : [%s] [%s] [%s]', servicio, funcion, mensaje)
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

################################################################
### busqueda bancos
#############################################################
@app.route(modulo + programa + '/ConstantesGlobales', methods=["GET"])
@auth_decorator()
def f5010_buscar_gbcon_ts302():
    #11 bancos 10 monedas 21 ciudad
    #Trae todos los campos de la tabla Gbcon Conceptos Globales
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5010_buscar_gbcon_ts302'

    try:
        codigoGlobal = None
        
        if 'codigoGlobal' in  request.args:
            codigoGlobal =  request.args.get('codigoGlobal')
            sql_gbcon = "select * from gbcon where gbconpfij = " + codigoGlobal
        else:
            sql_gbcon = "select * from gbcon"
        
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_gbcon)
        db.conectar()
        rsp_gbcon = db.query(sql_gbcon)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_gbcon)

        array = []
        i = 0
        print(rsp_gbcon)

        if rsp_gbcon is None:
            result['mensaje'] = 'No se encuentran registros'
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_gbcon:
                i_gbcon = collections.OrderedDict()
                array.append({
                    'prefijoConcepto' : str(item['gbconpfij']).strip(),
                    'correlativoConcepto' : str(item['gbconcorr']).strip(),
                    'descripcionConcepto' : str(item['gbcondesc']).strip(),
                    'abreviacionConcepto' : str(item['gbconabre']).strip()
                })

            result['mensaje'] = "Cargado Correctamente"
       
        if codigoGlobal == "10":
                result['monedasGbcon'] = array
        elif codigoGlobal == "11":
                result['bancosGbcon'] = array
        elif codigoGlobal == "21":
                result['plazasGbcon'] = array
        else:
            result['respuestaGbcon'] = array

        result['total'] = len(array)
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        logging.info('ERROR : [%s] [%s] [%s]', servicio, funcion, mensaje)
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################
@app.route(modulo + programa + '/PlanDeCuentas', methods=["GET"])
@auth_decorator()
def f5020_buscar_cnplc_ts302():
    #Trae todos los campos de la tabla Cnplc Plan de Cuentas
    g_tcon = None
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5020_buscar_cnplc_ts302'

    try:
        sql_cnplc = "select * from cnplc"
        #sql_cnplc = "select cnplctcon as g_tcon from cnplc"
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_cnplc)
        db.conectar()
        rsp_cnplc = db.query(sql_cnplc)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_cnplc)
        array = []
        i = 0
        print(rsp_cnplc)
        if rsp_cnplc is None:
            result['mensaje'] = 'No se encuentran registros'
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_cnplc:
                i_cnplc = collections.OrderedDict()
                array.append({
                        'codigoCuenta' : str(item['cnplccnta']).strip(),
                        'nombreCuetnta' : str(item['cnplcnomb']).strip(),
                        'moneda' : str(item['cnplccmon']).strip(),
                        'obligaCentroCosto' : str(item['cnplcmcco']).strip(),
                        'tipoAnalisisAdicional' : str(item['cnplctcon']).strip(),
                        'usuario' : str(item['cnplcuser']).strip(),
                        'hora' : str(item['cnplchora']).strip(),
                        'fechaProceso' : str(item['cnplcfpro']).strip()
                    })
            result['mensaje'] = "Cargado Correctamente"

        result['respuestaCnplc'] = array
        result['total'] = len(array)
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        logging.info('ERROR : [%s] [%s] [%s]', servicio, funcion, mensaje)
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################
@app.route(modulo + programa + '/AnalisisAdicional', methods=["GET"])
@auth_decorator()
def f5030_buscar_cncnp_ts302():
    #Trae todos los campos de la tabla Cncnp Analisis Adicional
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5030_buscar_cncnp_ts302'

    try:
        sql_cncnp = "select * from cncnp"
        #sql_cncnp = "select cncnpdesc from cncnp" where cncnptcon = g_tcon AND cncnpncon = t1.tsccbadic

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_cncnp)
        db.conectar()
        rsp_cncnp = db.query(sql_cncnp)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_cncnp)
        array = []
        i = 0
        print(rsp_cncnp)

        if rsp_cncnp is None:
            result['mensaje'] = 'No se encuentran registros'
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_cncnp:
                i_cncnp = collections.OrderedDict()
                array.append({
                        'tipoAnalisis' : str(item['cncnptcon']).strip(),
                        'numeroAnalisis' : str(item['cncnpncon']).strip(),
                        'descripcion' : str(item['cncnpdesc']).strip()
                    })
            result['mensaje'] = "Cargado Correctamente"
           
        result['respuestaCncnp'] = array
        result['total'] = len(array)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        logging.info('ERROR : [%s] [%s] [%s]', servicio, funcion, mensaje)
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################
@app.route(modulo + programa + '/ConsultaUnidadNegocios', methods=["GET"])
@auth_decorator()
def f5040_buscar_cnune_ts302():
    #Trae todos los campos de la tabla Cnune Unidad de Negocio
    g_dune = None
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5040_buscar_cnune_ts302'

    try:
        sql_cnune = "select cnuneuneg, cnunedesc as g_dune, cnunecreg from cnune"# where cnuneuneg=t1.tsccbuneg"
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_cnune)
        db.conectar()
        rsp_cnune = db.query(sql_cnune)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_cnune)
        array = []
        i = 0
        print(rsp_cnune)

        if rsp_cnune is None:
            result['mensaje'] = 'No se encuentran registros'
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_cnune:
                i_cnune = collections.OrderedDict()
                array.append({
                        'unidadNegocio' : str(item['cnuneuneg']).strip(),
                        'descripcion' : str(item['g_dune']).strip(),
                        'codigoRegional' : str(item['cnunecreg']).strip()
                    })
            result['mensaje'] = "Cargado Correctamente"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, array)
       
        result['respuestaCnune'] = array
        result['total'] = len(array)
    
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        logging.info('ERROR : [%s] [%s] [%s]', servicio, funcion, mensaje)
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################
@app.route(modulo + programa + '/FormatoBanco', methods=["GET"])
@auth_decorator()
def f5050_buscar_tsfcb_ts302():
    #Trae todos los campos de la tabla Tsfcb Formatos por Banco para Impresion de Cheques  
    g_dfto = None
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5050_buscar_tsfcb_ts302'

    try:
        sql_tsfcb = "select * from tsfcb"
        #sql_tsfcb = "select tsfcbdesc as g_dfto from tsfcb" #where tsfcbfmto = g_fmto
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_tsfcb)
        db.conectar()
        rsp_tsfcb = db.query(sql_tsfcb)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_tsfcb)
        array = []
        i = 0
        print(rsp_tsfcb)

        if rsp_tsfcb is None:
            result['mensaje'] = 'No se encuentran registros'
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_tsfcb:
                i_tsfcb = collections.OrderedDict()
                array.append({
                        'codigoFormato' : str(item['tsfcbfmto']).strip(),
                        'descripcion' : str(item['tsfcbdesc']).strip()
                    })
            result['mensaje'] = "Cargado Correctamente"

        result['respuestaTsfcb'] = array
        result['total'] = len(array)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        logging.info('ERROR : [%s] [%s] [%s]', servicio, funcion, mensaje)
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################
@app.route(modulo + programa + '/ConsultaProyectos', methods=["GET"])
@auth_decorator()
def f5060_buscar_eppry_ts302():
    #Trae todos los campos de la tabla Eppry Proyectos
    g_dpry = None
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5060_buscar_eppry_ts302'

    try:
        sql_eppry = "select *, epprynomb as g_dpry from eppry" #where epprycpry = l_cpry
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_eppry)
        db.conectar()
        rsp_eppry = db.query(sql_eppry)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_eppry)
        array = []
        i = 0
        print(rsp_eppry)

        if rsp_eppry is None:
            result['mensaje'] = 'No se encuentran registros'
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_eppry:
                i_eppry = collections.OrderedDict()
                array.append({
                        'codigoProyecto' : str(item['epprycpry']).strip(),
                        'nombreProyecto' : str(item['epprynomb']).strip(),
                        'nombreCortoProyecto' : str(item['epprynomc']).strip(),
                        'descripcion' : str(item['epprydesc']).strip(),
                        'fechaRegistro' : str(item['eppryfreg']).strip(),
                        'fechaInicio' : str(item['eppryfini']).strip(),
                        'fechaFin' : str(item['eppryffin']).strip(),
                        'monedaProyecto' : str(item['epprycmon']).strip(),
                        'cuentaDiferida' : str(item['epprycdif']).strip(),
                        'cuentaDonacionProducto' : str(item['epprycdon']).strip(),
                        'usuario' : str(item['eppryuser']).strip(),
                        'hora' : str(item['eppryhora']).strip(),
                        'fechaProceso' : str(item['eppryfpro']).strip()
                    })
            result['mensaje'] = "Cargado Correctamente"

        result['respuestaEppry'] = array
        result['total'] = len(array)
       
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        logging.info('ERROR : [%s] [%s] [%s]', servicio, funcion, mensaje)
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

@app.route(modulo + programa + '/ConsultaProgramasProyectos', methods=["GET"])
@auth_decorator()
def f5070_buscar_epprg_ts302():
    #Trae todos los campos de la tabla Eeprg Programas por Proyectos
    g_dprg = None
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5070_buscar_epprg_ts302'

    try:
        sql_epprg = "select *, epprgdesc as g_dprg from epprg" #where epprgcpry = l_cpry AND epprgcprg = l_cprg
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_epprg)
        db.conectar()
        rsp_epprg = db.query(sql_epprg)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_epprg)
        array = []
        i = 0
        print(rsp_epprg)

        if rsp_epprg is None:
            result['mensaje'] = 'No se encuentran registros'
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_epprg:
                i_epprg = collections.OrderedDict()
                array.append({
                        'codigoProyecto' : str(item['epprgcpry']).strip(),
                        'nombrePrograma' : str(item['epprgcprg']).strip(),
                        'descripcion' : str(item['epprgdesc']).strip(),
                        'fechaRegistro' : str(item['epprgfreg']).strip(),
                        'fechaInicio' : str(item['epprgfini']).strip(),
                        'fechaFin' : str(item['epprgffin']).strip(),
                        'moneda' : str(item['epprgcmon']).strip(),
                        'montoProyectoPresupuestado' : str(item['epprgmont']).strip(),
                        'montoEjecutado' : str(item['epprgmeje']).strip(),
                        'usuario' : str(item['epprguser']).strip(),
                        'hora' : str(item['epprghora']).strip(),
                        'fechaProceso' : str(item['epprgfpro']).strip()
                    })
            result['mensaje'] = "Cargado Correctamente"

        result['respuestaEpprg'] = array
        result['total'] = len(array)
       
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        logging.info('ERROR : [%s] [%s] [%s]', servicio, funcion, mensaje)
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################
@app.route(modulo + programa + '/ConsultaFinanciadorRegistroClientes', methods=["GET"])
@auth_decorator()
def f5080_buscar_cfin_ts302():
    #Trae todos los campos de la tabla Epfin Financiador cruzada con Gbage Registro de Clientes
    g_dfin = None
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5080_buscar_cfin_ts302'

    try:
        sql_epfin_gbage = "select *, gbagenomb as g_dfin from epfin JOIN gbage ON epfincfin = gbagecage" #AND epfincfin = l_cfin  
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_epfin_gbage)
        db.conectar()
        rsp_epfin_gbage = db.query(sql_epfin_gbage)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_epfin_gbage)
        array = []
        i = 0
        print(rsp_epfin_gbage)

        if rsp_epfin_gbage is None:
            result['mensaje'] = 'No se encuentran registros'
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_epfin_gbage:
                i_epfin_gbage = collections.OrderedDict()
                array.append({
                        'financiadorCodigoAgenda' : str(item['epfincfin']).strip(),
                        'tipoFinanciador' : str(item['epfintfin']).strip(),
                        'fechaRegistro' : str(item['epfinfreg']).strip(),

                        'codigoAgenda' : str(item['gbagecage']).strip(),
                        'razonSocial' : str(item['gbagenomb']).strip(),
                        'tipoDocumentoIdentidad' : str(item['gbagetdid']).strip(),
                        'documentoIdentidad' : str(item['gbagendid']).strip(),
                        'ruc' : str(item['gbagenruc']).strip(),
                        'tipoPersona' : str(item['gbagetper']).strip(),
                        'fechaNacimiento' : str(item['gbagefnac']).strip(),
                
                        'sexo' : str(item['gbagesexo']).strip()
                    })
            result['mensaje'] = "Cargado Correctamente"

        result['respuestaEpfinGbage'] = array
        result['total'] = len(array)
      
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        logging.info('ERROR : [%s] [%s] [%s]', servicio, funcion, mensaje)
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################
@app.route(modulo + programa + '/ConsultaRegistroClientes', methods=["GET"])
@auth_decorator()
def f5085_buscar_gbage_ts302():
    #Trae todos los campos de la tabla Gbage Registros de Clientes
    g_dfin = None
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5085_buscar_gbage_ts302'

    try:
        sql_gbage = "select * from gbage"  
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_gbage)
        db.conectar()
        rsp_gbage = db.query(sql_gbage)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_gbage)
        array = []
        i = 0
        print(rsp_gbage)

        if rsp_gbage is None:
            result['mensaje'] = 'No se encuentran registros'
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_gbage:
                i_gbage = collections.OrderedDict()
                array.append({
                        'codigoAgenda' : str(item['gbagecage']).strip(),
                        'razonSocial' : str(item['gbagenomb']).strip(),
                        'tipoDocumentoIdentidad' : str(item['gbagetdid']).strip(),
                        'documentoIdentidad' : str(item['gbagendid']).strip(),
                        'ruc' : str(item['gbagenruc']).strip(),
                        'tipoPersona' : str(item['gbagetper']).strip(),
                        'sexo' : str(item['gbagesexo']).strip(),
                        'estadoCivil' : str(item['gbageeciv']).strip(),
                        'nacionalidad' : str(item['gbagenaci']).strip(),
                        'fechaNacimiento' : str(item['gbagefnac']).strip(),
                        'profesion' : str(item['gbageprof']).strip(),
                        'direccionEnvioCorrespondencia1' : str(item['gbagedir1']).strip()
                    })
            result['mensaje'] = "Cargado Correctamente"

        result['respuestaGbage'] = array
        result['total'] = len(array)
     
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        logging.info('ERROR : [%s] [%s] [%s]', servicio, funcion, mensaje)
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################
@app.route(modulo + programa + '/ConsultaFinanciador', methods=["GET"])
@auth_decorator()
def f5086_buscar_gbage_ts302():
    #Trae todos los campos de la tabla Epfin Financiador
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5086_buscar_gbage_ts302'

    try:
        sql_epfin = "select * from epfin"  
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_epfin)
        db.conectar()
        rsp_epfin = db.query(sql_epfin)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_epfin)
        array = []
        i = 0
        print(rsp_epfin)

        if rsp_epfin is None:
            result['mensaje'] = 'No se encuentran registros'
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_epfin:
                i_epfin = collections.OrderedDict()
                array.append({
                        'financiadorCodigoAgenda' : str(item['epfincfin']).strip(),
                        'tipoFinanciador' : str(item['epfintfin']).strip(),
                        'fechaRegistro' : str(item['epfinfreg']).strip()
                    })
            result['mensaje'] = "Cargado Correctamente"
        result['respuestaEpfin'] = array
        result['total'] = len(array)
       
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        logging.info('ERROR : [%s] [%s] [%s]', servicio, funcion, mensaje)
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################
@app.route(modulo + programa + '/ConsultaFinanciadorProyecto', methods=["GET"])
@auth_decorator()
def f5090_buscar_cfin_ts302():
    #Trae todos los campos de la tabla Epfip Financiadores por proyecto
    g_dfin = None
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5090_buscar_cfin_ts302'

    try:
        sql_epfip = "select * from epfip " #AND epfincfin = l_cfin  
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_epfip)
        db.conectar()
        rsp_epfip = db.query(sql_epfip)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_epfip)
        array = []
        i = 0
        print(rsp_epfip)

        if rsp_epfip is None:
            result['mensaje'] = 'No se encuentran registros'
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_epfip:
                i_epfip = collections.OrderedDict()
                array.append({
                        'codigoProyecto' : str(item['epfipcpry']).strip(),
                        'financiadorAgenda' : str(item['epfipcfin']).strip()
                    })
            result['mensaje'] = "Cargado Correctamente"

        result['respuestaEpfip'] = array
        result['total'] = len(array)
       
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        logging.info('ERROR : [%s] [%s] [%s]', servicio, funcion, mensaje)
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']




#############################################################
@app.route(modulo + programa + '/ReglasNegocio', methods=["GET"])
@auth_decorator()
def f6050_buscar_empresa_ts302():
    #Trae todos los campos de la tabla Gbrne Reglas de Negocio
    g_mcfi = None
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f6050_buscar_empresa_ts302'

    try:
        
        #gbrne Reglas de negocio
        #sql_gbrne = "select * FROM gbrne"
        sql_gbrne = "select * FROM gbrne"
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_gbrne)
        db.conectar()
        rsp_gbrne = db.query(sql_gbrne)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_gbrne)
        array = []
        i = 0
        print(rsp_gbrne)

        if rsp_gbrne is None:
            result['mensaje'] = 'No se encuentran registros'
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_gbrne:
                i_gbrne = collections.OrderedDict()
                array.append({
                    'permitirStockNegativo' : str(item['gbrnesneg']).strip(),
                    'modificarPrecioVenta' : str(item['gbrnempre']).strip(),
                    'modificarPrecioVentaAutorizacion' : str(item['gbrnempca']).strip(),
                    'porcentajeVariacionPrecioVentaNegativa' : str(item['gbrnepvpn']).strip(),
                    'porcentajeVariacionPrecioVentaPositiva' : str(item['gbrnepvpp']).strip(),
                    'modificarDescuento' : str(item['gbrnemdes']).strip(),
                    'modificarDescuentoAutorizacion' : str(item['gbrnemdca']).strip(),
                    'porcentajeVariacionDescuentoNegativo' : str(item['gbrnepvdn']).strip(),
                    'porcentajeVariacionDescuentoPositivo' : str(item['gbrnepvdp']).strip()
                })

            result['mensaje'] = "Cargado Correctamente"
        result['respuestaGbrne'] = array
        result['total'] = len(array)
    
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        logging.info('ERROR : [%s] [%s] [%s]', servicio, funcion, mensaje)
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################
@app.route(modulo + programa + '/ContabilidadPorFinanciadores', methods=["GET"])
@auth_decorator()
def f6051_buscar_empresa_ts302():
    #Trae todos los campos de la tabla Gbrne Reglas de Negocio solo el campo Contabilidad por financiadores
    g_mcfi = None
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f6051_buscar_empresa_ts302'

    try:
        #gbrne Reglas de negocio
        #gbrnemcfi Contabilidad p/financiadores (S/N)
        sql_gbrne = "select gbrnemcfi as g_mcfi FROM gbrne"
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_gbrne)
        db.conectar()
        rsp_gbrne = db.query(sql_gbrne)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_gbrne)
        array = []
        i = 0
        print(rsp_gbrne)

        if rsp_gbrne is None:
            result['mensaje'] = 'No se encuentran registros'
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_gbrne:
                i_gbrne = collections.OrderedDict()
                array.append({
                    'contabilidadPorFinanciadores' : str(item['g_mcfi']).strip()
                })

            result['mensaje'] = "Cargado Correctamente"

        result['respuestaGbrne'] = array
        result['total'] = len(array)
   
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        logging.info('ERROR : [%s] [%s] [%s]', servicio, funcion, mensaje)
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################
@app.route(modulo + programa + '/PedirProyecto', methods=["GET"])
@auth_decorator()
def f6100_pedir_proyecto_ts302():
    #Trae todos los campos de la tabla Gbrne Contabilidad p/financiadores (S/N)
    g_mcfi = None
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f6100_pedir_proyecto_ts302'

    try:
        #gbrne Reglas de negocio
        #gbrnemcfi Contabilidad p/financiadores (S/N)
        sql_gbrne = "select gbrnemcfi as g_mcfi FROM gbrne"
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_gbrne)
        db.conectar()
        rsp_gbrne = db.query(sql_gbrne)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_gbrne)
        array = []
        i = 0
        print(rsp_gbrne)

        if rsp_gbrne is None:
            result['mensaje'] = 'No se encuentran registros'
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_gbrne:
                i_gbrne = collections.OrderedDict()
                array.append({
                    'contabilidadFinanciadores' : item['g_mcfi']
                })
            result['mensaje'] = "Cargado Correctamente"
        result['respuestaGbrne'] = array
        result['total'] = len(array)
      
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        logging.info('ERROR : [%s] [%s] [%s]', servicio, funcion, mensaje)
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']
    
#############################################################
@app.route(modulo + programa + '/DatosImpresionCheque', methods=["GET"])
@auth_decorator()
def f6310_display_datos_ts302():
    #Trae todos los campos de la tabla Tsich Datos para impresion de cheque      
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f6310_display_datos_ts302'

    try:
        sql_tsich = "select *, tsichplza as g_plza, tsichfmto as g_fmto from tsich" #WHERE tsichcbco = t1.tsccbcbco AND tsichncta = t1.tsccbncta
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_tsich)
        db.conectar()
        rsp_tsich = db.query(sql_tsich)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_tsich)
        array = []
        i = 0
        print(rsp_tsich)

        if rsp_tsich is None:
            result['mensaje'] = 'No se encuentran registros'
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_tsich:
                i_tsich = collections.OrderedDict()
                array.append({
                        'numeroBanco' : str(item['tsichcbco']).strip(),
                        'numeroCuenta' : str(item['tsichncta']).strip(),
                        'codigoLogoBanco' : str(item['tsichlbco']).strip(),
                        'datosLineMic' : str(item['tsichlmic']).strip(),
                        'codigoPlaza' : str(item['g_plza']).strip(),
                        'formatoImpresionPorCuenta' : str(item['tsichfmto']).strip()
                    })
            result['mensaje'] = "Cargado Correctamente"

        result['respuestaTsich'] = array
        result['total'] = len(array)
    

        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        logging.info('ERROR : [%s] [%s] [%s]', servicio, funcion, mensaje)
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']