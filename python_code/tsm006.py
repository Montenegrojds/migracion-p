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
programa = "/TiposDeTarjetasHabilitadas"
servicio = 'tsm006'
funcion = 'main'
#############################################################


class RegistrarTiposDeTarjetasHabilitadas(BaseSchema):
    tipoTarjeta = fields.Integer(required=True)
    usuario = fields.String(required=True)
    hora = fields.String(required=True)
    fechaProceso = fields.Date(required=True)

############################################
# ALTA DE REGISTROS
# REGISTRA TIPOS DE TARJETAS
############################################
@app.route(modulo + programa + '/Registrar', methods=["POST"])
@auth_decorator()
@required_params(RegistrarTiposDeTarjetasHabilitadas())
def f1000_altas_tsm006():
    resultado = {
        'mensaje': 'Las transacciones se realizaron exitosamente',
        'status': 200
    }

    funcion = 'f1000_altas_tsm006'
    parametros = []
   
    try:
        datos = request.json
        item = 1
        sql_insert_tstht = "insert into tstht (tsthtttar, tsthtuser, tsththora, tsthtfpro) values(" + str(datos['tipoTarjeta']) + ", '" + str(datos['usuario']) +  "', '" + str(datos['hora']) + "', '" +  str(datos['fechaProceso']) + "')"
       
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_insert_tstht)
        
        db.conectar()
        db.BEGIN_WORK()
        
        rsp_insert_tstht = db.insertar(sql_insert_tstht)
       
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_insert_tstht)
        
        if rsp_insert_tstht == 0:
            mensaje = "No se pudo insertar el registro en la tabla tstht"
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
            
            resultado['status'] = 200
            resultado['mensaje'] = mensaje
        else:
            mensaje = "El registro se inserto correctamente"
            resultado['mensaje'] = mensaje
            resultado['status'] = 200
            
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)

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


@app.route(modulo + programa + '/BuscarGbcon', methods=["GET"])
@auth_decorator()
def f5020_buscar_gbcon_tsm006():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5020_buscar_gbcon_tsm006'

    try:

        prefijoConcepto = None
        correlativoConcepto = None
        

        if 'prefijoConcepto' in  request.args and 'correlativoConcepto' in  request.args: 
            prefijoConcepto =  request.args.get('prefijoConcepto')
            correlativoConcepto =  request.args.get('correlativoConcepto')
            logging.info('INFO : [%s] [%s] Tipo Tarjeta [%s]', servicio, funcion, prefijoConcepto)
            logging.info('INFO : [%s] [%s] Tipo Tarjeta [%s]', servicio, funcion, correlativoConcepto)

            sql_gbcon = "SELECT gbconpfij, gbconcorr, gbcondesc FROM gbcon where gbconpfij = " + str(prefijoConcepto) + " AND gbconcorr  = " + str(correlativoConcepto)  + " AND gbconcorr > 0"
        else:
            sql_gbcon = "SELECT gbconpfij, gbconcorr, gbcondesc FROM gbcon WHERE gbconcorr > 0"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_gbcon)

        db.conectar()
        rsp_gbcon = db.query(sql_gbcon)
        array = []
        i = 0

        if rsp_gbcon is None:
            mensaje = 'No se encuentran registros'
            result['mensaje'] = mensaje
            result['total'] = 0
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
        else:
            for item in rsp_gbcon:
                i_gbcon = collections.OrderedDict()
               
                array.append({
                    'prefijoConcepto' : str(item['gbconpfij']).strip(),
                    'correlativoConcepto' : str(item['gbconcorr']).strip(),
                    'descripcion' : str(item['gbcondesc']).strip()
                })

                result['conceptosGlobales'] = array
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

@app.route(modulo + programa + '/BuscarTstht', methods=["GET"])
@auth_decorator()
def f5100_buscar_tstht_tsm006():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f5100_buscar_tstht_tsm006'

    try:
        
        sql_tstht = "SELECT * FROM tstht ORDER BY tsthtttar" 

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_tstht)

        db.conectar()
        rsp_tstht = db.query(sql_tstht)
        array = []

        if rsp_tstht is None:
            mensaje = 'No se encuentran registros'
            result['mensaje'] = mensaje
            result['total'] = 0
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
        else:
            for item in rsp_tstht:
                i_tstht = collections.OrderedDict()
               
                array.append({
                    'tipoTarjeta' : str(item['tsthtttar']).strip(),
                    'usuario' : str(item['tsthtuser']).strip(),
                    'hora' : str(item['tsththora']).strip(),
                    'fechaProceso' : str(item['tsthtfpro']).strip()
                })

                result['tipoTarjetasCreditosHabilitadasParaTransaccion'] = array
                result['total'] = len(array)
                result['mensaje'] = "Cargado Correctamente"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_tstht)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

