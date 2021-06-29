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
programa = "/TiposDeTarjetas"
servicio = 'tsm003'
funcion = 'main'
#############################################################


class RegistrarTiposDeTarjetas(BaseSchema):
    tipoTarjeta = fields.Integer(required=True)
    descripcion = fields.String(required=True)
    codigoAdmTarjeta = fields.Integer(required=True)
    porcentajeComisionPago = fields.Decimal(required=True)
    tipoCxCImporteVenta = fields.Integer(required=True)
    tipoCxCComision = fields.Integer(required=True)
    aplicacion = fields.Integer(required=True)
    marcaGeneracionCuentas = fields.Integer(required=True)
    cantidadCuotas = fields.Integer(required=True)
    usuario = fields.String(required=True)
    hora = fields.String(required=True)
    fechaProceso = fields.Date(required=True)
    relacionConceptos = fields.String(required=True)

############################################
# ALTA DE REGISTROS
# REGISTRA TIPOS DE TARJETAS
############################################
@app.route(modulo + programa + '/Registrar', methods=["POST"])
@auth_decorator()
@required_params(RegistrarTiposDeTarjetas())
def f1000_altas_tsm003():
    resultado = {
        'mensaje': 'Las transacciones se realizaron exitosamente',
        'status': 200
    }

    funcion = 'f1000_altas_tsm003'
    parametros = []
   

    try:
        datos = request.json
        item = 1
        sql_insert_tsttc = "insert into tsttc (tsttcttrj, tsttcdesc, tsttccage, tsttcpcom, tsttctciv, tsttctcic, tsttccapl, tsttcmgen, tsttcccuo, tsttcuser, tsttchora, tsttcfpro, tsttcmcon) values(" + str(datos['tipoTarjeta']) + ", '" + str(datos['descripcion']) +  "', " + str(datos['codigoAdmTarjeta']) + ", " +  str(datos['porcentajeComisionPago']) + ", " +  str(datos['tipoCxCImporteVenta']) + ", " +  str(datos['tipoCxCComision']) + ", " +  str(datos['aplicacion']) + ", " +  str(datos['marcaGeneracionCuentas']) + ", " +  str(datos['cantidadCuotas']) + ", '" +  str(datos['usuario']) + "', '" +  str(datos['hora']) + "', '" +  str(datos['fechaProceso']) + "', '" +  str(datos['relacionConceptos']) +  "')"
        sql_delete_gbcon = "delete gbcon where gbconpfij = 12 and gbconcorr = " + str(datos['tipoTarjeta'])  +  ""
        sql_insert_gbcon = "insert into gbcon (gbconpfij, gbconcorr, gbcondesc, gbconabre) values(12, " + str(datos['tipoTarjeta']) + ", '" + str(datos['descripcion']) +  "', NULL)"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_insert_tsttc)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_delete_gbcon)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_insert_gbcon)

        db.conectar()
        db.BEGIN_WORK()
        
        rsp_insert_tsttc = db.insertar(sql_insert_tsttc)
        rsp_delete_gbcon = db.eliminar(sql_delete_gbcon)
        rsp_insert_gbcon = db.insertar(sql_insert_gbcon)

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_insert_tsttc)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_delete_gbcon)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_insert_gbcon)

        if rsp_insert_tsttc == 0:
            mensaje = "No se pudo insertar el registro en la tabla tsttc"
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
            
            resultado['status'] = 200
            resultado['mensaje'] = mensaje
            db.ROLLBACK_WORK()

        if rsp_delete_gbcon == 0:
            mensaje = "No se pudo eliminar el registro " + str(datos['tipoTarjeta'])  + " de la tabla gbcon"
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
            
        if rsp_insert_gbcon == 0:
            mensaje = "No se pudo insertar el registro " + str(datos['tipoTarjeta'])  + " en la tabla gbcon"
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
            
            resultado['status'] = 200
            resultado['mensaje'] = mensaje
            db.ROLLBACK_WORK()

        db.COMMIT_WORK()

    except Exception as ex:
        db.ROLLBACK_WORK()
        resultado['status'] = 500
        resultado['mensaje'] = str(ex)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, str(ex))
    finally:
        db.desconectar()

    return json.dumps(resultado, cls=CustomJSONEncoder), resultado['status']

#############################################################


#########################################
# MODIFICACION TIPOS DE TARJETAS
#########################################
class ModificarTiposDeTarjetas(BaseSchema):
    tipoTarjeta = fields.Integer(required=True)
    descripcion = fields.String(required=True)
    codigoAdmTarjeta = fields.Integer(required=True)
    porcentajeComisionPago = fields.Decimal(required=True)
    tipoCxCImporteVenta = fields.Integer(required=True)
    tipoCxCComision = fields.Integer(required=True)
    aplicacion = fields.Integer(required=True)
    marcaGeneracionCuentas = fields.Integer(required=True)
    cantidadCuotas = fields.Integer(required=True)
    usuario = fields.String(required=True)
    hora = fields.String(required=True)
    fechaProceso = fields.Date(required=True)
    relacionConceptos = fields.String(required=True)


@app.route(modulo + programa + '/Modificar', methods=["PUT"])
@auth_decorator()
@required_params(ModificarTiposDeTarjetas())
def f2000_modificar_tsm003():
    resultado = {
        'mensaje': 'Actualizado correctamente',
        'status': 200
    }
    
    funcion = 'f2000_modificar_tsm003'
    parametros = []
   

    try:
        datos = request.json
        item = 1
        sql_update_tsttc = "update tsttc set tsttcdesc = '" + str(datos['descripcion'])+ "' , tsttccage = " + str(datos['codigoAdmTarjeta']) + " , tsttcpcom = " + str(datos['porcentajeComisionPago']) + " , tsttctciv = " + str(datos['tipoCxCImporteVenta']) + " , tsttctcic = " + str(datos['tipoCxCComision']) + " , tsttccapl = " + str(datos['aplicacion']) + " , tsttcmgen = " + str(datos['marcaGeneracionCuentas']) + " , tsttcccuo = " + str(datos['cantidadCuotas']) + ", tsttcuser = '" + str(datos['usuario']) + "' , tsttchora = '" + str(datos['hora']) + "', tsttcfpro = '" + str(datos['fechaProceso']) + "' , tsttcmcon = '" + str(datos['relacionConceptos']) + "' WHERE  tsttcttrj = " + str(datos['tipoTarjeta']) + ""
        sql_delete_gbcon = "delete gbcon where gbconpfij = 12 and gbconcorr = " + str(datos['tipoTarjeta'])  +  ""
        sql_insert_gbcon = "insert into gbcon (gbconpfij, gbconcorr, gbcondesc, gbconabre) values(12, " + str(datos['tipoTarjeta']) + ", '" + str(datos['descripcion']) +  "', NULL)"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_update_tsttc)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_delete_gbcon)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_insert_gbcon)

        db.conectar()
        db.BEGIN_WORK()
        
        rsp_update_tsttc = db.actualizar(sql_update_tsttc)
        rsp_delete_gbcon = db.eliminar(sql_delete_gbcon)
        rsp_insert_gbcon = db.insertar(sql_insert_gbcon)

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_update_tsttc)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_delete_gbcon)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_insert_gbcon)

        if rsp_update_tsttc == 0:
            mensaje = "No se pudo insertar el registro en la tabla tsttc"
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
            
            resultado['status'] = 200
            resultado['mensaje'] = mensaje
            db.ROLLBACK_WORK()

        if rsp_delete_gbcon == 0:
            mensaje = "No se pudo eliminar el registro " + str(datos['tipoTarjeta'])  + " de la tabla gbcon"
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
            
        if rsp_insert_gbcon == 0:
            mensaje = "No se pudo insertar el registro " + str(datos['tipoTarjeta'])  + " en la tabla gbcon"
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
            
            resultado['status'] = 200
            resultado['mensaje'] = mensaje
            db.ROLLBACK_WORK()

        db.COMMIT_WORK()

    except Exception as ex:
        db.ROLLBACK_WORK()
        resultado['status'] = 500
        resultado['mensaje'] = str(ex)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, str(ex))
    finally:
        db.desconectar()

    return json.dumps(resultado, cls=CustomJSONEncoder), resultado['status']
#############################################################

class EliminarTiposDeTarjetas(BaseSchema):
    tipoTarjeta = fields.Integer(required=True)


####################################################
# BORRAR REGISTROS TIPOS DE TARJETAS
####################################################
@app.route(modulo + programa + '/Eliminar', methods=["DELETE"])
@auth_decorator()
@required_params(EliminarTiposDeTarjetas())
def f3000_borrar_tsm003():
    l_cntr = 0
    resultado = {
        'mensaje': 'Eliminado correctamente',
        'status': 200
    }
    
    funcion = 'f3000_borrar_tsm003'
    parametros = []

    try:
        datos = request.json
        item = 1
        
        sql_query = "SELECT COUNT(*) AS l_cntr FROM tstrj where tstrjttrj = " + str(datos['tipoTarjeta'])   + ""
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_query)

        db.conectar()
        db.BEGIN_WORK()
        rsp_query = db.query(sql_query)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_query)

        for item in rsp_query:
            l_cntr = str(item['l_cntr']).strip()
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, l_cntr)

        
        if l_cntr ==  '0':
            mensaje = 'No se encuentra el tipo de tarjeta en la tabla tstrj, se puede eliminar'
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)

            sql_delete_tsttc = "DELETE tsttc WHERE tsttcttrj = " + str(datos['tipoTarjeta'])   + ""
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_delete_tsttc)
            rsp_delete_tsttc = db.eliminar(sql_delete_tsttc)
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_delete_tsttc)

            if sql_delete_tsttc == 0:
                mensaje = "No se pudo borrar de la tabla tsttc, no se encontro el registro solicitado, tipoTarjeta: " + str(datos['tipoTarjeta']) + ""
                print('f3000_borrar_tsm003 Mensaje: ', mensaje)

                resultado['status'] = 200
                resultado['mensaje'] = mensaje
                resultado['total'] = 0
            else:
                mensaje = "El registro " +  str(datos['tipoTarjeta'])  + " se elimino correctamente de la tabla tsttc"
                resultado['status'] = 200
                resultado['mensaje'] = mensaje
                resultado['total'] = 1

                #if str(datos['tipoTarjeta']) == 'N':
                sql_delete_gbcon = "DELETE gbcon WHERE gbconpfij = 12 AND gbconcorr = " + str(datos['tipoTarjeta'])  +  ""
                logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_delete_gbcon)
                rsp_delete_gbcon = db.eliminar(sql_delete_gbcon)
                logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_delete_gbcon)

                if rsp_delete_gbcon == 0:
                    mensaje = "No se pudo borrar de la tabla gbcon, no se encontro el registro solicitado, tipoTarjeta: " + str(datos['tipoTarjeta']) + ""
                    
                    resultado['status'] = 200
                    resultado['mensaje'] = mensaje
                    resultado['total'] = 0
                else:
                    mensaje = "El registro " +  str(datos['tipoTarjeta'])  + " se elimino correctamente de las tablas gbcon y tsttc"
                    resultado['status'] = 200
                    resultado['mensaje'] = mensaje
                    resultado['total'] = 1

        else:
            mensaje = 'Tipo de tarjeta utilizado no se puede borrar'
            resultado['mensaje'] = mensaje
            resultado['total'] = 0
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
            db.ROLLBACK_WORK()


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
def f4000_consulta_tsm003():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f4000_consulta_tsm003'

    try:

        tipoTarjeta = None
        descripcion = None
        codigoAdmTarjeta = None
        porcentajeComisionPago = None
        tipoCxCImporteVenta = None
        tipoCxCComision = None
        aplicacion = None
        cantidadCuotas = None
        marcaGeneracionCuentas = None

        if 'tipoTarjeta' in  request.args: 
            tipoTarjeta =  request.args.get('tipoTarjeta')
            sql_tsttc = "SELECT * FROM tsttc where tsttcttrj = " + tipoTarjeta + " ORDER BY tsttcttrj"
        elif 'descripcion' in  request.args: 
            descripcion =  request.args.get('descripcion')
            sql_tsttc = "SELECT * FROM tsttc where tsttcdesc = " + descripcion + "  ORDER BY tsttcttrj"
        elif 'codigoAdmTarjeta' in  request.args: 
            codigoAdmTarjeta =  request.args.get('codigoAdmTarjeta')
            sql_tsttc = "SELECT * FROM tsttc where tsttccage = " + codigoAdmTarjeta + " ORDER BY tsttcttrj"
        elif 'porcentajeComisionPago' in  request.args: 
            porcentajeComisionPago =  request.args.get('porcentajeComisionPago')
            sql_tsttc = "SELECT * FROM tsttc where tsttcpcom = " + porcentajeComisionPago + "  ORDER BY tsttcttrj"
        elif 'tipoCxCImporteVenta' in  request.args: 
            tipoCxCImporteVenta =  request.args.get('tipoCxCImporteVenta')
            sql_tsttc = "SELECT * FROM tsttc where tsttctciv = " + tipoCxCImporteVenta + " ORDER BY tsttcttrj"
        elif 'tipoCxCComision' in  request.args: 
            tipoCxCComision =  request.args.get('tipoCxCComision')
            sql_tsttc = "SELECT * FROM tsttc where tsttctcic = " + tipoCxCComision + "  ORDER BY tsttcttrj"
        elif 'aplicacion' in  request.args: 
            aplicacion =  request.args.get('aplicacion')
            sql_tsttc = "SELECT * FROM tsttc where tsttccapl = " + aplicacion + " ORDER BY tsttcttrj"
        elif 'cantidadCuotas' in  request.args: 
            cantidadCuotas =  request.args.get('cantidadCuotas')
            sql_tsttc = "SELECT * FROM tsttc where tsttcccuo = " + cantidadCuotas + "  ORDER BY tsttcttrj"
        elif 'marcaGeneracionCuentas' in  request.args: 
            marcaGeneracionCuentas =  request.args.get('marcaGeneracionCuentas')
            sql_tsttc = "SELECT * FROM tsttc where tsttcmgen = " + marcaGeneracionCuentas + " ORDER BY tsttcttrj"
        else:
            sql_tsttc = "SELECT * FROM tsttc ORDER BY tsttcttrj"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_tsttc)

        db.conectar()
        rsp_tsttc = db.query(sql_tsttc)
        array = []
        i = 0

        if rsp_tsttc is None:
            mensaje = 'No se encuentran registros'
            result['mensaje'] = mensaje
            result['total'] = 0
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
        else:
            for item in rsp_tsttc:
                i_tsttc = collections.OrderedDict()
               
                array.append({
                    'tipoTarjeta' : str(item['tsttcttrj']).strip(),
                    'descripcion' : str(item['tsttcdesc']).strip(),
                    'codigoAdmTarjeta' : str(item['tsttccage']).strip(),
                    'porcentajeComisionPago' : str(item['tsttcpcom']).strip(),
                    'tipoCxCImporteVenta' : str(item['tsttctciv']).strip(),
                    'tipoCxCComision' : str(item['tsttctcic']).strip(),
                    'aplicacion' : str(item['tsttccapl']).strip(),
                    'marcaGeneracionCuentas' : str(item['tsttcmgen']).strip(),
                    'cantidadCuotas' : str(item['tsttcccuo']).strip(),
                    'usuario' : str(item['tsttcuser']).strip(),
                    'hora' : str(item['tsttchora']).strip(),
                    'fechaProceso' : str(item['tsttcfpro']).strip(),
                    'relacionConceptos' : str(item['tsttcmcon']).strip() # Relacion con conceptos (S/N)
                })

                result['tiposTarjetaCredito'] = array
                result['total'] = len(array)
                result['mensaje'] = "Cargado Correctamente"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_tsttc)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

######################################
# BUSQUEDA DE DATOS TIPOS DE TARJETAS
######################################

@app.route(modulo + programa + '/BuscarRegistro', methods=["GET"])
@auth_decorator()
def f5000_buscar_registro_tsm003():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5000_buscar_registro_tsm003'

    try:
        tipoTarjeta = None

        if 'tipoTarjeta' in  request.args: 
            tipoTarjeta =  request.args.get('tipoTarjeta')
            logging.info('INFO : [%s] [%s] Tipo Tarjeta [%s]', servicio, funcion, tipoTarjeta)
            sql_tsttc = "SELECT * FROM tsttc where tsttcttrj = " + str(tipoTarjeta) + ""
        else:
            sql_tsttc = "SELECT * FROM tsttc" 

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_tsttc)

        db.conectar()
        rsp_tsttc = db.query(sql_tsttc)
        array = []

        if rsp_tsttc is None:
            sql_gbcon = "SELECT gbcondesc FROM gbcon WHERE gbconpfij = 12 AND gbconcorr = " + str(tipoTarjeta) + ""
            print(sql_tsttc)
            rsp_gbcon = db.query(sql_gbcon)
            print(rsp_gbcon)

            if rsp_gbcon is None:
                array.append({
                        'descripcion' : None,
                        'relacionConConceptos' : "N"
                })

                result['data'] = array
                result['total'] = len(array)
                result['mensaje'] = "Cargado Correctamente"
            else:
                for item in rsp_gbcon:
                    i_gbcon = collections.OrderedDict()
                
                    array.append({
                        'descripcion' : str(item['gbcondesc']).strip(),
                        'relacionConConceptos' : "S"
                    })

                    result['data'] = array
                    result['total'] = len(array)
                    result['mensaje'] = "Cargado Correctamente"

        else:
            for item in rsp_tsttc:
                i_tsttc = collections.OrderedDict()
               
                array.append({
                    'tipoTarjeta' : str(item['tsttcttrj']).strip(),
                    'descripcion' : str(item['tsttcdesc']).strip(),
                    'codigoAdmTarjeta' : str(item['tsttccage']).strip(),
                    'porcentajeComisionPago' : str(item['tsttcpcom']).strip(),
                    'tipoCxCImporteVenta' : str(item['tsttctciv']).strip(),
                    'tipoCxCComision' : str(item['tsttctcic']).strip(),
                    'aplicacion' : str(item['tsttccapl']).strip(),
                    'marcaGeneracionCuentas' : str(item['tsttcmgen']).strip(), # 1=Resumen por Caja 2=Por cada nota de venta
                    'cantidadCuotas' : str(item['tsttcccuo']).strip(),
                    'usuario' : str(item['tsttcuser']).strip(),
                    'hora' : str(item['tsttchora']).strip(),
                    'fechaProceso' : str(item['tsttcfpro']).strip(),
                    'relacionConConceptos' : str(item['tsttcmcon']).strip() # Relacion con conceptos (S/N)
                })

                result['tipoTarjetasCredito'] = array
                result['total'] = len(array)
                result['mensaje'] = "Cargado Correctamente"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_tsttc)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

@app.route(modulo + programa + '/BuscarCodigoAgenda', methods=["GET"])
@auth_decorator()
def f5010_buscar_gbage_tsm003():
    g_nomb = None
    g_stat = None

    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5010_buscar_gbage_tsm003'

    try:

        codigoAdmTarjeta = None
        
        if 'codigoAdmTarjeta' in  request.args: 
            codigoAdmTarjeta =  request.args.get('codigoAdmTarjeta')
            logging.info('INFO : [%s] [%s] Codigo Agenda [%s]', servicio, funcion, codigoAdmTarjeta)
            sql_gbage = "SELECT gbagecage, gbagenomb as g_nomb, gbagestat as g_stat FROM gbage WHERE gbagecage = " + codigoAdmTarjeta + ""
        else:
            sql_gbage = "SELECT gbagecage, gbagenomb as g_nomb, gbagestat as g_stat FROM gbage"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_gbage)

        db.conectar()
        rsp_gbage = db.query(sql_gbage)
        array = []
        i = 0

        if rsp_gbage is None:
            mensaje = 'No se encuentran registros'
            result['mensaje'] = mensaje
            result['total'] = 0
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
        else:
            for item in rsp_gbage:
                i_gbage = collections.OrderedDict()
               
                array.append({
                    'codigoAgenda' : str(item['gbagecage']).strip(),
                    'nombreRazonSocial' : str(item['g_nomb']).strip(),
                    'estadoCliente' : str(item['g_stat']).strip()
                })

                result['registroClientes'] = array
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

@app.route(modulo + programa + '/BuscarTiposCuentas', methods=["GET"])
@auth_decorator()
def f5020_buscar_cptcp_tsm003():
    l_apld = None

    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5020_buscar_cptcp_tsm003'

    try:

        codigoTipoCuenta = None
        
        if 'codigoTipoCuenta' in  request.args: 
            codigoTipoCuenta =  request.args.get('codigoTipoCuenta')
            logging.info('INFO : [%s] [%s] Tipo Cuenta [%s]', servicio, funcion, codigoTipoCuenta)
            sql_cptcp = "SELECT cptcpctcp, cptcpclsc, cptcpapld as l_apld, cptcpdesc FROM cptcp WHERE cptcpclsc = 2 AND cptcpctcp = " + str(codigoTipoCuenta) + ""
        else:
            sql_cptcp = "SELECT cptcpctcp, cptcpclsc, cptcpapld as l_apld, cptcpdesc FROM cptcp"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_cptcp)

        db.conectar()
        rsp_cptcp = db.query(sql_cptcp)
        array = []
        i = 0

        if rsp_cptcp is None:
            mensaje = 'No se encuentran registros'
            result['mensaje'] = mensaje
            result['total'] = 0
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
        else:
            for item in rsp_cptcp:
                i_cptcp = collections.OrderedDict()
               
                array.append({
                    'codigoTipoCuenta' : str(item['cptcpctcp']).strip(),
                    'claseCuenta' : str(item['cptcpclsc']).strip(),  #Pagar, Cobrar 1: CxP, 2: CxC
                    'marcaPorAplicacionDiferida' : str(item['l_apld']).strip(),#   N=No   C=Con C/F (c/Plan Devengamiento) S=Sin C/F (c/Plan Devengamiento) P=En el Pago (S/Plan Dev.)
                    'descripcion' : str(item['cptcpdesc']).strip()
                })

                result['registroClientes'] = array
                result['total'] = len(array)
                result['mensaje'] = "Cargado Correctamente"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_cptcp)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

@app.route(modulo + programa + '/BuscarAplicaciones', methods=["GET"])
@auth_decorator()
def f5030_buscar_cpapl_tsm003():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5030_buscar_cpapl_tsm003'

    try:

        codigoAplicacion = None
        
        if 'codigoAplicacion' in  request.args: 
            codigoAplicacion =  request.args.get('codigoAplicacion')
            logging.info('INFO : [%s] [%s] Codigo Aplicacion [%s]', servicio, funcion, codigoAplicacion)
            sql_cpapl = "SELECT * FROM cpapl WHERE cpaplclsc = 2 AND cpaplcapl = " + str(codigoAplicacion) + ""
        else:
            sql_cpapl = "SELECT * FROM cpapl"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_cpapl)

        db.conectar()
        rsp_cpapl = db.query(sql_cpapl)
        array = []
        i = 0

        if rsp_cpapl is None:
            mensaje = 'No se encuentran registros'
            result['mensaje'] = mensaje
            result['total'] = 0
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
        else:
            for item in rsp_cpapl:
                i_cpapl = collections.OrderedDict()
               
                array.append({
                    'claseCuenta' : str(item['cpaplclsc']).strip(), #Pagar, Cobrar 1: CxP, 2: CxC
                    'codigoAplicacion' : str(item['cpaplcapl']).strip(),  
                    'descripcion' : str(item['cpapldesc']).strip(),
                    'tipoAplicacion' : str(item['cpapltapl']).strip(), #1=Gastos, 2=Provision, 0=CxC
                    'cuentaContable' : str(item['cpaplcctb']).strip(),
                    'analisisAdicional' : str(item['cpapladic']).strip(),
                    'gastoExento' : str(item['cpaplgexe']).strip()
                })

                result['aplicaciones'] = array
                result['total'] = len(array)
                result['mensaje'] = "Cargado Correctamente"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_cpapl)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

@app.route(modulo + programa + '/CuentaDeResultado', methods=["GET"])
@auth_decorator()
def f5040_cuenta_de_resultado_tsm003():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5040_cuenta_de_resultado_tsm003'

    try:
        l_natu = None
        status = None
        cuentaContableFirstCharacter = None

        sql_cnprm = "SELECT * FROM cnprm"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_cnprm)

        db.conectar()
        rsp_cnprm = db.query(sql_cnprm)
        array = []
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_cnprm)
        print(rsp_cnprm)

        if rsp_cnprm is None:
            if l_natu == None or l_natu == '':
                l_natu = 'O'
                status = False
            else:
                status = False
            
            array.append({
                    'status' : str(status).strip()
            })

            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, array)
            
            result['respuesta'] = array
            result['mensaje'] = "Cargado Correctamente"
            result['total'] = len(array)

            
        else:
            
            if 'cuentaContableFirstCharacter' in  request.args: 
                cuentaContableFirstCharacter =  request.args.get('cuentaContableFirstCharacter')
                logging.info('INFO : [%s] [%s] Primer caracter de la cuenta contable [%s]', servicio, funcion, cuentaContableFirstCharacter)
                for item in rsp_cnprm:
                    if cuentaContableFirstCharacter == '1':
                        l_natu = str(item['cnprmncp1']).strip()
                    elif cuentaContableFirstCharacter == '2':
                        l_natu = str(item['cnprmncp2']).strip()
                    elif cuentaContableFirstCharacter == '3':
                        l_natu = str(item['cnprmncp3']).strip()
                    elif cuentaContableFirstCharacter == '4':
                        l_natu = str(item['cnprmncp4']).strip()
                    elif cuentaContableFirstCharacter == '5':
                        l_natu = str(item['cnprmncp5']).strip()
                    elif cuentaContableFirstCharacter == '6':
                        l_natu = str(item['cnprmncp6']).strip()
                    elif cuentaContableFirstCharacter == '7':
                        l_natu = str(item['cnprmncp7']).strip()
                    elif cuentaContableFirstCharacter == '8':
                        l_natu = str(item['cnprmncp8']).strip()
                    elif cuentaContableFirstCharacter == '9':
                        l_natu = str(item['cnprmncp9']).strip()

                    logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, l_natu)
                    print(l_natu)
                    
                    if l_natu == None or l_natu == '':
                        l_natu = 'O'
                        status = False
                    
                    if l_natu == 'I' or l_natu == 'E':
                        status = True
                    else:
                        status = False

                    array.append({
                        'status' : str(status).strip()
                    })

                result['respuesta'] = array
                result['total'] = len(array)
                result['mensaje'] = "Cargado Correctamente"
            else:
                mensaje = 'Solicitud invalida, debe enviar el primer caracter de la cuenta contable'
                result['mensaje'] = mensaje
                result['total'] = 0
                logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)

            

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, result['mensaje'] )
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    
    return json.dumps(result, cls=CustomJSONEncoder), result['status']
