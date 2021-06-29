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
programa = "/ChequerasHabilitadasUsuario"
servicio = 'tsm001'
funcion = 'main'
#############################################################


class RegistrarChequerasHabilitadasUsuario(BaseSchema):
    codigoUsuario = fields.String(required=True)
    numeroChequera = fields.String(required=True)
    usuarioChequera = fields.String(required=True)
    horaChequera = fields.String(required=True)
    fechaProcesoChequera = fields.Date(required=True)

############################################
# ALTA DE REGISTROS
# REGISTRA CHEQUERAS HABILITADAS POR USUARIO
############################################
@app.route(modulo + programa + '/Registrar', methods=["POST"])
@auth_decorator()
@required_params(RegistrarChequerasHabilitadasUsuario())
def f1000_altas_tsm001():
    resultado = {
        'mensaje': 'Guardado correctamente',
        'status': 200
    }
    

    funcion = 'f1000_altas_tsm001'
    parametros = []
   

    try:
        datos = request.json
        item = 1

        sql_insert = "insert into tscpu (tscpuusrn, tscpunoca, tscpuuser, tscpuhora, tscpufpro) values('" + str(datos['codigoUsuario']) + "', '" + str(datos['numeroChequera']) +  "', '" + str(datos['usuarioChequera']) + "', '" + str(datos['horaChequera']) + "', '" +  str(datos['fechaProcesoChequera']) +  "')"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_insert)
        
        db.conectar()
        db.BEGIN_WORK()
        
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



################################################
# MODIFICACION CHEQUERAS HABILITADAS POR USUARIO
################################################
class ModificarChequerasHabilitadasUsuario(BaseSchema):
    codigoUsuario = fields.String(required=True)
    numeroChequera = fields.String(required=True)
    usuarioChequera = fields.String(required=True)
    horaChequera = fields.String(required=True)
    fechaProcesoChequera = fields.Date(required=True)


@app.route(modulo + programa + '/Modificar', methods=["PUT"])
@auth_decorator()
@required_params(ModificarChequerasHabilitadasUsuario())
def f2000_modificar_tsm001():
    resultado = {
        'mensaje': 'Actualizado correctamente',
        'status': 200
    }
    
    #db = Database()
    funcion = 'f2000_modificar_tsm001'
    parametros = []
   

    try:
        datos = request.json
        item = 1

        sql_update = "update tscpu set tscpunoca = '" + str(datos['numeroChequera']) + "', tscpuuser = '" + str(datos['usuarioChequera']) +  "', tscpuhora = '" + str(datos['horaChequera']) +  "', tscpufpro = '" + str(datos['fechaProcesoChequera']) +  "'  where tscpuusrn = '" + str(datos['codigoUsuario'])  + "'"
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_update)

        db.conectar()
        db.BEGIN_WORK()
        rsp_update = db.actualizar(sql_update)
        
        if rsp_update == 0:
            mensaje = "No se encontro el registro solicitado, codigoUsuario: " + datos['codigoUsuario'] 
            
            resultado['status'] = 500
            resultado['mensaje'] = mensaje
        else:
            mensaje = "El registro " +  str(datos['codigoUsuario'])  + " se actualizo correctamente"
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

class EliminarChequerasHabilitadasUsuario(BaseSchema):
    codigoUsuario= fields.String(required=True)


####################################################
# BORRAR REGISTROS CHEQUERAS HABILITADAS POR USUARIO
####################################################
@app.route(modulo + programa + '/Eliminar', methods=["DELETE"])
@auth_decorator()
@required_params(EliminarChequerasHabilitadasUsuario())
def f3000_borrar_tsm001():
    
    resultado = {
        'mensaje': 'Eliminado correctamente',
        'status': 200
    }
    
    #db = Database()
    funcion = 'f3000_borrar_tsm001'
    parametros = []


    try:
        datos = request.json
        item = 1
        
        sql_delete = "delete tscpu" +  " where tscpuusrn = '" + str(datos['codigoUsuario'])  + "'"
        

        db.conectar()
        db.BEGIN_WORK()
        rsp_delete = db.eliminar(sql_delete)
    
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_delete)


        if rsp_delete == 0:
            mensaje = "No se encontro el registro solicitado, codigoUsuario: " + datos['codigoUsuario'] 
            print('f3000_borrar_tsm001 mensaje: ', mensaje)
            resultado['status'] = 500
            resultado['mensaje'] = mensaje
        else:
            mensaje = "El registro " +  str(datos['codigoUsuario'])  + " se elimino correctamente"
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
def f4000_consulta_tsm001():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f4000_consulta_tsm001'

    try:

        codigoUsuario = None
        nombreUsuario = None
        fechaNacimiento = None
        direccion = None
        telefono = None
        clave = None
        fechaUltCambioClave = None
        numeroCajaActiva = None
        codigoAgencia = None
        statusUsuario = None
        marcaLoginUsuario = None
        utilizaGui = None
        viasAutorizadas = None
        fechaMarca = None
        marcaBaja = None
        usuario = None
        hora = None
        fechaProceso = None
        unidadNegocio = None
        usrCula = None
        codigoAgenda = None

        numeroChequera = None
        usuarioChequera = None
        horaChequera = None
        fechaProcesoChequera = None

        
        if 'codigoUsuario' in  request.args: 
            codigoUsuario =  request.args.get('codigoUsuario')
            sql_adusr_tscpu = "SELECT DISTINCT *, tscpu.tscpunoca as numerochequera, tscpu.tscpuuser as usuariochequera  FROM adusr JOIN tscpu ON adusrusrn = tscpuusrn AND adusrmrcb = 0 ORDER BY adusrusrn"
        elif 'nombreUsuario' in  request.args: 
            nombreUsuario =  request.args.get('nombreUsuario')
            sql_adusr_tscpu = "SELECT DISTINCT *, tscpu.tscpunoca as numerochequera  FROM adusr JOIN tscpu ON adusrusrn = tscpuusrn AND adusrmrcb = 0 ORDER BY adusrusrn"
        else:
            sql_adusr_tscpu = "SELECT DISTINCT *, tscpu.tscpunoca as numerochequera, tscpu.tscpuuser as usuariochequera FROM adusr JOIN tscpu ON adusrusrn = tscpuusrn ORDER BY adusrusrn"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_adusr_tscpu)

        db.conectar()
        rsp_adusr_tscpu = db.query(sql_adusr_tscpu)
        array = []
        i = 0

        if rsp_adusr_tscpu is None:
            mensaje = 'No se encuentran registros'
            result['mensaje'] = mensaje
            result['total'] = 0
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
        else:
            for item in rsp_adusr_tscpu:
                i_adusr_tscpu = collections.OrderedDict()
               
                array.append({
                    'codigoUsuario' : str(item['adusrusrn']).strip(),
                    'nombreUsuario' : str(item['adusrnomb']).strip(),
                    'fechaNacimiento' : str(item['adusrfnac']).strip(),
                    'direccion' : str(item['adusrdir1']).strip(),
                    'telefono' : str(item['adusrtelf']).strip(),
                    'clave' : str(item['adusrclav']).strip(),
                    'fechaUltCambioClave' : str(item['adusrfcla']).strip(),
                    'numeroCajaActiva' : str(item['adusrcaja']).strip(),
                    'codigoAgencia' : str(item['adusragen']).strip(),
                    'statusUsuario' : str(item['adusrstat']).strip(),
                    'marcaLoginUsuario' : str(item['adusrmlog']).strip(),
                    'utilizaGui' : str(item['adusrmgui']).strip(),
                    'viasAutorizadas' : str(item['adusrvias']).strip(),
                    'fechaMarca' : str(item['adusrfmrc']).strip(),
                    'marcaBaja' : str(item['adusrmrcb']).strip(),
                    'usuario' : str(item['adusruser']).strip(),
                    'hora' : str(item['adusrhora']).strip(),
                    'fechaProceso' : str(item['adusrfpro']).strip(),
                    'unidadNegocio' : str(item['adusruneg']).strip(),
                    'usrCula' : str(item['adusrcula']).strip(),
                    'codigoAgenda' : str(item['adusrcage']).strip(),

                    'numeroChequera' : str(item['numerochequera']).strip(),
                    'usuarioChequera' : str(item['usuariochequera']).strip()
                })

                result['cuentasTscpu'] = array
                result['total'] = len(array)
                result['mensaje'] = "Cargado Correctamente"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_adusr_tscpu)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    
    return json.dumps(result, cls=CustomJSONEncoder), result['status']

