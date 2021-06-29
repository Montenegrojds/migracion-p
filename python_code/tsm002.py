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
programa = "/FirmasAutorizadasCuentas"
servicio = 'tsm002'
funcion = 'main'
#############################################################


class RegistrarFirmasAutorizadasCuentas(BaseSchema):
    unidadNegocio = fields.Integer(required=True)
    codigoBanco = fields.Integer(required=True)
    numeroCuenta = fields.String(required=True)
    codigoCliente = fields.String(required=True)

############################################
# ALTA DE REGISTROS
# REGISTRA FIRMAS AUTORIZADAS POR U/N
############################################
@app.route(modulo + programa + '/Registrar', methods=["POST"])
@auth_decorator()
@required_params(RegistrarFirmasAutorizadasCuentas())
def f1000_altas_tsm002():
    resultado = {
        'mensaje': 'Guardado correctamente',
        'status': 200
    }
    

    funcion = 'f1000_altas_tsm002'
    parametros = []
   

    try:
        datos = request.json
        item = 1

        sql_delete = "delete tsfau where tsfauuneg = " + str(datos['unidadNegocio']) + " and tsfaucbco = " + str(datos['codigoBanco'])  +  " and tsfauncta = '" + str(datos['numeroCuenta']) + "'"
        sql_insert = "insert into tsfau (tsfauuneg, tsfaucbco, tsfauncta, tsfaucage) values(" + str(datos['unidadNegocio']) + ", " + str(datos['codigoBanco']) +  ", '" + str(datos['numeroCuenta']) + "', '" +  str(datos['codigoCliente']) +  "')"

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
# MODIFICACION FIRMAS AUTORIZADAS POR U/N
#########################################
class ModificarFirmasAutorizadasCuentas(BaseSchema):
    unidadNegocio = fields.Integer(required=True)
    codigoBanco = fields.Integer(required=True)
    numeroCuenta = fields.String(required=True)
    codigoClienteAntiguo = fields.Integer(required=True)
    codigoClienteNuevo = fields.Integer(required=True)


@app.route(modulo + programa + '/Modificar', methods=["PUT"])
@auth_decorator()
@required_params(ModificarFirmasAutorizadasCuentas())
def f2000_modificar_tsm002():
    resultado = {
        'mensaje': 'Actualizado correctamente',
        'status': 200
    }
    
    #db = Database()
    funcion = 'f2000_modificar_tsm002'
    parametros = []
   

    try:
        datos = request.json
        item = 1

        sql_update = "update tsfau set tsfauuneg = " + str(datos['unidadNegocio']) + ", tsfaucbco = " + str(datos['codigoBanco']) + ", tsfauncta = '" + str(datos['numeroCuenta']) +  "', tsfaucage = " + str(datos['codigoClienteNuevo']) +  "  where tsfaucage = " + str(datos['codigoClienteAntiguo'])  + ""
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

class EliminarFirmasAutorizadasCuentas(BaseSchema):
    unidadNegocio= fields.Integer(required=True)
    codigoBanco = fields.Integer(required=True)
    numeroCuenta = fields.String(required=True)

####################################################
# BORRAR REGISTROS FIRMAS AUTORIZADAS POR U/N
####################################################
@app.route(modulo + programa + '/Eliminar', methods=["DELETE"])
@auth_decorator()
@required_params(EliminarFirmasAutorizadasCuentas())
def f3000_borrar_tsm002():
    
    resultado = {
        'mensaje': 'Eliminado correctamente',
        'status': 200
    }
    
    #db = Database()
    funcion = 'f3000_borrar_tsm002'
    parametros = []


    try:
        datos = request.json
        item = 1
        

        if datos['codigoAgenda'] is not None:
            for item in datos['codigoAgenda']:
                logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, item)
                sql_delete = "delete tsfau where tsfauuneg = " + str(datos['unidadNegocio']) + " and tsfaucbco = " + str(datos['codigoBanco']) + " and tsfauncta = '" + str(datos['numeroCuenta']) + "' and tsfaucage = " + item + ""
        else:
            sql_delete = "delete tsfau where tsfauuneg = " + str(datos['unidadNegocio']) + " and tsfaucbco = " + str(datos['codigoBanco']) + " and tsfauncta = '" + str(datos['numeroCuenta']) + "'"
        

        db.conectar()
        db.BEGIN_WORK()
        rsp_delete = db.eliminar(sql_delete)
        print(rsp_delete)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_delete)


        if rsp_delete == 0:
            mensaje = "No se encontro el registro solicitado, unidadNegocio: " + str(datos['unidadNegocio']) + " codigoBanco: " + str(datos['codigoBanco']) + " numeroCuenta: " + str(datos['numeroCuenta'])
            print('f3000_borrar_tsm002 mensaje: ', mensaje)
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
    
#############################################################

@app.route(modulo + programa + '/Consultar', methods=["GET"])
@auth_decorator()
def f4000_consulta_tsm002():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f4000_consulta_tsm002'

    try:

        unidadNegocio = None
        codigoBanco = None
        numeroCuenta = None
        codigoCliente = None

        
        if 'codigoBanco' in  request.args: 
            codigoBanco =  request.args.get('codigoBanco')
            sql_tsfau = "SELECT * FROM tsfau where tsfaucbco = " + codigoBanco + " ORDER BY tsfaucbco, tsfauncta, tsfaucage"
        elif 'numeroCuenta' in  request.args: 
            numeroCuenta =  request.args.get('numeroCuenta')
            sql_tsfau = "SELECT * FROM tsfau where tsfauncta = " + numeroCuenta + "  ORDER BY tsfaucbco, tsfauncta, tsfaucage"
        elif 'codigoCliente' in  request.args: 
            codigoCliente =  request.args.get('codigoCliente')
            sql_tsfau = "SELECT * FROM tsfau where tsfaucage = " + codigoCliente + " ORDER BY tsfaucbco, tsfauncta, tsfaucage"
        else:
            sql_tsfau = "SELECT * FROM tsfau ORDER BY tsfaucbco, tsfauncta, tsfaucage"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_tsfau)

        db.conectar()
        rsp_tsfau = db.query(sql_tsfau)
        array = []
        i = 0

        if rsp_tsfau is None:
            mensaje = 'No se encuentran registros'
            result['mensaje'] = mensaje
            result['total'] = 0
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
        else:
            for item in rsp_tsfau:
                i_tsfau = collections.OrderedDict()
               
                array.append({
                    'unidadNegocio' : str(item['tsfauuneg']).strip(),
                    'codigoBanco' : str(item['tsfaucbco']).strip(),
                    'numeroCuenta' : str(item['tsfauncta']).strip(),
                    'codigoCliente' : str(item['tsfaucage']).strip()
                })

                result['firmaAutorizadaTsfau'] = array
                result['total'] = len(array)
                result['mensaje'] = "Cargado Correctamente"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_tsfau)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

@app.route(modulo + programa + '/ConsultarConceptosGlobales', methods=["GET"])
@auth_decorator()
def f5010_buscar_gbcon_tsm002():

    g_flag = False
    l_stat = ''
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5010_buscar_gbcon_tsm002'

    try:
        prefijoConcepto = None
        correlativoConcepto = None
        
        if 'prefijoConcepto' in  request.args and 'correlativoConcepto' in  request.args: 
            prefijoConcepto =  request.args.get('prefijoConcepto')
            correlativoConcepto =  request.args.get('correlativoConcepto')
            sql_gbcon = "SELECT gbconpfij, gbconcorr, gbcondesc as l_desc FROM gbcon where gbconpfij = " + prefijoConcepto + " and gbconcorr = " + correlativoConcepto + ""
        else:
            sql_gbcon = "SELECT gbconpfij, gbconcorr, gbcondesc as l_desc FROM gbcon"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_gbcon)

        db.conectar()
        rsp_gbcon = db.query(sql_gbcon)
        array = []
        i = 0

        if rsp_gbcon is None:
            #mensaje = 'No se encuentran registros'
            array.append({
                    'prefijoConcepto' : prefijoConcepto,
                    'correlativoConcepto' : correlativoConcepto,
                    'existe' : 'FALSE',
                    'descripcion' : ''
            })

            result['firmaAutorizadaGbcon'] = array
            result['total'] = len(array)
            result['mensaje'] = "Cargado Correctamente"
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_gbcon:
                i_gbcon = collections.OrderedDict()

                array.append({
                    'prefijoConcepto' : str(item['gbconpfij']).strip(),
                    'correlativoConcepto' : str(item['gbconcorr']).strip(),
                    'existe' : 'TRUE',
                    'descripcion' : str(item['l_desc']).strip()
                })

                result['firmaAutorizadaGbcon'] = array
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

@app.route(modulo + programa + '/ConsultarCuentasEnBancos', methods=["GET"])
@auth_decorator()
def f5020_buscar_tsccb_tsm002():

    g_flag = False
    l_stat = ''
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5020_buscar_tsccb_tsm002'

    try:
        codigoBanco = None
        numeroCuenta = None
        
        if 'codigoBanco' in  request.args and 'numeroCuenta' in  request.args: 
            codigoBanco =  request.args.get('codigoBanco')
            numeroCuenta =  request.args.get('numeroCuenta')
            sql_tsccb = "SELECT tsccbcbco, tsccbncta, tsccbstat as l_stat FROM tsccb where tsccbcbco = " + codigoBanco + " and tsccbncta = " + numeroCuenta + ""
        else:
            sql_tsccb = "SELECT tsccbcbco, tsccbncta, tsccbstat as l_stat FROM tsccb"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_tsccb)

        db.conectar()
        rsp_tsccb = db.query(sql_tsccb)
        array = []
        i = 0

        if rsp_tsccb is None:
            #mensaje = 'No se encuentran registros'
            array.append({
                    'codigoBanco' : codigoBanco,
                    'numeroCuenta' : numeroCuenta,
                    'existe' : 'FALSE',
                    'estado' : ''
            })

            result['firmaAutorizadaTsccb'] = array
            result['total'] = len(array)
            result['mensaje'] = "Cargado Correctamente"
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_tsccb:
                i_tsccb = collections.OrderedDict()

                if str(item['l_stat']).strip() == '1':
                    l_stat = 'Habilitada'
                else:
                    l_stat = 'Deshabilitada'
               
                array.append({
                    'codigoBanco' : str(item['tsccbcbco']).strip(),
                    'numeroCuenta' : str(item['tsccbncta']).strip(),
                    'existe' : 'TRUE',
                    'estado' : l_stat
                })

                result['firmaAutorizadaTsccb'] = array
                result['total'] = len(array)
                result['mensaje'] = "Cargado Correctamente"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_tsccb)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

@app.route(modulo + programa + '/RegistroClientes', methods=["GET"])
@auth_decorator()
def f5040_buscar_gbage_tsm002():

    g_msj = ''
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5040_buscar_gbage_tsm002'

    try:
        codigoAgenda = None
        
        if 'codigoAgenda' in  request.args : 
            codigoAgenda =  request.args.get('codigoAgenda')
            sql_gbage = "SELECT * FROM gbage where gbagecage = " + codigoAgenda + ""
        else:
            sql_gbage = "SELECT * FROM gbage"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_gbage)

        db.conectar()
        rsp_gbage = db.query(sql_gbage)
        array = []
        i = 0

        if rsp_gbage is None:
            #mensaje = 'No se encuentran registros'
            array.append({
                    'codigoAgenda' : codigoAgenda,
                    'existe' : 'FALSE'
            })

            result['firmaAutorizadaGbage'] = array
            result['total'] = len(array)
            result['mensaje'] = "Cargado Correctamente"
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_gbage:
                i_gbage = collections.OrderedDict()

                if str(item['gbagestat']).strip() == '2':
                    g_msj = 'Codigo Deshabilitado'
                elif str(item['gbagestat']).strip() == '1':
                    g_msj = 'Codigo Habilitado'

                array.append({
                    'codigoAgenda' : str(item['gbagecage']).strip(),
                    'nombreRazonSocial' : str(item['gbagenomb']).strip(),
                    'estadoCliente' : g_msj,
                    'estaHabilitado' : str(item['gbagestat']).strip(),
                    'existe' : 'TRUE'
                })

                result['firmaAutorizadaGbage'] = array
                result['total'] = len(array)
                result['mensaje'] = "Cargado Correctamente"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_gbage)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

@app.route(modulo + programa + '/EsEmpleado', methods=["GET"])
@auth_decorator()
def f5050_buscar_suemp_tsm002():

    g_msj = ''
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5050_buscar_suemp_tsm002'
    logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, "ENTER")
    try:
        codigoAgenda = None
        
        if 'codigoAgenda' in  request.args : 
            codigoAgenda =  request.args.get('codigoAgenda')
            sql_suemp = "SELECT * FROM suemp where suempcemp = " + codigoAgenda + ""
        else:
            sql_suemp = "SELECT * FROM suemp"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_suemp)

        db.conectar()
        rsp_suemp = db.query(sql_suemp)
        array = []
        i = 0

        if rsp_suemp is None:
            #mensaje = 'No se encuentran registros'
            array.append({
                    'codigoAgenda' : codigoAgenda,
                    'esEmpleado' : 'FALSE'
            })

            result['firmaAutorizadaSuemp'] = array
            result['total'] = len(array)
            result['mensaje'] = "Cargado Correctamente"
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'])
        else:
            for item in rsp_suemp:
                i_suemp = collections.OrderedDict()

                array.append({
                    'codigoAgenda' : str(item['suempcemp']).strip(),
                    'esEmpleado' : 'TRUE'
                })

                result['firmaAutorizadaSuemp'] = array
                result['total'] = len(array)
                result['mensaje'] = "Cargado Correctamente"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_suemp)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    
    return json.dumps(result, cls=CustomJSONEncoder), result['status']