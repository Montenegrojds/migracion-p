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
programa = "/FormatoImpresionCheques"
servicio = 'ts309'
funcion = 'main'
#############################################################

class RegistrarFormatoImpresionCheques(BaseSchema):
    fmtoImpresion = fields.Integer(required=True)
    descImpresion = fields.String(required=True)

###################
# ALTA DE REGISTROS
###################
@app.route(modulo + programa + '/Registrar', methods=["POST"])
@auth_decorator()
@required_params(RegistrarFormatoImpresionCheques())
def f1000_altas_ts309():
    
    resultado = {
        'mensaje': 'Guardado correctamente',
        'status': 200
    }
    
    #db = Database()
    funcion = 'f1000_altas_ts309'
    parametros = []
    operacion = "A"

    try:
        datos = request.json
        item = 1

        sql_insert = "insert into tsfcb (tsfcbfmto, tsfcbdesc) values(" + str(datos['fmtoImpresion']) + ", '" + str(datos['descImpresion']) + "')"
        
        db.conectar()
        db.BEGIN_WORK()

        print(sql_insert)
        rsp_insert = db.insertar(sql_insert)
        print(rsp_insert)

        if rsp_insert == 0:
            mensaje = "No se pudo insertar el registro"
            print('f1000_altas_ts309 mensaje: ', mensaje)
            resultado['status'] = 500
            resultado['mensaje'] = mensaje
        else:
            mensaje = "El registro se inserto correctamente"
            print('f1000_altas_ts309 rsp_insert: ', mensaje)
            resultado['mensaje'] = mensaje

        db.COMMIT_WORK()

        '''if(datos['correlativo'] is not None):  
            operacion = "M" 
        else:
            operacion = "A"'''

        
        
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
class ModificarFormatoImpresionCheques(BaseSchema):
    fmtoImpresion = fields.Integer(required=True)
    descImpresion = fields.String(required=True)

@app.route(modulo + programa + '/Modificar', methods=["PUT"])
@auth_decorator()
@required_params(ModificarFormatoImpresionCheques())
def f2000_modificar_ts309():
    resultado = {
        'mensaje': 'Actualizado correctamente',
        'status': 200
    }
    
    #db = Database()
    funcion = 'f2000_modificar_ts309'
    parametros = []
    operacion = "M"

    try:
        datos = request.json
        item = 1
        
        sql_update = "update tsfcb set tsfcbdesc = '" +  datos['descImpresion'] + "' where  tsfcbfmto = " + str(datos['fmtoImpresion']) + ""
        print(sql_update)

        db.conectar()
        db.BEGIN_WORK()
        rsp_update = db.actualizar(sql_update)

        if rsp_update == 0:
            mensaje = "No se encontro el registro solicitado, fmtoImpresion: " + str(datos['fmtoImpresion']) 
            print('f2000_modificar_ts309 mensaje: ', mensaje)
            resultado['status'] = 500
            resultado['mensaje'] = mensaje
        else:
            mensaje = "El registro " +  str(datos['fmtoImpresion'])  + " se actualizo correctamente"
            print('f2000_modificar_ts309 rsp_update: ', mensaje)
            resultado['mensaje'] = mensaje
        
        print(rsp_update)
        db.COMMIT_WORK()

    except Exception as ex:
        db.ROLLBACK_WORK()
        resultado['status'] = 500
        resultado['mensaje'] = str(ex)
    finally:
        db.desconectar()

    return json.dumps(resultado, cls=CustomJSONEncoder), resultado['status']

class EliminarFormatoImpresionCheques(BaseSchema):
    fmtoImpresion = fields.Integer(required=True)


##################
# BORRAR REGISTROS
##################
@app.route(modulo + programa + '/Eliminar', methods=["DELETE"])
@auth_decorator()
@required_params(EliminarFormatoImpresionCheques())
def f3000_borrar_ts309():
    
    resultado = {
        'mensaje': 'Eliminado correctamente',
        'status': 200
    }
    
    #db = Database()
    funcion = 'f3000_borrar_ts309'
    parametros = []
    operacion = "E"

    try:
        datos = request.json
        item = 1
        
        sql_delete = "delete tsfcb where tsfcbfmto = " + str(datos['fmtoImpresion']) + ""
        print(sql_delete)

        db.conectar()
        rsp_delete = db.eliminar(sql_delete)
        
        print(rsp_delete)

        print('f3000_borrar_ts309 rsp_delete: ', rsp_delete)

        if rsp_delete == 0:
            mensaje = "No se encontro el registro solicitado, fmtoImpresion: " + str(datos['fmtoImpresion']) 
            print('f3000_borrar_ts309 mensaje: ', mensaje)
            resultado['status'] = 500
            resultado['mensaje'] = mensaje
        else:
            print('f3000_borrar_ts309 rsp_delete: ', "El registro " +  str(datos['fmtoImpresion'])  + " se elimino correctamente")
        
       
        
        
    except Exception as ex:
        resultado['status'] = 500
        resultado['mensaje'] = str(ex)
    finally:
        db.desconectar()

    return json.dumps(resultado, cls=CustomJSONEncoder), resultado['status']
    
#############################################################

@app.route(modulo + programa + '/BuscarRegistro', methods=["GET"])
@auth_decorator()
def f5000_buscar_registro_ts309():
   
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }

    funcion = 'f4000_consulta_ts308'
    logging.info('INFO: [%s] [%s]', servicio, funcion)

    try:
        fmtoImpresion = None
        descImpresion = None
        
        if 'fmtoImpresion' in  request.args:
            fmtoImpresion =  request.args.get('fmtoImpresion')
            sql_tsfcb = "select * from tsfcb where tsfcbfmto  = '" + str(fmtoImpresion) + "' order by tsfcbfmto"
        elif 'descImpresion' in  request.args:
            numeroBanco =  request.args.get('descImpresion')
            sql_tsfcb = "select * from tsfcb where tsfcbdesc  = " + str(descImpresion) + " order by tsfcbdesc"
        else:
            sql_tsfcb = "select * from tsfcb order by tsfcbfmto"

        db.conectar()
        rsp_tsfcb = db.query(sql_tsfcb)
        ary_tsfcb = []
        i = 0
        print(rsp_tsfcb)
        for item in rsp_tsfcb:
            i_tsfcb = collections.OrderedDict()
            ary_tsfcb.append({
                'fmtoImpresion' : item['tsfcbfmto'],
                'descImpresion' : item['tsfcbdesc']
            })

        result['formatoImpresionChequesTsfcb'] = ary_tsfcb
        result['total'] = len(ary_tsfcb)
        result['mensaje'] = "Cargado Correctamente"
        mensaje = json.dumps(ary_tsfcb)
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

#############################################################

@app.route(modulo + programa + '/BuscarEmpresa', methods=["GET"])
@auth_decorator()
def f6050_buscar_empresa_ts309():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f6050_buscar_empresa_ts309'

    try:
        
        sql_gbpmt = "select * from gbpmt order by gbpmtfdia"

        db.conectar()
        rsp_gbpmt = db.query(sql_gbpmt)
        ary_gbpmt = []
        i = 0
        print(rsp_gbpmt)
        
        for item in rsp_gbpmt:
            i_gbpmt = collections.OrderedDict()
            print(item['gbpmtfdia'])
            ary_gbpmt.append({
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
                'direccion2' : str(item['gbpmtdir2']).strip(),
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

        result['parametrosInicialesGbpmt'] = ary_gbpmt
        result['total'] = len(ary_gbpmt)
        result['mensaje'] = "Cargado Correctamente"
        mensaje = json.dumps(ary_gbpmt)
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

