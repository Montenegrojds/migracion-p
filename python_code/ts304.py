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
programa = "/DosificacionCheques"
servicio = 'ts304'
funcion = 'main'
#############################################################


class RegistrarDosificacionCheques(BaseSchema):
    numeroChequera = fields.String(required=True)
    descripcion = fields.String(required=True)
    fechaRegistro = fields.Date(required=True)
    numeroBanco = fields.Integer(required=True)
    numeroCuenta = fields.String(required=True)
    controlCorretavilidad = fields.String(required=True)
    marcaLlenadoCheque = fields.String(required=True)
    formatoImpresionCuenta = fields.Integer(required=True)
    codigoPlaza = fields.Integer(required=True)
    numeroInicial = fields.Integer(required=True)
    numeroFinal = fields.Integer(required=True)
    proximoNumeroCheque = fields.Integer(required=True)
    estadoChequera = fields.Integer(required=True)
    fechaCambioEstado = fields.Date(required=True)
    usuario = fields.String(required=True)
    hora = fields.String(required=True)
    fechaProceso = fields.Date(required=True)

##################################
# ALTA DE REGISTROS
# REGISTRA DOSIFICACION DE CHEQUES
##################################
@app.route(modulo + programa + '/Registrar', methods=["POST"])
@auth_decorator()
@required_params(RegistrarDosificacionCheques())
def f1000_altas_ts304():
    resultado = {
        'mensaje': 'Guardado correctamente',
        'status': 200
    }
    
    #db = Database()
    funcion = 'f1000_altas_ts304'
    parametros = []
    operacion = "A"

    try:
        datos = request.json
        item = 1

        sql_insert = "insert into tsoca (tsocanoca, tsocadesc, tsocafreg, tsocacbco, tsocancta, tsocaccrl, tsocamlch, tsocafmto, tsocaplza, tsocanini, tsocanfin, tsocapnch, tsocastat, tsocafsta, tsocauser, tsocahora, tsocafpro) values('" + str(datos['numeroChequera']) + "', '" + str(datos['descripcion']) +  "', '" + str(datos['fechaRegistro']) + "', " + str(datos['numeroBanco']) + ", '" +  str(datos['numeroCuenta']) + "', '" + str(datos['controlCorretavilidad']) + "', '" +  str(datos['marcaLlenadoCheque']) + "', " +  str(datos['formatoImpresionCuenta']) + ", " +  str(datos['codigoPlaza']) +  ", " +  str(datos['numeroInicial']) + ", " +   str(datos['numeroFinal']) + ", " +  str(datos['proximoNumeroCheque'])  + ", " +   str(datos['estadoChequera']) + ", '"  + str(datos['fechaProceso']) + "', '" +  str(datos['usuario'])  + "', '" +   str(datos['hora'])  + "', '" +   str(datos['fechaProceso']) + "')"

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

        if(datos['numeroChequera'] is not None):  
            operacion = "M" 
        else:
            operacion = "A"

        
        
    except Exception as ex:
        db.ROLLBACK_WORK()
        resultado['status'] = 500
        resultado['mensaje'] = str(ex)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, str(ex))
    finally:
        db.desconectar()

    return json.dumps(resultado, cls=CustomJSONEncoder), resultado['status']



#########################################
# MODIFICACION DE DOSIFICACION DE CHEQUES
#########################################
class ModificarDosificacionCheques(BaseSchema):
    numeroChequera = fields.String(required=True)
    descripcion = fields.String(required=True)
    fechaRegistro = fields.Date(required=True)
    numeroBanco = fields.Integer(required=True)
    numeroCuenta = fields.String(required=True)
    controlCorretavilidad = fields.String(required=True)
    marcaLlenadoCheque = fields.String(required=True)
    formatoImpresionCuenta = fields.Integer(required=True)
    codigoPlaza = fields.Integer(required=True)
    numeroInicial = fields.Integer(required=True)
    numeroFinal = fields.Integer(required=True)
    proximoNumeroCheque = fields.Integer(required=True)
    estadoChequera = fields.Integer(required=True)
    fechaCambioEstado = fields.Date(required=True)
    usuario = fields.String(required=True)
    hora = fields.String(required=True)
    fechaProceso = fields.Date(required=True)


@app.route(modulo + programa + '/Modificar', methods=["PUT"])
@auth_decorator()
@required_params(ModificarDosificacionCheques())
def f2000_modificar_ts304():
    resultado = {
        'mensaje': 'Actualizado correctamente',
        'status': 200
    }
    
    #db = Database()
    funcion = 'f2000_modificar_ts304'
    parametros = []
    operacion = "M"

    try:
        datos = request.json
        item = 1

        sql_update = "update tsoca set tsocadesc = '" + str(datos['descripcion']) + "', tsocafreg = '" + str(datos['fechaRegistro']) +  "', tsocacbco = " + str(datos['numeroBanco']) + ", tsocancta = '" + str(datos['numeroCuenta']) + "', tsocaccrl = '" + str(datos['controlCorretavilidad']) + "', tsocamlch = '" + str(datos['marcaLlenadoCheque']) + "', tsocafmto = " + str(datos['formatoImpresionCuenta']) + ", tsocaplza = " + str(datos['codigoPlaza']) + ", tsocanini = " + str(datos['numeroInicial']) + ", tsocanfin = " + str(datos['numeroFinal']) + ", tsocapnch = " + str(datos['proximoNumeroCheque']) + ", tsocastat = " + str(datos['estadoChequera']) + ", tsocafsta = '" + str(datos['fechaCambioEstado']) + "', tsocauser = '" + str(datos['usuario']) + "', tsocahora = '" + str(datos['hora']) + "', tsocafpro = '" + str(datos['fechaProceso']) + "'  where tsocanoca = " + datos['numeroChequera']  + ""
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_update)

        db.conectar()
        db.BEGIN_WORK()
        rsp_update = db.actualizar(sql_update)
        
        if rsp_update == 0:
            mensaje = "No se encontro el registro solicitado, numeroChequera: " + datos['numeroChequera'] 
            
            resultado['status'] = 500
            resultado['mensaje'] = mensaje
        else:
            mensaje = "El registro " +  str(datos['numeroChequera'])  + " se actualizo correctamente"
            resultado['mensaje'] = mensaje
        
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_update)

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

        if(datos['numeroChequera'] is not None):  
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

class EliminarDosificacionCheques(BaseSchema):
    numeroChequera= fields.Integer(required=True)


##########################################
# BORRAR REGISTROS DOSIFICACION DE CHEQUES
##########################################
@app.route(modulo + programa + '/Eliminar', methods=["DELETE"])
@auth_decorator()
@required_params(EliminarDosificacionCheques())
def f3000_borrar_ts304():
    
    resultado = {
        'mensaje': 'Eliminado correctamente',
        'status': 200
    }
    
    #db = Database()
    funcion = 'f3000_borrar_ts304'
    parametros = []
    operacion = "E"

    try:
        datos = request.json
        item = 1
        
        sql_delete = "delete tsoca" +  " where tsocanoca = " + datos['numeroChequera']  + ""
        

        db.conectar()
        db.BEGIN_WORK()
        rsp_delete = db.eliminar(sql_delete)
    
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_delete)


        if rsp_delete == 0:
            mensaje = "No se encontro el registro solicitado, numeroChequera: " + datos['numeroChequera'] 
            print('f3000_borrar_ts304 mensaje: ', mensaje)
            resultado['status'] = 500
            resultado['mensaje'] = mensaje
        else:
            mensaje = "El registro " +  str(datos['numeroChequera'])  + " se elimino correctamente"
            resultado['mensaje'] = mensaje
        
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_delete)

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

        if(datos['numeroChequera'] is not None):  
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

@app.route(modulo + programa + '/Consultar', methods=["GET"])
@auth_decorator()
def f4000_consulta_ts304():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f4000_consulta_ts304'

    try:

        numeroChequera = None
        descripcion = None
        fechaRegistro = None
        numeroBanco = None
        numeroCuenta = None
        numeroInicial = None
        numeroFinal = None
        controlCorretavilidad = None
        marcaLlenadoCheque = None
        
        if 'numeroChequera' in  request.args: 
            numeroChequera =  request.args.get('numeroChequera')
            sql_tsoca = "select * from tsoca where tsocanoca = " + numeroChequera  +  " order by tsocanoca, tsocacbco, tsocancta"
        elif 'descripcion' in  request.args: 
            descripcion =  request.args.get('descripcion')
            sql_tsoca = "select * from tsoca where tsocadesc = " + descripcion  +  " order by tsocanoca, tsocacbco, tsocancta"
        elif 'fechaRegistro' in  request.args: 
            fechaRegistro =  request.args.get('fechaRegistro')
            sql_tsoca = "select * from tsoca where tsocafreg = " + fechaRegistro  +  " order by tsocanoca, tsocacbco, tsocancta"
        elif 'numeroBanco' in  request.args: 
            numeroBanco =  request.args.get('numeroBanco')
            sql_tsoca = "select * from tsoca where tsocacbco = " + numeroBanco  +  " order by tsocanoca, tsocacbco, tsocancta"
        elif 'numeroCuenta' in  request.args: 
            numeroCuenta =  request.args.get('numeroCuenta')
            sql_tsoca = "select * from tsoca where tsocancta = " + numeroCuenta  +  " order by tsocanoca, tsocacbco, tsocancta"
        elif 'numeroInicial' in  request.args: 
            numeroInicial =  request.args.get('numeroInicial')
            sql_tsoca = "select * from tsoca where tsocanini = " + numeroInicial  +  " order by tsocanoca, tsocacbco, tsocancta"
        elif 'numeroFinal' in  request.args: 
            numeroFinal =  request.args.get('numeroFinal')
            sql_tsoca = "select * from tsoca where tsocanfin = " + numeroFinal  +  " order by tsocanoca, tsocacbco, tsocancta"
        elif 'controlCorretavilidad' in  request.args: 
            controlCorretavilidad =  request.args.get('controlCorretavilidad')
            sql_tsoca = "select * from tsoca where tsocaccrl = " + controlCorretavilidad  +  " order by tsocanoca, tsocacbco, tsocancta"
        elif 'marcaLlenadoCheque' in  request.args: 
            marcaLlenadoCheque =  request.args.get('marcaLlenadoCheque')
            sql_tsoca = "select * from tsoca where tsocamlch = " + marcaLlenadoCheque  +  " order by tsocanoca, tsocacbco, tsocancta"
        else:
            sql_tsoca = "select * from tsoca order by tsocanoca, tsocacbco, tsocancta"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_tsoca)

        db.conectar()
        rsp_tsoca = db.query(sql_tsoca)
        array = []
        i = 0

        if rsp_tsoca is None:
            mensaje = 'No se encuentran registros'
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
        else:
            for item in rsp_tsoca:
                i_tsoca = collections.OrderedDict()
               
                array.append({
                    'numeroChequera' : str(item['tsocacbco']).strip(),
                    'descripcion' : str(item['tsocacbco']).strip(),
                    'fechaRegistro' : str(item['tsocacbco']).strip(),
                    'numeroBanco' : str(item['tsocacbco']).strip(),
                    'numeroCuenta' : str(item['tsocacbco']).strip(),
                    'controlCorretavilidad' : str(item['tsocacbco']).strip(),
                    'marcaLlenadoCheque' : str(item['tsocacbco']).strip(),
                    'formatoImpresionCuenta' : str(item['tsocacbco']).strip(),
                    'codigoPlaza' : str(item['tsocacbco']).strip(),
                    'numeroInicial' : str(item['tsocacbco']).strip(),
                    'numeroFinal' : str(item['tsocacbco']).strip(),
                    'proximoNumeroCheque' : str(item['tsocacbco']).strip(),
                    'estadoChequera' : str(item['tsocacbco']).strip(),
                    'fechaCambioEstado' : str(item['tsocacbco']).strip(),
                    'usuario' : str(item['tsocacbco']).strip(),
                    'hora' : str(item['tsocacbco']).strip(),
                    'fechaProceso' : str(item['tsocacbco']).strip()
                })

                result['cuentasTsoca'] = array
                result['total'] = len(array)
                result['mensaje'] = "Cargado Correctamente"

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_tsoca)
        
    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    
    return json.dumps(result, cls=CustomJSONEncoder), result['status']
