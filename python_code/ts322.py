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
programa = "/DepositoChequesMismoBanco"
servicio = 'ts322'
funcion = 'main'
#############################################################


class RegistrarDepositoChequesMismoBanco(BaseSchema):
    unidadNegocio = fields.Integer(required=True)
    codigoBanco = fields.Integer(required=True)
    numeroCuenta = fields.String(required=True)
    codigoCliente = fields.String(required=True)

############################################
# ALTA DE REGISTROS
# REGISTRA DEPOSITO CHEQUES MISMO BANCO
############################################
@app.route(modulo + programa + '/Registrar', methods=["POST"])
@auth_decorator()
@required_params(RegistrarDepositoChequesMismoBanco())
def f1000_altas_ts322():
    resultado = {
        'mensaje': 'Guardado correctamente',
        'status': 200
    }
    

    funcion = 'f1000_altas_ts322'
    parametros = []
   

    try:
        datos = request.json
        item = 1

        sql_delete = "delete tsdep where tsdepuneg = " + str(datos['unidadNegocio']) + " and tsdepcbco = " + str(datos['codigoBanco'])  +  " and tsdepncta = '" + str(datos['numeroCuenta']) + "'"
        sql_insert = "insert into tsdep (tsdepuneg, tsdepcbco, tsdepncta, tsdepcage) values(" + str(datos['unidadNegocio']) + ", " + str(datos['codigoBanco']) +  ", '" + str(datos['numeroCuenta']) + "', '" +  str(datos['codigoCliente']) +  "')"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_insert)
        
        db.conectar()
        db.BEGIN_WORK()
        
        rsp_delete = db.eliminar(sql_delete)

        rsp_insert = db.insertar(sql_insert)

        if rsp_insert == 0:
            mensaje = "No se pudo insertar el registro"
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
            
            resultado['status'] = 500
            resultado['mensaje'] = mensaje
        else:
            mensaje = "El registro se inserto correctamente"
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
            resultado['mensaje'] = mensaje
        
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_insert)


        db.COMMIT_WORK()

    except Exception as ex:
        db.ROLLBACK_WORK()
        resultado['status'] = 500
        resultado['mensaje'] = str(ex)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, str(ex))
    finally:
        db.desconectar()

    return json.dumps(resultado, cls=CustomJSONEncoder), resultado['status']



#########################################
# MODIFICACION DEPOSITO CHEQUES MISMO BANCO
#########################################
class ModificarDepositoChequesMismoBanco(BaseSchema):
    unidadNegocio = fields.Integer(required=True)
    codigoBanco = fields.Integer(required=True)
    numeroCuenta = fields.String(required=True)
    codigoClienteAntiguo = fields.Integer(required=True)
    codigoClienteNuevo = fields.Integer(required=True)


@app.route(modulo + programa + '/Modificar', methods=["PUT"])
@auth_decorator()
@required_params(ModificarDepositoChequesMismoBanco())
def f2000_modificar_ts322():
    resultado = {
        'mensaje': 'Actualizado correctamente',
        'status': 200
    }
    
    #db = Database()
    funcion = 'f2000_modificar_ts322'
    parametros = []
   

    try:
        datos = request.json
        item = 1

        sql_update = "update tsdep set tsdepuneg = " + str(datos['unidadNegocio']) + ", tsdepcbco = " + str(datos['codigoBanco']) + ", tsdepncta = '" + str(datos['numeroCuenta']) +  "', tsdepcage = " + str(datos['codigoClienteNuevo']) +  "  where tsdepcage = " + str(datos['codigoClienteAntiguo'])  + ""
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_update)

        db.conectar()
        db.BEGIN_WORK()
        rsp_update = db.actualizar(sql_update)
        
        if rsp_update == 0:
            mensaje = "No se encontro el registro solicitado, unidadNegocio: " + str(datos['unidadNegocio']) + " codigoBanco: " + str(datos['codigoBanco']) + " numeroCuenta: " + str(datos['numeroCuenta']) + " codigoAgendaAntiguo: " + str(datos['codigoClienteAntiguo'])
            
            resultado['status'] = 500
            resultado['mensaje'] = mensaje
        else:
            mensaje = "El registro  unidadNegocio: " + str(datos['unidadNegocio']) + " codigoBanco: " + str(datos['codigoBanco']) + " numeroCuenta: " + str(datos['numeroCuenta']) + " codigoAgendaAntiguo: " + str(datos['codigoClienteAntiguo']) + " se actualizo correctamente con codigoAgendaNuevo: " + str(datos['codigoClienteNuevo'])
            resultado['mensaje'] = mensaje
        
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_update)

        
        db.COMMIT_WORK()

        
    except Exception as ex:
        db.ROLLBACK_WORK()
        resultado['status'] = 500
        resultado['mensaje'] = str(ex)
    finally:
        db.desconectar()

    return json.dumps(resultado, cls=CustomJSONEncoder), resultado['status']

class EliminarDepositoChequesMismoBanco(BaseSchema):
    unidadNegocio= fields.Integer(required=True)
    codigoBanco = fields.Integer(required=True)
    numeroCuenta = fields.String(required=True)

####################################################
# BORRAR REGISTROS DEPOSITO CHEQUES MISMO BANCO
####################################################
@app.route(modulo + programa + '/Eliminar', methods=["DELETE"])
@auth_decorator()
@required_params(EliminarDepositoChequesMismoBanco())
def f3000_borrar_ts322():
    
    resultado = {
        'mensaje': 'Eliminado correctamente',
        'status': 200
    }
    
    #db = Database()
    funcion = 'f3000_borrar_ts322'
    parametros = []


    try:
        datos = request.json
        item = 1
        

        if datos['codigoAgenda'] is not None:
            for item in datos['codigoAgenda']:
                logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, item)
                sql_delete = "delete tsdep where tsdepuneg = " + str(datos['unidadNegocio']) + " and tsdepcbco = " + str(datos['codigoBanco']) + " and tsdepncta = '" + str(datos['numeroCuenta']) + "' and tsdepcage = " + item + ""
        else:
            sql_delete = "delete tsdep where tsdepuneg = " + str(datos['unidadNegocio']) + " and tsdepcbco = " + str(datos['codigoBanco']) + " and tsdepncta = '" + str(datos['numeroCuenta']) + "'"
        

        db.conectar()
        db.BEGIN_WORK()
        rsp_delete = db.eliminar(sql_delete)
        print(rsp_delete)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_delete)


        if rsp_delete == 0:
            mensaje = "No se encontro el registro solicitado, unidadNegocio: " + str(datos['unidadNegocio']) + " codigoBanco: " + str(datos['codigoBanco']) + " numeroCuenta: " + str(datos['numeroCuenta'])
            print('f3000_borrar_ts322 mensaje: ', mensaje)
            resultado['status'] = 200
            resultado['mensaje'] = mensaje
        else:
            if datos['codigoAgenda'] is not None:
                for item in datos['codigoAgenda']:
                    mensaje = "El registro unidadNegocio: " + str(datos['unidadNegocio']) + " codigoBanco: " + str(datos['codigoBanco']) + " numeroCuenta: " + str(datos['numeroCuenta']) + " codigoAgenda: " + item + " se elimino correctamente"
                    resultado['mensaje'] = mensaje
            else:
                mensaje = "El registro unidadNegocio: " + str(datos['unidadNegocio']) + " codigoBanco: " + str(datos['codigoBanco']) + " numeroCuenta: " + str(datos['numeroCuenta']) + " se elimino correctamente"
                resultado['mensaje'] = mensaje
        
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_delete)

        db.COMMIT_WORK()

        
    except Exception as ex:
        db.ROLLBACK_WORK()
        resultado['status'] = 500
        resultado['mensaje'] = str(ex)
    finally:
        db.desconectar()

    return json.dumps(resultado, cls=CustomJSONEncoder), resultado['status']
    
###################
# BUSQUEDA DE DATOS
###################

@app.route(modulo + programa + '/BuscarDepositos', methods=["GET"])
@auth_decorator()
def f5000_buscar_registro_ts322():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5000_buscar_registro_ts322'

    try:

        numeroDeposito = None

        if 'numeroDeposito' in  request.args: 
            numeroDeposito =  request.args.get('numeroDeposito')
            sql_tsdep = "SELECT * FROM tsdep where tsdepntra = " + numeroDeposito + " AND tsdeptdep = 1 AND tsdepmrcb = 0"
        else:
            sql_tsdep = "SELECT * FROM tsdep WHERE tsdeptdep = 1 AND tsdepmrcb = 0 ORDER BY tsdepntra"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_tsdep)

        db.conectar()
        rsp_tsdep = db.query(sql_tsdep)
        array = []
        i = 0

        if rsp_tsdep is None:
            mensaje = 'No se encuentran registros para la transaccion ' + str(numeroDeposito)
            result['mensaje'] = mensaje
            result['total'] = 0
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
        else:
            for item in rsp_tsdep:
                i_tsdep = collections.OrderedDict()
               
                array.append({
                    'numeroDeposito' : str(item['tsdepntra']).strip(),
                    'tipoDeposito' : str(item['tsdeptdep']).strip(),
                    'fechaTransaccion' : str(item['tsdepftra']).strip(),
                    'numeroDocumento' : str(item['tsdepndoc']).strip(),
                    'fechaDocumento' : str(item['tsdepfdoc']).strip(),
                    'unidadNegocio' : str(item['tsdepuneg']).strip(),
                    'codigoBanco' : str(item['tsdepcbco']).strip(),
                    'numeroCuenta' : str(item['tsdepncta']).strip(),
                    'monedaDeposito' : str(item['tsdepcmon']).strip(),
                    'tipoCambio' : str(item['tsdeptcam']).strip(),
                    'importeEfectivo' : str(item['tsdepiefe']).strip(),
                    'importeCheques' : str(item['tsdepichq']).strip(),
                    'importeTotalDepositadoMonDep' : str(item['tsdepimpt']).strip(),
                    'importeTotalDepositadoMonCta' : str(item['tsdepimpo']).strip(),
                    'monedaCuenta' : str(item['tsdepmcta']).strip(),
                    'glosa1' : str(item['tsdepgls1']).strip(),
                    'glosa2' : str(item['tsdepgls2']).strip(),
                    'glosa3' : str(item['tsdepgls3']).strip(),
                    'marcaBaja' : str(item['tsdepmrcb']).strip(),
                    'usuario' : str(item['tsdepuser']).strip(),
                    'hora' : str(item['tsdephora']).strip(),
                    'fechaProceso' : str(item['tsdepfpro']).strip()
                })

                result['depositos'] = array
                result['total'] = len(array)
                result['mensaje'] = "Cargado Correctamente"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_tsdep)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

@app.route(modulo + programa + '/BuscarConceptosGlobales', methods=["GET"])
@auth_decorator()
def f5010_buscar_gbcon_ts322():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5010_buscar_gbcon_ts322'

    try:
        prefijoConcepto = None
        correlativoConcepto = None
        
        if 'prefijoConcepto' in  request.args and 'correlativoConcepto' in  request.args: 
            prefijoConcepto =  request.args.get('prefijoConcepto')
            correlativoConcepto =  request.args.get('correlativoConcepto')
            sql_gbcon = "SELECT gbconpfij, gbconcorr, gbcondesc AS l_desc, gbconabre AS l_abre FROM gbcon WHERE gbconpfij = " + str(prefijoConcepto) + " AND gbconcorr = " + str(correlativoConcepto) + " AND gbconcorr > 0"
        elif 'prefijoConcepto' in  request.args:
            prefijoConcepto =  request.args.get('prefijoConcepto')
            sql_gbcon = "SELECT gbconpfij, gbconcorr, gbcondesc AS l_desc, gbconabre AS l_abre FROM gbcon WHERE gbconpfij = " + str(prefijoConcepto) + " AND gbconcorr > 0"
        elif 'correlativoConcepto' in  request.args:
            correlativoConcepto =  request.args.get('correlativoConcepto')
            sql_gbcon = "SELECT gbconpfij, gbconcorr, gbcondesc AS l_desc, gbconabre AS l_abre FROM gbcon WHERE gbconcorr = " + str(correlativoConcepto) + " AND gbconcorr > 0"
        else:
            sql_gbcon = "SELECT gbconpfij, gbconcorr, gbcondesc AS l_desc, gbconabre AS l_abre FROM gbcon WHERE gbconcorr > 0"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_gbcon)

        db.conectar()
        rsp_gbcon = db.query(sql_gbcon)
        array = []
        i = 0

        if rsp_gbcon is None:
            mensaje = 'No se encuentran registros'
            result['total'] = 0
            result['mensaje'] = mensaje
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_gbcon:
                i_gbcon = collections.OrderedDict()

                array.append({
                    'prefijoConcepto' : str(item['gbconpfij']).strip(),
                    'correlativoConcepto' : str(item['gbconcorr']).strip(),
                    'descripcion' : str(item['l_desc']).strip(),
                    'abreviacion' : str(item['l_abre']).strip()
                })

            result['depositoChequesMismoBancoGbcon'] = array
            result['total'] = len(array)
            result['mensaje'] = "Cargado Correctamente"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_gbcon)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

@app.route(modulo + programa + '/BuscarHistoricoTipoCambio', methods=["GET"])
@auth_decorator()
def f5010_buscar_gbhtc_ts322():

    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5010_buscar_gbhtc_ts322'

    try:
        fechaTipoCambio = None
        
        if 'fechaTipoCambio' in  request.args : 
            fechaTipoCambio =  request.args.get('fechaTipoCambio')
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, fechaTipoCambio)
            print(fechaTipoCambio)
            sql_gbhtc = "SELECT gbhtcfech, gbhtctcof, gbhtctcco, gbhtctcve FROM gbhtc WHERE gbhtcfech <= '" + str(fechaTipoCambio) + "' ORDER BY gbhtcfech"
        else:
            sql_gbhtc = "SELECT gbhtcfech, gbhtctcof, gbhtctcco, gbhtctcve FROM gbhtc ORDER BY gbhtcfech"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_gbhtc)

        db.conectar()
        rsp_gbhtc = db.query(sql_gbhtc)
        array = []
        i = 0

        if rsp_gbhtc is None:
            mensaje = 'No puede recuperar los Tipos de Cambio para la fecha: ' + fechaTipoCambio 
            result['total'] = 0
            result['mensaje'] = mensaje
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_gbhtc:
                i_gbhtc = collections.OrderedDict()
               
                array.append({
                    'fecha' : str(item['gbhtcfech']).strip(),
                    'tipoCambioOficial' : str(item['gbhtctcof']).strip(),
                    'tipoCambioCompra' : str(item['gbhtctcco']).strip(),
                    'tipoCambioVenta' : str(item['gbhtctcve']).strip()
                })

                result['tipoCambio'] = array
                result['total'] = len(array)
                result['mensaje'] = "Cargado Correctamente"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_gbhtc)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

@app.route(modulo + programa + '/BuscarCuentasBancos', methods=["GET"])
@auth_decorator()
def f5020_buscar_tsccb_ts322():
    #Trae todos los campos de la tabla Tsccb Cuentas en Bancos, puedes filtrar por numeroBanco y numeroCuenta
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5020_buscar_tsccb_ts322'
    try:
        numeroBanco = None
        numeroCuenta = None

        if 'numeroBanco' in  request.args and 'numeroCuenta' in  request.args:
            numeroBanco =  request.args.get('numeroBanco')
            numeroCuenta =  request.args.get('numeroCuenta')
            sql_tsccb = "SELECT * FROM tsccb WHERE tsccbcbco = " + str(numeroBanco) + " AND tsccbncta = '" + str(numeroCuenta) + "' ORDER BY tsccbcbco, tsccbncta"
        elif 'numeroBanco' in  request.args:
            numeroBanco =  request.args.get('numeroBanco')
            sql_tsccb = "SELECT * FROM tsccb WHERE tsccbcbco = " + str(numeroBanco) + " ORDER BY tsccbcbco, tsccbncta"
        elif 'numeroCuenta' in  request.args:
            numeroCuenta =  request.args.get('numeroCuenta')
            sql_tsccb = "SELECT * FROM tsccb WHERE tsccbncta = '" + str(numeroCuenta) + "' ORDER BY tsccbcbco, tsccbncta"
        else:
            sql_tsccb = "SELECT * FROM tsccb ORDER BY tsccbcbco, tsccbncta"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_tsccb)

        db.conectar()
        rsp_tsccb = db.query(sql_tsccb)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_tsccb)
        array = []
        i = 0
        print(rsp_tsccb)

        if rsp_tsccb is None:
            result['mensaje'] = 'No se encuentran registros'
            result['total'] = 0
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_tsccb:
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
                  
                    'habilitada' : str(item['tsccbstat']).strip()
                })
            result['mensaje'] = "Cargado Correctamente"

        result['cuentasBancosTsccb'] = array
        result['total'] = len(array)
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        logging.info('ERROR : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

@app.route(modulo + programa + '/BuscarCheques', methods=["GET"])
@auth_decorator()
def f5030_buscar_tscha_ts322():
    #Trae todos los campos de la tabla Tsccb Cuentas en Bancos, puedes filtrar por numeroBanco y numeroCuenta
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5030_buscar_tscha_ts322'
    try:
        numeroBanco = None
        numeroCuenta = None
        numeroCheque = None

        # Cheques Emitidos, parametro 1 : Prefijo Numero de Banco, parametro 2 : Prefijo Numero de Cuenta, parametro 3 : Prefijo Numero de Cheque
        numeroBanco =  request.args.get('numeroBanco')
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, numeroBanco)
        numeroCuenta =  request.args.get('numeroCuenta')
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, numeroCuenta)
        numeroCheque =  request.args.get('numeroCheque')
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, numeroCheque)
        
        if 'numeroBanco' in  request.args and 'numeroCuenta' in  request.args and 'numeroCheque' in  request.args:
            numeroBanco =  request.args.get('numeroBanco')
            numeroCuenta =  request.args.get('numeroCuenta')
            numeroCheque =  request.args.get('numeroCheque')
            sql_select = "SELECT tschacbco, tschancta, tschanchq, tschatchq, tschaimpo, tschacmon, tschauneg, tschastat, tschamorg FROM tscha WHERE tschatchq = 2 AND tschacbco = " + str(numeroBanco) + " AND tschancta = '" + str(numeroCuenta) + "' AND tschanchq = '" + str(numeroCheque) + "' AND tschatchq = 2 ORDER BY tschanchq"
        elif 'numeroBanco' in  request.args and 'numeroCuenta' in  request.args:
            numeroBanco =  request.args.get('numeroBanco')
            numeroCuenta =  request.args.get('numeroCuenta')
            sql_select = "SELECT tschacbco, tschancta, tschanchq, tschatchq, tschaimpo, tschacmon, tschauneg, tschastat, tschamorg FROM tscha WHERE tschatchq = 2 AND tschacbco = " + str(numeroBanco) + " AND tschancta = '" + str(numeroCuenta) + "' ORDER BY tschanchq"
        elif 'numeroBanco' in  request.args:
            numeroBanco =  request.args.get('numeroBanco')
            sql_select = "SELECT tschacbco, tschancta, tschanchq, tschatchq, tschaimpo, tschacmon, tschauneg, tschastat, tschamorg FROM tscha WHERE tschatchq = 2 AND tschacbco = " + str(numeroBanco) + " ORDER BY tschanchq"   
        elif 'numeroCuenta' in  request.args:
            numeroCuenta =  request.args.get('numeroCuenta')
            sql_select = "SELECT tschacbco, tschancta, tschanchq, tschatchq, tschaimpo, tschacmon, tschauneg, tschastat, tschamorg FROM tscha WHERE tschatchq = 2 AND tschancta = '" + str(numeroCuenta) + "' ORDER BY tschanchq"   
        elif 'numeroCheque' in  request.args:
            numeroCheque =  request.args.get('numeroCheque')
            sql_select = "SELECT tschacbco, tschancta, tschanchq, tschatchq, tschaimpo, tschacmon, tschauneg, tschastat, tschamorg FROM tscha WHERE tschatchq = 2 AND tschanchq = '" + str(numeroCheque) + "' ORDER BY tschanchq"
        else:
            sql_select = "SELECT tschacbco, tschancta, tschanchq, tschatchq, tschaimpo, tschacmon, tschauneg, tschastat, tschamorg FROM tscha WHERE tschatchq = 2 ORDER BY tschanchq"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_select)
        print(sql_select)
        db.conectar()
        rsp_tscha = db.query(sql_select)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_tscha)
        array = []
        i = 0
        print(rsp_tscha)

        if rsp_tscha is None:
            result['mensaje'] = 'No se encuentran registros'
            result['total'] = 0
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_tscha:
                i_tscha = collections.OrderedDict()

                if str(item['tschastat']).strip() == '3':
                    estiloCheque = "Cheque Depositado"
                elif str(item['tschastat']).strip() == '4':
                    estiloCheque = "Cheque dado de Baja"
                elif str(item['tschastat']).strip() == '5':
                    estiloCheque = "Cheque Anulado"
                elif str(item['tschastat']).strip() == '6':
                    estiloCheque = "Cheque Cambiado"
                else:
                    estiloCheque = ""

                array.append({
                        'numeroBanco' : str(item['tschacbco']).strip(),
                        'numeroCuenta' : str(item['tschancta']).strip(),
                        'numeroCheque' : str(item['tschanchq']).strip(),
                        'tipoCheque' : str(item['tschatchq']).strip(),
                        'importe' : str(item['tschaimpo']).strip(),
                        'moneda' : str(item['tschacmon']).strip(),
                        'unidadNegocio' : str(item['tschauneg']).strip(),
                        'estiloCheque' : estiloCheque,
                        'moduloOrigen' : str(item['tschamorg']).strip()
                })
            result['mensaje'] = "Cargado Correctamente"
            result['cuentasBancosTscha'] = array
            result['total'] = len(array)
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        logging.info('ERROR : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

@app.route(modulo + programa + '/BuscarUsuariosHabilitadosUnidadNegocio', methods=["GET"])
@auth_decorator()
def f5040_buscar_adhuu_ts322():
    #Trae todos los campos de la tabla Adhuu Cuentas en Bancos, puedes filtrar por numeroBanco y numeroCuenta
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5040_buscar_adhuu_ts322'
    try:
        usuario = None
        unidadNegocio = None

        if 'usuario' in  request.args and 'unidadNegocio' in  request.args:
            usuario =  request.args.get('usuario')
            unidadNegocio =  request.args.get('unidadNegocio')
            sql_adhuu = "SELECT * FROM adhuu WHERE adhuuusrn = '" + str(usuario) + "' AND adhuuuneg = " + str(unidadNegocio) + " ORDER BY adhuuusrn"
        elif 'usuario' in  request.args:
            usuario =  request.args.get('usuario')
            sql_adhuu = "SELECT * FROM adhuu WHERE adhuuusrn = '" + str(usuario) + "' ORDER BY adhuuusrn"
        elif 'unidadNegocio' in  request.args:
            unidadNegocio =  request.args.get('unidadNegocio')
            sql_adhuu = "SELECT * FROM adhuu WHERE adhuuuneg = " + str(unidadNegocio) + " ORDER BY adhuuusrn"
        else:
            sql_adhuu = "SELECT * FROM adhuu ORDER BY adhuuusrn"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_adhuu)

        db.conectar()
        rsp_adhuu = db.query(sql_adhuu)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_adhuu)
        array = []
        i = 0
        print(rsp_adhuu)

        if rsp_adhuu is None:
            result['mensaje'] = 'No se encuentran registros'
            result['total'] = 0
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_adhuu:
                i_adhuu = collections.OrderedDict()
                array.append({
                    'codigoUsuario' : str(item['adhuuusrn']).strip(),
                    'unidadNegocio' : str(item['adhuuuneg']).strip(),
                    'usuario' : str(item['adhuuuser']).strip(),
                    'hora' : str(item['adhuuhora']).strip(),
                    'fechaProceso' : str(item['adhuufpro']).strip()
                })
            result['mensaje'] = "Cargado Correctamente"

        result['usuariosHabilitadorsAdhuu'] = array
        result['total'] = len(array)
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        logging.info('ERROR : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']


#############################################################

@app.route(modulo + programa + '/BuscarUnidadNegocio', methods=["GET"])
@auth_decorator()
def f5050_buscar_cnune_ts322():
    #Trae todos los campos de la tabla Adhuu Cuentas en Bancos, puedes filtrar por numeroBanco y numeroCuenta
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5050_buscar_cnune_ts322'
    try:
        unidadNegocio = None
        descripcion = None

        unidadNegocio =  request.args.get('unidadNegocio')
        descripcion =  request.args.get('descripcion')
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, unidadNegocio)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, descripcion)

        if unidadNegocio is not None:
            sql_select = "SELECT cnuneuneg, cnunedesc, cnunecreg FROM cnune WHERE cnuneuneg = " + str(unidadNegocio) + " ORDER BY cnuneuneg"
        elif descripcion is not None:
            sql_select = "SELECT cnuneuneg, cnunedesc, cnunecreg FROM cnune WHERE cnunedesc LIKE '%" + str(descripcion) + "%' ORDER BY cnuneuneg"
        else:
            sql_select = "SELECT cnuneuneg, cnunedesc, cnunecreg FROM cnune ORDER BY cnuneuneg"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_select)

        db.conectar()
        rsp_cnune = db.query(sql_select)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_cnune)
        array = []
        i = 0
        print(rsp_cnune)

        if rsp_cnune is None:
            result['mensaje'] = 'No se encuentran registros'
            result['total'] = 0
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_cnune:
                i_cnune = collections.OrderedDict()
                array.append({
                    'unidadNegocio' : str(item['cnuneuneg']).strip(),
                    'descripcion' : str(item['cnunedesc']).strip(),
                    'codigoRegional' : str(item['cnunecreg']).strip()
                })
            result['mensaje'] = "Cargado Correctamente"
            result['usuariosCnune'] = array
            result['total'] = len(array)
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        logging.info('ERROR : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

@app.route(modulo + programa + '/BuscarDetalleDepositos', methods=["GET"])
@auth_decorator()
def f5100_buscar_detalle_ts322():

    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5100_buscar_detalle_ts322'

    try:
        numeroDeposito = None
        
        if 'numeroDeposito' in  request.args : 
            numeroDeposito =  request.args.get('numeroDeposito')
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, numeroDeposito)
            print(numeroDeposito)
            sql_tsdch = "SELECT * FROM tsdch WHERE tsdchntra = " + str(numeroDeposito) + " ORDER BY tsdchntra"
        else:
            sql_tsdch = "SELECT * FROM tsdch ORDER BY tsdchntra"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_tsdch)

        db.conectar()
        rsp_tsdch = db.query(sql_tsdch)
        array = []
        i = 0

        if rsp_tsdch is None:
            mensaje = 'No puede recuperar el detalle para el numero de deposito: ' + numeroDeposito 
            result['total'] = 0
            result['mensaje'] = mensaje
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_tsdch:
                i_tsdch = collections.OrderedDict()
               
                array.append({
                    'numeroDeposito' : str(item['tsdchntra']).strip(),
                    'fechaDocumento' : str(item['tsdchfdoc']).strip(),
                    'numeroBanco' : str(item['tsdchcbco']).strip(),
                    'numeroCuenta' : str(item['tsdchncta']).strip(),
                    'numeroCheque' : str(item['tsdchnchq']).strip(),
                    'importe' : str(item['tsdchimpt']).strip(),
                    'monedaCheque' : str(item['tsdchcmon']).strip()
                })

                result['depositosTsdhc'] = array
                result['total'] = len(array)
                result['mensaje'] = "Cargado Correctamente"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_tsdch)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

@app.route(modulo + programa + '/BuscarCajas', methods=["GET"])
@auth_decorator()
def f5400_buscar_caja_ts322():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5400_buscar_caja_ts322'

    try:
        numeroCaja = None
        usuarioResponsable = None
        
        if 'numeroCaja' in  request.args and 'usuarioResponsable' in  request.args: 
            numeroCaja =  request.args.get('numeroCaja')
            usuarioResponsable =  request.args.get('usuarioResponsable')
            sql_cjmcj = "SELECT cjmcjncja, cjmcjresp, cjmcjuneg FROM cjmcj WHERE cjmcjncja = " + str(numeroCaja) + " AND cjmcjresp = '" + str(usuarioResponsable) + "'"
        elif 'numeroCaja' in  request.args:
            numeroCaja =  request.args.get('numeroCaja')
            sql_cjmcj = "SELECT cjmcjncja, cjmcjresp, cjmcjuneg FROM cjmcj WHERE cjmcjncja = " + str(numeroCaja)
        elif 'usuarioResponsable' in  request.args:
            usuarioResponsable =  request.args.get('usuarioResponsable')
            sql_cjmcj = "SELECT cjmcjncja, cjmcjresp, cjmcjuneg FROM cjmcj WHERE cjmcjresp = '" + str(usuarioResponsable) + "'"
        else:
            sql_cjmcj = "SELECT cjmcjncja, cjmcjresp, cjmcjuneg FROM cjmcj"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_cjmcj)

        db.conectar()
        rsp_cjmcj = db.query(sql_cjmcj)
        array = []
        i = 0

        if rsp_cjmcj is None:
            mensaje = 'No se encuentran registros'
            result['total'] = 0
            result['mensaje'] = mensaje
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_cjmcj:
                i_cjmcj = collections.OrderedDict()

                array.append({
                    'numeroCaja' : str(item['cjmcjncja']).strip(),
                    'usuarioResponsable' : str(item['cjmcjresp']).strip(),
                    'unidadNegocio' : str(item['cjmcjuneg']).strip()
                })

            result['cajasCjmcj'] = array
            result['total'] = len(array)
            result['mensaje'] = "Cargado Correctamente"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_cjmcj)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

@app.route(modulo + programa + '/BuscarParametrosIniciales', methods=["GET"])
@auth_decorator()
def f6050_parametros_iniciales_ts322():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f6050_parametros_iniciales_ts322'

    try:
        sql_gbpmt = "SELECT * FROM gbpmt"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_gbpmt)

        db.conectar()
        rsp_gbpmt = db.query(sql_gbpmt)
        array = []
        i = 0
        print(rsp_gbpmt)
        if rsp_gbpmt is None:
            mensaje = 'No se encuentran registros'
            result['total'] = 0
            result['mensaje'] = mensaje
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_gbpmt:
                i_gbpmt = collections.OrderedDict()

                array.append({
                    'fechaDia' : str(item['gbpmtfdia']).strip(),
                    'tipoCambioOficial' : str(item['gbpmttcof']).strip(),
                    'tipoCambioCompra' : str(item['gbpmttcco']).strip(),
                    'tipoCambioVentaa' : str(item['gbpmttcve']).strip(),
                    'fechaInicioGestion' : str(item['gbpmtfini']).strip(),
                    'fechaFinGestion' : str(item['gbpmtffin']).strip(),
                    'anioCurso' : str(item['gbpmtgest']).strip(),
                    'ultimoMesActivo' : str(item['gbpmtumes']).strip(),
                    'tasaIVA' : str(item['gbpmtiiva']).strip(),
                    'impuestoTransacciones' : str(item['gbpmtitra']).strip(),
                    'monedaImputacion' : str(item['gbpmtmimp']).strip(),
                    'monedaConversion' : str(item['gbpmtmcon']).strip(),
                    'direccion1' : str(item['gbpmtdir1']).strip(),
                    'direccion2' : str(item['gbpmtdir2']).strip()
                    #'sensibilidadCambiaria' : str(item['gbpmtscam']).strip(),
                    #'nombreEmpresa' : str(item['gbpmtnemp']).strip(),
                    #'codigoBanco' : str(item['gbpmtcbco']).strip(),
                    #'clave' : str(item['gbpmtclav']).strip(),
                    #'rucEmpresa' : str(item['gbpmtcruc']).strip(),
                    #'plaza' : str(item['gbpmtplaz']).strip(),
                    #'tipoEntidad' : str(item['gbpmttent']).strip(),
                    #'montoGarantiaFavor' : str(item['gbpmtmfin']).strip(),
                    #'tipoCambioUFV' : str(item['gbpmttufv']).strip()
                })

            result['parametrosInicialesGbpmt'] = array
            result['total'] = len(array)
            result['mensaje'] = "Cargado Correctamente"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_gbpmt)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

@app.route(modulo + programa + '/BuscarReglasNegocio', methods=["GET"])
@auth_decorator()
def f6050_reglas_negocio_ts322():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f6050_parametros_iniciales_ts322'

    try:
        sql_gbrne = "SELECT * FROM gbrne"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_gbrne)

        db.conectar()
        rsp_gbrne = db.query(sql_gbrne)
        array = []
        i = 0
        print(rsp_gbrne)
        if rsp_gbrne is None:
            mensaje = 'No se encuentran registros'
            result['total'] = 0
            result['mensaje'] = mensaje
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

            result['reglasNegocioGbrne'] = array
            result['total'] = len(array)
            result['mensaje'] = "Cargado Correctamente"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_gbrne)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

@app.route(modulo + programa + '/BuscarParametrosFlujoCaja', methods=["GET"])
@auth_decorator()
def f6050_flujo_caja_ts322():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f6050_flujo_caja_ts322'

    try:
        sql_cnpmf = "SELECT * FROM cnpmf"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_cnpmf)

        db.conectar()
        rsp_cnpmf = db.query(sql_cnpmf)
        array = []
        i = 0
        print(rsp_cnpmf)
        if rsp_cnpmf is None:
            mensaje = 'No se encuentran registros'
            result['total'] = 0
            result['mensaje'] = mensaje
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_cnpmf:
                i_cnpmf = collections.OrderedDict()

                array.append({
                    'trabajaConFlujo' : str(item['cnpmfmtfc']).strip(),
                    'cuentaVentaProductos' : str(item['cnpmfcfvp']).strip(),
                    'cuentaVentaServicios' : str(item['cnpmfcfvs']).strip(),
                    'cuentaPorAnticipoVentas' : str(item['cnpmfcfav']).strip(),
                    'cuentaCobroVentasCreditoProductos' : str(item['cnpmfcfcp']).strip(),
                    'cuentaCobroVentasCreditoServicios' : str(item['cnpmfcfcs']).strip(),
                    'cuentaDevolucionProductosEnPos' : str(item['cnpmfcdvp']).strip()
                })

            result['parametrosCnpmf'] = array
            result['total'] = len(array)
            result['mensaje'] = "Cargado Correctamente"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_cnpmf)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

@app.route(modulo + programa + '/BuscarParametrosControl', methods=["GET"])
@auth_decorator()
def f6050_parametros_control_ts322():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f6050_parametros_control_ts322'

    try:
        sql_tsctl = "SELECT * FROM tsctl"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_tsctl)

        db.conectar()
        rsp_tsctl = db.query(sql_tsctl)
        array = []
        i = 0
        print(rsp_tsctl)
        if rsp_tsctl is None:
            mensaje = 'No se encuentran registros'
            result['total'] = 0
            result['mensaje'] = mensaje
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_tsctl:
                i_tsctl = collections.OrderedDict()

                if item['tsctlflim'] == None:
                    fechaLimpieza = ''
                else:
                    fechaLimpieza = str(item['tsctlflim'])

                array.append({
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

            result['parametrosControlTsctl'] = array
            result['total'] = len(array)
            result['mensaje'] = "Cargado Correctamente"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_tsctl)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

@app.route(modulo + programa + '/BuscarParametrosContabilidad', methods=["GET"])
@auth_decorator()
def f6050_parametros_contabilidad_ts322():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f6050_parametros_control_ts322'

    try:
        sql_cnprm = "SELECT * FROM cnprm"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_cnprm)

        db.conectar()
        rsp_cnprm = db.query(sql_cnprm)
        array = []
        i = 0
        print(rsp_cnprm)
        if rsp_cnprm is None:
            mensaje = 'No se encuentran registros'
            result['total'] = 0
            result['mensaje'] = mensaje
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_cnprm:
                i_cnprm = collections.OrderedDict()

                if item['cnprmfdes'] == None:
                    fechaDesactivado = ''
                else:
                    fechaDesactivado = str(item['cnprmfdes'])

                array.append({
                    'naturalezaCuentaCapitulo1' : str(item['cnprmncp1']).strip(), #      A = activo P = pasivo I = ingreso E = egreso O = orden
                    'naturalezaCuentaCapitulo2' : str(item['cnprmncp2']).strip(),
                    'naturalezaCuentaCapitulo3' : str(item['cnprmncp3']).strip(),
                    'naturalezaCuentaCapitulo4' : str(item['cnprmncp4']).strip(),
                    'naturalezaCuentaCapitulo5' : str(item['cnprmncp5']).strip(),
                    'naturalezaCuentaCapitulo6' : str(item['cnprmncp6']).strip(),
                    'naturalezaCuentaCapitulo7' : str(item['cnprmncp7']).strip(),
                    'naturalezaCuentaCapitulo8' : str(item['cnprmncp8']).strip(),
                    'naturalezaCuentaCapitulo9' : str(item['cnprmncp9']).strip(),
                    'cuentaResultadoGestion' : str(item['cnprmcres']).strip(),
                    'cuentaResultadoAcumulado' : str(item['cnprmcrea']).strip(),
                    'cuentaAjusteGlobalPatrimonio' : str(item['cnprmcaju']).strip(),
                    'centroCostoAjusteGlobalPatrimonio' : str(item['cnprmccos']).strip(),
                    'fechaDesactivado' : fechaDesactivado,
                    'marcaCierreResultado' : str(item['cnprmmcre']).strip(),
                    'fechaSaldosPorReportes' : str(item['cnprmfsld']).strip(),
                    'reglaNegocioGop' : str(item['cnprmcpog']).strip() # Gestion = "G" o por Periodo = "P"
            })

            result['parametrosContabilidadCnprm'] = array
            result['total'] = len(array)
            result['mensaje'] = "Cargado Correctamente"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_cnprm)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

@app.route(modulo + programa + '/ValidarSiChequeEmitidoParaDepositoEnCuenta', methods=["GET"])
@auth_decorator()
def f0400_proceso_cheques_ts322():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f0400_proceso_cheques_ts322'

    try:
        codigoBanco = None
        numeroCuenta = None
        numeroCheque = None

        if 'codigoBanco' in  request.args  and 'numeroCuenta' in  request.args  and 'numeroCheque' in  request.args:
            codigoBanco =  request.args.get('codigoBanco')
            numeroCuenta =  request.args.get('numeroCuenta')
            numeroCheque =  request.args.get('numeroCheque')

            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, codigoBanco)
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, numeroCuenta)
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, numeroCheque)

            sql_tscdc = "SELECT tscdccbco, tscdcncta, tscdcnchq, tscdccbcd, tscdcnctd FROM tscdc WHERE tscdccbco = " + str(codigoBanco) + " AND tscdcncta = '" + str(numeroCuenta) + "' AND tscdcnchq = '" + str(numeroCheque) + "'"
        elif 'codigoBanco' in  request.args:
            codigoBanco =  request.args.get('codigoBanco')
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, codigoBanco)
            sql_tscdc = "SELECT tscdccbco, tscdcncta, tscdcnchq, tscdccbcd, tscdcnctd FROM tscdc WHERE tscdccbco = " + str(codigoBanco) + ""
        elif 'numeroCuenta' in  request.args:
            numeroCuenta =  request.args.get('numeroCuenta')
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, numeroCuenta)
            sql_tscdc = "SELECT tscdccbco, tscdcncta, tscdcnchq, tscdccbcd, tscdcnctd FROM tscdc WHERE tscdcncta = '" + str(numeroCuenta) + "'"
        elif 'numeroCheque' in  request.args:
            numeroCheque =  request.args.get('numeroCheque')
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, numeroCheque)
            sql_tscdc = "SELECT tscdccbco, tscdcncta, tscdcnchq, tscdccbcd, tscdcnctd FROM tscdc WHERE tscdcnchq = '" + str(numeroCheque) + "'"
        else:
            sql_tscdc = "SELECT tscdccbco, tscdcncta, tscdcnchq, tscdccbcd, tscdcnctd FROM tscdc"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_tscdc)

        db.conectar()
        rsp_tscdc = db.query(sql_tscdc)
        array = []
        i = 0
        print(rsp_tscdc)
        if rsp_tscdc is None:
            mensaje = 'No se encuentran registros'
            result['total'] = 0
            result['mensaje'] = mensaje
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_tscdc:
                i_tscdc = collections.OrderedDict()

                array.append({
                    'codigoBanco' : str(item['tscdccbco']).strip(),
                    'numeroCuenta' : str(item['tscdcncta']).strip(),
                    'numeroCheque' : str(item['tscdcnchq']).strip(),
                    'codigoBancoDestino' : str(item['tscdccbcd']).strip(),
                    'numeroCuentaDestino' : str(item['tscdcnctd']).strip()
            })

            result['dataTscdc'] = array
            result['total'] = len(array)
            result['mensaje'] = "Cargado Correctamente"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_tscdc)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

@app.route(modulo + programa + '/BuscarTransaccionesCaja', methods=["GET"])
@auth_decorator()
def f6300_transacciones_caja_ts322():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f6300_transacciones_caja_ts322'

    try:

        numeroDeposito = None

        if 'numeroDeposito' in  request.args: 
            numeroDeposito =  request.args.get('numeroDeposito')
            sql_cjtrn = "SELECT cjtrnmorg, cjtrntorg, cjtrnntra, cjtrnncja, cjtrnuneg FROM cjtrn WHERE cjtrnmorg = 96 AND cjtrntorg = " + numeroDeposito + " ORDER BY cjtrnntra "
        else:
            sql_cjtrn = "SELECT cjtrnmorg, cjtrntorg, cjtrnntra, cjtrnncja, cjtrnuneg FROM cjtrn WHERE cjtrnmorg = 96 ORDER BY cjtrnntra"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_cjtrn)

        db.conectar()
        rsp_cjtrn = db.query(sql_cjtrn)
        array = []
        i = 0

        if rsp_cjtrn is None:
            mensaje = 'No se encuentran registros para la transaccion ' + str(numeroDeposito)
            result['mensaje'] = mensaje
            result['total'] = 0
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
        else:
            for item in rsp_cjtrn:
                i_cjtrn = collections.OrderedDict()
               
                array.append({
                    'moduloOrigen' : str(item['cjtrnmorg']).strip(),
                    'numeroTransaccionOrigen' : str(item['cjtrntorg']).strip(),
                    'numeroTransaccion' : str(item['cjtrnntra']).strip(),
                    'numeroCaja' : str(item['cjtrnncja']).strip(),
                    'unidadNegocio' : str(item['cjtrnuneg']).strip()
                })

                result['transaccionesCajaCjtrn'] = array
                result['total'] = len(array)
                result['mensaje'] = "Cargado Correctamente"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_cjtrn)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

