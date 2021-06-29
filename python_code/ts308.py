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
programa = "/DeshabilitacionCuentas"
servicio = 'ts308'
funcion = 'main'
#############################################################

###################
# ERRORES
###################
'''@app.route(modulo + programa + '/ErroresBaseDatos', methods=["GET"])
@auth_decorator()
def f0500_error_gb000():
    l_desc = None
    status = 200
    mensaje = None
    try:
        sql_gberr = "select * from gberr"
        #sql_gberr = "select gberrdesc as l_desc from gberr" WHERE gberrcerr = l_cerr
        db.conectar()
        rq_gberr = db.query(sql_gberr)
        ary_gberr = []
        i = 0
        print(rq_gberr)
        for t1 in rq_gberr:
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
    return {'status':status, 'mensaje':(mensaje)}'''

###########################
# MODIFICACION DE REGISTROS
###########################
class DeshabilitarCuentas(BaseSchema):
    numeroBanco = fields.Integer(required=True)
    numeroCuenta = fields.String(required=True)
    habilitada = fields.Integer(required=True)

@app.route(modulo + programa + '/Deshabilitar', methods=["PUT"])
@auth_decorator()
@required_params(DeshabilitarCuentas())
def f2000_modificar_ts308():
    resultado = {
        'mensaje': 'Deshabilitada correctamente',
        'status': 200
    }
    
    #db = Database()
    funcion = 'f2000_modificar_ts308'
    parametros = []
    operacion = "M"

    try:
        datos = request.json
        item = 1
        db.conectar()

        if datos['habilitada'] is not None and datos['numeroBanco'] is not None and datos['numeroCuenta'] is not None: 
            #and datos['numeroBanco'] is not None and datos['numeroCuenta'] is not None:
            #sql_update = "update tsccb set tsccbstat = " + datos['habilitada'] + " where tsccbcbco = '" + str(datos['numeroBanco'])  +  "' and tsccbncta = '" + datos['numeroCuenta']  + "'"
            sql_update = "update tsccb set tsccbstat = " + str(datos['habilitada']) + " where tsccbcbco = " + str(datos['numeroBanco'])  +  " and tsccbncta = " + datos['numeroCuenta']  + ""
            
            rq_update = db.actualizar(sql_update)
            print(sql_update)
            print(rq_update)
        else:
            resultado = {
                'mensaje': 'Peticion incorrecta',
                'status': 500
            }

        '''if g_mcfi == "S":
            if t2.tscbacpry is None:
                t2.tscbacpry == 0
            if t2.tscbacprg is None: 
                t2.tscbacprg == 0
            if t2.tscbacfin is None:
                t2.tscbacfin == 0

            sql_insert = "INSERT INTO tscba"'''

        if(datos['numeroCuenta'] is not None):  
            operacion = "M" 
        else:
            operacion = "A"

        
        
    except Exception as ex:
        resultado['status'] = 500
        resultado['mensaje'] = str(ex)
    finally:
        db.desconectar()

    return json.dumps(resultado, cls=CustomJSONEncoder), resultado['status']


#############################################################

@app.route(modulo + programa + '/ConsultaCuentas', methods=["GET"])
@auth_decorator()
def f4000_consulta_ts308():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f4000_consulta_ts308'

    codigoBanco = None
    codigoCuenta = None
    estadoCuenta = None

    try:

        if 'codigoBanco' in  request.args:
            codigoBanco =  request.args.get('codigoBanco')
            sql_tsccb = "select * from tsccb where tsccbcbco = " + str(codigoBanco) + " order by tsccbcbco, tsccbncta, tsccbstat"
        elif 'codigoCuenta' in  request.args:
            codigoCuenta =  request.args.get('codigoCuenta')
            sql_tsccb = "select * from tsccb where tsccbncta = '" + codigoCuenta + "' order by tsccbcbco, tsccbncta, tsccbstat"
        elif 'estadoCuenta' in  request.args:
            estadoCuenta =  request.args.get('estadoCuenta')
            sql_tsccb = "select * from tsccb where tsccbstat = '" + estadoCuenta + "' order by tsccbcbco, tsccbncta, tsccbstat"
        else:
            sql_tsccb = "select * from tsccb order by tsccbcbco, tsccbncta, tsccbstat"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_tsccb)

        db.conectar()
        rsp_tsccb = db.query(sql_tsccb)
        array = []
        i = 0
        print(rsp_tsccb)

        if rsp_tsccb is None:
            mensaje = 'No se encuentran registros'
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
        else:
            for item in rsp_tsccb:
                i_tsccb = collections.OrderedDict()
                
                array.append({
                    'numeroBanco' : str(item['tsccbcbco']).strip(),
                    'numeroCuenta' : str(item['tsccbncta']).strip(),
                    'unidadNegocio' : str(item['tsccbuneg']).strip(),
                    'moneda' : str(item['tsccbcmon']).strip(),
                    'saldoDisponibleActual' : str(item['tsccbsald']).strip(),
                    'sobregiroContratado' : str(item['tsccbsgro']).strip(),
                    'cuentaContable' : str(item['tsccbcctb']).strip(),
                    'analisisAdicional' : str(item['tsccbadic']).strip(),
                    'marcaChequeras' : str(item['tsccbmcch']).strip(),
                    'marcaLlenadoCheques' : str(item['tsccbmlch']).strip(),
                    'habilitada' : str(item['tsccbstat']).strip()
                })

                result['cuentasBancosTsccb'] = array
                result['total'] = len(array)
                result['mensaje'] = "Cargado Correctamente"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_tsccb)
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################
