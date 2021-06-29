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
programa = "/TipoMovimientos"
servicio = 'ts301'
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
    return {'status':status, 'mensaje':(mensaje)}'''


class RegistrarTipoMovimientos(BaseSchema):
    prefijo = fields.Integer(required=True)
    correlativo = fields.Integer(required=True)
    descripcion = fields.String(required=True)
    cuentaContable = fields.String(required=True)
    analisisAdicional = fields.Integer(required=True)

###################
# ALTA DE REGISTROS
###################
@app.route(modulo + programa + '/Registrar', methods=["POST"])
@auth_decorator()
@required_params(RegistrarTipoMovimientos())
def f1000_altas_ts301():
    resultado = {
        'mensaje': 'Guardado correctamente',
        'status': 200
    }
    
    #db = Database()
    funcion = 'f1000_altas_ts301'
    parametros = []
    operacion = "A"

    try:
        datos = request.json
        item = 1

        sql_insert = "insert into tstmv (tstmvpref, tstmvcorr, tstmvdesc, tstmvctbl, tstmvadic) values('" + str(datos['prefijo']) + "', '" + str(datos['correlativo']) +  "', '" + datos['descripcion'] + "', " + datos['cuentaContable'] + ", '" +  str(datos['analisisAdicional']) +  "')"
        
        db.conectar()
        db.BEGIN_WORK()

        print(sql_insert)
        rsp_insert = db.insertar(sql_insert)

        if rsp_insert == 0:
            mensaje = "No se pudo insertar el registro"
            print('f1000_altas_ts301 mensaje: ', mensaje)
            resultado['status'] = 500
            resultado['mensaje'] = mensaje
        else:
            mensaje = "El registro se inserto correctamente"
            print('f1000_altas_ts301 rsp_insert: ', mensaje)
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
class ModificarTipoMovimientos(BaseSchema):
    prefijo = fields.Integer(required=True)
    correlativo = fields.Integer(required=True)
    descripcion = fields.String(required=True)
    cuentaContable = fields.String(required=True)
    analisisAdicional = fields.Integer(required=True)

@app.route(modulo + programa + '/Modificar', methods=["PUT"])
@auth_decorator()
@required_params(ModificarTipoMovimientos())
def f2000_modificar_ts301():
    resultado = {
        'mensaje': 'Actualizado correctamente',
        'status': 200
    }
    
    #db = Database()
    funcion = 'f2000_modificar_ts301'
    parametros = []
    operacion = "M"

    try:
        datos = request.json
        item = 1
        
        sql_update = "update tstmv set tstmvpref = " + str(datos['prefijo']) + ", tstmvdesc = '" + datos['descripcion'] +  "', tstmvctbl = '" + datos['cuentaContable'] + "', tstmvadic = " + str(datos['analisisAdicional'])  + " where  tstmvcorr = " + str(datos['correlativo']) + ""
        print(sql_update)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_update)
        db.conectar()
        db.BEGIN_WORK()
        rsp_update = db.actualizar(sql_update)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_update)
        if rsp_update == 0:
            mensaje = "No se encontro el registro solicitado, correlativo: " + datos['correlativo'] 
            print('f2000_modificar_ts301 mensaje: ', mensaje)
            resultado['status'] = 500
            resultado['mensaje'] = mensaje
        else:
            mensaje = "El registro " +  str(datos['correlativo'])  + " se actualizo correctamente"
            print('f2000_modificar_ts301 rsp_update: ', mensaje)
            resultado['mensaje'] = mensaje

        print(rsp_update)
        db.COMMIT_WORK()

        if(datos['correlativo'] is not None):  
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

class EliminarTipoMovimientos(BaseSchema):
    correlativo = fields.Integer(required=True)


##################
# BORRAR REGISTROS
##################
@app.route(modulo + programa + '/Eliminar', methods=["DELETE"])
@auth_decorator()
@required_params(EliminarTipoMovimientos())
def f3000_borrar_ts301():
    
    resultado = {
        'mensaje': 'Eliminado correctamente',
        'status': 200
    }
    
    #db = Database()
    funcion = 'f3000_borrar_ts301'
    parametros = []
    operacion = "E"

    try:
        datos = request.json
        item = 1
        
        sql_delete = "delete tstmv" +  " where tstmvcorr = " + datos['correlativo']  + ""
        print(sql_delete)

        db.conectar()
        rsp_delete = db.eliminar(sql_delete)
        
        print(rsp_delete)

        print('f3000_borrar_ts301 rsp_delete: ', rsp_delete)

        if rsp_delete == 0:
            mensaje = "No se encontro el registro solicitado, correlativo: " + datos['correlativo'] 
            print('f3000_borrar_ts301 mensaje: ', mensaje)
            resultado['status'] = 500
            resultado['mensaje'] = mensaje
        else:
            print('f3000_borrar_ts301 rsp_delete: ', "El registro " +  datos['correlativo']  + " se elimino correctamente")
        
    except Exception as ex:
        resultado['status'] = 500
        resultado['mensaje'] = str(ex)
    finally:
        db.desconectar()

    return json.dumps(resultado, cls=CustomJSONEncoder), resultado['status']
    
#############################################################

@app.route(modulo + programa + '/Consultar', methods=["GET"])
@auth_decorator()
def f4000_consulta_ts301():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f4000_consulta_ts301'

    try:
        prefijo = None
        correlativo = None
        descripcion = None
        cuentaContable = None
        
        if 'prefijo' in  request.args:
            prefijo =  request.args.get('prefijo')
            sql_tstmv = "select * from tstmv where tstmvpref < 3 and tstmvpref = " + str(prefijo) + " order by tstmvpref, tstmvcorr"
        elif 'correlativo' in  request.args:
            correlativo =  request.args.get('correlativo')
            sql_tstmv = "select * from tstmv where tstmvpref < 3 and tstmvcorr = '" + correlativo + "' order by tstmvpref, tstmvcorr"
        elif 'descripcion' in  request.args:
            descripcion =  request.args.get('descripcion')
            sql_tstmv = "select * from tstmv where tstmvpref < 3 and tstmvdesc = " + descripcion + " order by tstmvpref, tstmvcorr"
        elif 'cuentaContable' in  request.args:
            cuentaContable =  request.args.get('cuentaContable')
            sql_tstmv = "select * from tstmv where tstmvpref < 3 and tstmvctbl = " + cuentaContable + " order by tstmvpref, tstmvcorr"
        else:
            print('All')
            sql_tstmv = "select * from tstmv where tstmvpref < 3 order by tstmvpref, tstmvcorr"

        db.conectar()
        rsp_tstmv = db.query(sql_tstmv)
        array = []
        i = 0
        print(rsp_tstmv)
        for item in rsp_tstmv:
            i_tstmv = collections.OrderedDict()
            array.append({
                'prefijo' : str(item['tstmvpref']).strip(),
                'correlativo' : str(item['tstmvcorr']).strip(),
                'descripcion' : str(item['tstmvdesc']).strip(),
                'cuentaContable' : str(item['tstmvctbl']).strip(),
                'analisisAdicional' : str(item['tstmvadic']).strip()
            })

        result['tipoMovimientosTstmv'] = array
        result['total'] = len(array)
        result['mensaje'] = "Cargado Correctamente"
        mensaje = json.dumps(array)
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

