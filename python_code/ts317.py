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
programa = "/CuentasFinanciador"
servicio = 'ts317'
funcion = 'main'
#############################################################

###################
# ERRORES
###################
#############################################################



class RegistrarCuentasFinanciador(BaseSchema):
    codigoFinanciador = fields.Integer(required=True)
    numeroBanco = fields.Integer(required=True)
    numeroCuenta = fields.String(required=True)

###################
# ALTA DE REGISTROS
###################
@app.route(modulo + programa + '/Registrar', methods=["POST"])
@auth_decorator()
@required_params(RegistrarCuentasFinanciador())
def f1000_altas_ts317():
    resultado = {
        'mensaje': 'Guardado correctamente',
        'status': 200
    }
    
    #db = Database()
    funcion = 'f1000_altas_ts317'
    parametros = []
    operacion = "A"

    try:
        datos = request.json
        item = 1

        sql_insert = "insert into tscfi (tscficfin, tscficbco, tscfincta) values('" + str(datos['codigoFinanciador']) + "', '" + str(datos['numeroBanco']) +  "', '" + datos['numeroCuenta'] + "')"
        
        db.conectar()
        db.BEGIN_WORK()

        print(sql_insert)
        rsp_insert = db.insertar(sql_insert)
        print(rsp_insert)

        if rsp_insert == 0:
            mensaje = "No se pudo insertar el registro"
            print('f1000_altas_ts317 mensaje: ', mensaje)
            resultado['status'] = 500
            resultado['mensaje'] = mensaje
        else:
            mensaje = "El registro se inserto correctamente"
            print('f1000_altas_ts317 rsp_insert: ', mensaje)
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
class ModificarCuentasFinanciador(BaseSchema):
    codigoFinanciador = fields.Integer(required=True)
    numeroBanco = fields.Integer(required=True)
    numeroCuenta = fields.String(required=True)

@app.route(modulo + programa + '/Modificar', methods=["PUT"])
@auth_decorator()
@required_params(ModificarCuentasFinanciador())
def f2000_modificar_ts317():
    resultado = {
        'mensaje': 'Actualizado correctamente',
        'status': 200
    }
    
    #db = Database()
    funcion = 'f2000_modificar_ts317'
    parametros = []
    operacion = "M"

    try:
        datos = request.json
        item = 1
        
        sql_update = "update tscfi set tscficbco = " + str(datos['numeroBanco']) + ", tscfincta = '" + datos['numeroCuenta'] + "' where  tscficfin = '" + str(datos['codigoFinanciador']) + "'"
        print(sql_update)

        db.conectar()
        #db.BEGIN_WORK()
        rsp_update = db.actualizar(sql_update)

        if rsp_update == 0:
            mensaje = "No se encontro el registro solicitado, codigoFinanciador: " + datos['codigoFinanciador'] 
            print('f2000_modificar_ts317 mensaje: ', mensaje)
            resultado['status'] = 500
            resultado['mensaje'] = mensaje
        else:
            mensaje = "El registro " +  str(datos['codigoFinanciador'])  + " se actualizo correctamente"
            print('f2000_modificar_ts317 rsp_update: ', mensaje)
            resultado['mensaje'] = mensaje
        
        print(rsp_update)
        #db.COMMIT_WORK()

        '''if(datos['correlativo'] is not None):  
            operacion = "M" 
        else:
            operacion = "A"'''

        
        
    except Exception as ex:
        #db.ROLLBACK_WORK()
        resultado['status'] = 500
        resultado['mensaje'] = str(ex)
    finally:
        db.desconectar()

    return json.dumps(resultado, cls=CustomJSONEncoder), resultado['status']

class EliminarCuentasFinanciador(BaseSchema):
    codigoFinanciador = fields.Integer(required=True)


##################
# BORRAR REGISTROS
##################
@app.route(modulo + programa + '/Eliminar', methods=["DELETE"])
@auth_decorator()
@required_params(EliminarCuentasFinanciador())
def f3000_borrar_ts317():
    
    resultado = {
        'mensaje': 'Eliminado correctamente',
        'status': 200
    }
    
    #db = Database()
    funcion = 'f3000_borrar_ts317'
    parametros = []
    operacion = "E"

    try:
        datos = request.json
        item = 1
        
        sql_delete = "delete tscfi" +  " where tscficfin = " + datos['codigoFinanciador']  + ""
        print(sql_delete)

        db.conectar()
        rsp_delete = db.eliminar(sql_delete)
        
        print(rsp_delete)

        print('f3000_borrar_ts317 rsp_delete: ', rsp_delete)

        if rsp_delete == 0:
            mensaje = "No se encontro el registro solicitado, codigoFinanciador: " + datos['codigoFinanciador'] 
            print('f3000_borrar_ts317 mensaje: ', mensaje)
            resultado['status'] = 500
            resultado['mensaje'] = mensaje
        else:
            print('f3000_borrar_ts317 rsp_delete: ', "El registro " +  datos['codigoFinanciador']  + " se elimino correctamente")
        
        

        '''

        if(datos['numeroCuenta'] is not None):  
            operacion = "M" 
        else:
            operacion = "A"'''

        
        
    except Exception as ex:
        resultado['status'] = 500
        resultado['mensaje'] = str(ex)
    finally:
        db.desconectar()

    return json.dumps(resultado, cls=CustomJSONEncoder), resultado['status']
    
#############################################################

@app.route(modulo + programa + '/Consultar', methods=["GET"])
@auth_decorator()
def f4000_consulta_ts317():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f4000_consulta_ts317'

    try:
        codigoFinanciador = None
        numeroBanco = None
        numeroCuenta = None
        
        if 'codigoFinanciador' in  request.args:
            codigoFinanciador =  request.args.get('codigoFinanciador')
            sql_tscfi = "select * from tscfi where tscficfin  = " + str(codigoFinanciador) + " order by tscficfin"
        elif 'numeroBanco' in  request.args:
            numeroBanco =  request.args.get('numeroBanco')
            sql_tscfi = "select * from tscfi where tscficfin  = " + str(numeroBanco) + " order by tscficfin"
        elif 'numeroCuenta' in  request.args:
            numeroCuenta =  request.args.get('numeroCuenta')
            sql_tscfi = "select * from tscfi where tscficfin  = " + str(numeroCuenta) + " order by tscficfin"
        else:
            print('All')
            sql_tscfi = "select * from tscfi order by tscficfin"

        db.conectar()
        rsp_tscfi = db.query(sql_tscfi)
        ary_tscfi = []
        i = 0
        print(rsp_tscfi)
        for item in rsp_tscfi:
            i_tscfi = collections.OrderedDict()
            ary_tscfi.append({
                'codigoFinanciador' : str(item['tscficfin']).strip(),
                'numeroBanco' : str(item['tscficbco']).strip(),
                'numeroCuenta' : str(item['tscfincta']).strip()
            })

        result['cuentasFinanciadorTscfi'] = ary_tscfi
        result['total'] = len(ary_tscfi)
        result['mensaje'] = "Cargado Correctamente"
        mensaje = json.dumps(ary_tscfi)
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

