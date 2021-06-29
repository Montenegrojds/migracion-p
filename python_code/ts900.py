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
programa = "/RutinaBusquedas"
servicio = 'ts900'
funcion = 'main'
#############################################################    
#############################################################

@app.route(modulo + programa + '/Consultar', methods=["GET"])
@auth_decorator()
def f0200_selec_cursor_ts900():
    result = {
        'mensaje': 'Procesado correctamente',
        'status': 200
    }
    funcion = 'f0201_selec_cursor_ts900'

    try:

        flag = None
        parametro1 = None
        parametro2 = None
        
        if 'flag' in  request.args: 
            flag =  request.args.get('flag')
            logging.info('INFO : [%s] [%s] FLAG[%s]', servicio, funcion, flag)

            if flag == '1':
                #Cuentas Bancarias Habilitadas, parametro 1 : Numero de Banco
                parametro1 =  request.args.get('parametro1')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                if parametro1 is not None:
                    sql_select = "SELECT gbconabre, tsccbncta FROM tsccb JOIN gbcon ON tsccbcmon = gbconcorr WHERE tsccbcbco = " + str(parametro1) + " AND gbconpfij = 10 AND tsccbstat = 1 ORDER BY tsccbncta"
                else:
                    sql_select = "SELECT gbconabre, tsccbncta FROM tsccb JOIN gbcon ON tsccbcmon = gbconcorr WHERE gbconpfij = 10 AND tsccbstat = 1 ORDER BY tsccbncta"
            elif flag == '2': 
                # Conceptos, parametro 1 : Prefijo Conceptos
                parametro1 =  request.args.get('parametro1')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                if parametro1 is not None:
                    sql_select = "SELECT tsconcorr, tscondesc FROM tscon where tsconpref = " + str(parametro1) + " AND tsconcorr > 0 ORDER BY tsconcorr"
                else:
                    sql_select = "SELECT tsconcorr, tscondesc FROM tscon ORDER BY tsconcorr"
            elif flag == '3':
                # Titulos de Tipos de Movimiento
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                sql_select = "SELECT tsconcorr, tscondesc FROM tscon WHERE tsconpref = 10 AND tsconcorr BETWEEN 1 AND 2 ORDER BY tsconcorr"
            elif flag == '4':
                # Tipos de Movimiento, parametro 1 : Prefijo (Deb/Crd/Reg.Chq)
                parametro1 =  request.args.get('parametro1')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                if parametro1 is not None:
                    sql_select = "SELECT tstmvcorr, tstmvdesc FROM tstmv WHERE tstmvpref = " + str(parametro1) + " ORDER BY tstmvcorr"
                else:
                    sql_select = "SELECT tstmvcorr, tstmvdesc FROM tstmv ORDER BY tstmvcorr"
            elif flag == '5':
                # Conceptos Generales, parametro 1 : Prefijo Concepto
                parametro1 =  request.args.get('parametro1')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1) 
                if parametro1 is not None:
                    sql_select = "SELECT gbconcorr, gbcondesc FROM gbcon where gbconpfij = " + str(parametro1) + " AND gbconcorr > 0 ORDER BY gbconcorr"
                else:
                    sql_select = "SELECT gbconcorr, gbcondesc FROM gbcon ORDER BY gbconcorr"
            elif flag == '6':
                # Cheques Emitidos, parametro 1 : Prefijo Numero de Banco parametro 2 : Prefijo Numero de Cuenta 
                parametro1 =  request.args.get('parametro1')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                parametro2 =  request.args.get('parametro2')
                logging.info('INFO : [%s] [%s] PARAMETRO 2[%s]', servicio, funcion, parametro2)
                
                if parametro1 is not None and parametro2 is not None:
                    sql_select = "SELECT tschanchq, tschafech, tschaimpo, tschacmon FROM tscha where tschacbco = " + str(parametro1) + " AND tschancta = '" + str(parametro2) + "' AND tschatchq = 1 ORDER BY tschanchq"
                else:
                    sql_select = "SELECT tschanchq, tschafech, tschaimpo, tschacmon FROM tscha ORDER BY tschanchq"
            elif flag == '7': 
                # Cheques Recibidos, Parametro 1 : Prefijo Numero de Banco Parametro 2 : Prefijo Numero de Cuenta 
                parametro1 =  request.args.get('parametro1')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                parametro2 =  request.args.get('parametro2')
                logging.info('INFO : [%s] [%s] PARAMETRO 2[%s]', servicio, funcion, parametro2)
               
                if parametro1 is not None and parametro2 is not None:
                    sql_select = "SELECT tschanchq, tschafech, tschaimpo, tschacmon FROM tscha where tschacbco = " + str(parametro1) + " AND tschancta = '" + str(parametro2) + "' AND tschatchq = 2 ORDER BY tschanchq"
                else:
                    sql_select = "SELECT tschanchq, tschafech, tschaimpo, tschacmon FROM tscha ORDER BY tschanchq"
            elif flag == '8':
                # Agenda, Parametro 1 : Codigo de Agenda Nombre del Cliente
                parametro1 =  request.args.get('parametro1')
                parametro2 =  request.args.get('parametro2')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                logging.info('INFO : [%s] [%s] PARAMETRO 2[%s]', servicio, funcion, parametro2)
                
                if parametro1 is not None:
                    sql_select = "SELECT gbagecage, gbagenomb FROM gbage WHERE gbagecage = " + str(parametro1) + " ORDER BY gbagenomb"
                elif parametro2 is not None:
                    sql_select = "SELECT gbagecage, gbagenomb FROM gbage WHERE gbagenomb LIKE '%" + str(parametro2) + "%' ORDER BY gbagenomb"
                else:
                    sql_select = "SELECT gbagecage, gbagenomb FROM gbage ORDER BY gbagenomb"

            elif flag == '9':
                # Cuentas Bancarias (Habilitadas/Deshabilitadas), Parametro 1 Numero de Banco
                parametro1 =  request.args.get('parametro1')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                if parametro1 is not None:
                    sql_select = "SELECT tsccbcbco, tsccbncta, tsccbuneg FROM tsccb where tsccbcbco = " + str(parametro1) + " ORDER BY tsccbncta"
                else:
                    sql_select = "SELECT tsccbcbco, tsccbncta, tsccbuneg FROM tsccb ORDER BY tsccbncta"
            elif flag == '10':
                # Plan de cuentas (Nivel Analitico)
                parametro1 =  request.args.get('parametro1')
                parametro2 =  request.args.get('parametro2')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                logging.info('INFO : [%s] [%s] PARAMETRO 2[%s]', servicio, funcion, parametro2)
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                
                if parametro1 is not None:
                    sql_select = "SELECT cnplccnta, cnplcnomb FROM cnplc WHERE cnplccnta = '" + str(parametro1) + "' ORDER BY cnplccnta"
                elif parametro2 is not None:
                    sql_select = "SELECT cnplccnta, cnplcnomb FROM cnplc WHERE cnplcnomb LIKE '%" + str(parametro2) + "%' ORDER BY cnplccnta"
                else:
                    sql_select = "SELECT cnplccnta, cnplcnomb FROM cnplc ORDER BY cnplccnta"
            elif flag == '11':
                # Analisis Adicional 
                parametro1 =  request.args.get('parametro1')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                if parametro1 is not None:
                    sql_select = "SELECT cncnptcon, cncnpncon, cncnpdesc FROM cncnp WHERE cncnptcon = " + str(parametro1) + " ORDER BY cncnpncon"
                else:
                    sql_select = "SELECT cncnptcon, cncnpncon, cncnpdesc FROM cncnp ORDER BY cncnpncon"
            elif flag == '12': 
                # Tipos de documentos contables
                parametro1 =  request.args.get('parametro1')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                
                sql_select = "SELECT cntdctdoc, cntdcdesc FROM cntdc ORDER BY cntdctdoc"
            elif flag == '13':
                # Usuarios
                parametro1 =  request.args.get('parametro1')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                parametro2 =  request.args.get('parametro2')
                logging.info('INFO : [%s] [%s] PARAMETRO 2[%s]', servicio, funcion, parametro2)

                if parametro1 is not None:
                    sql_select = "SELECT adusrusrn, adusrnomb FROM adusr WHERE adusrusrn = '" + str(parametro1) + "' ORDER BY adusrusrn"
                elif parametro2 is not None:
                    sql_select = "SELECT adusrusrn, adusrnomb FROM adusr WHERE adusrnomb = '" + str(parametro2) + "' ORDER BY adusrusrn"
                else:
                    sql_select = "SELECT adusrusrn, adusrnomb FROM adusr ORDER BY adusrusrn"
            elif flag == '14':
                #Tipos Cuentas
                parametro1 =  request.args.get('parametro1')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                if parametro1 is not None:
                    sql_select = "SELECT cptcpclsc, cptcpctcp, cptcpdesc FROM cptcp where cptcpclsc = " + str(parametro1) + " ORDER BY cptcpctcp"
                else:
                    sql_select = "SELECT cptcpclsc, cptcpctcp, cptcpdesc FROM cptcp ORDER BY cptcpctcp"
            elif flag == '15':
                # Aplicaciones Cuentas
                parametro1 =  request.args.get('parametro1')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                if parametro1 is not None:
                    sql_select = "SELECT cpaplclsc, cpaplcapl, cpapldesc FROM cpapl where cpaplclsc = " + str(parametro1) + " ORDER BY cpaplcapl"
                else:
                    sql_select = "SELECT cpaplclsc, cpaplcapl, cpapldesc FROM cpapl ORDER BY cpaplcapl"
            elif flag == '16':
                # Formatos de llenado de cheques
                parametro1 =  request.args.get('parametro1')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                
                sql_select = "SELECT tsfcbfmto, tsfcbdesc FROM tsfcb ORDER BY tsfcbfmto" 
            elif flag == '20':
                # Cajas
                parametro1 =  request.args.get('parametro1')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                
                sql_select = "SELECT cjmcjncja, cjmcjdesc FROM cjmcj ORDER BY cjmcjncja"
            elif flag == '21':
                # Tipos de Documento (Impuestos)
                parametro1 =  request.args.get('parametro1')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                
                sql_select = "SELECT iptdctdoc, iptdcdesc FROM iptdc ORDER BY iptdctdoc"
            elif flag == '22': 
                # Centros de Costo
                parametro1 =  request.args.get('parametro1')
                parametro2 =  request.args.get('parametro2')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                logging.info('INFO : [%s] [%s] PARAMETRO 2[%s]', servicio, funcion, parametro2)
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                
                if parametro1 is not None:
                    sql_select = "SELECT cnccoccos, cnccodesc FROM cncco WHERE cnccoccos = '" + str(parametro1) + "' ORDER BY cnccoccos"
                elif parametro2 is not None:
                    sql_select = "SELECT cnccoccos, cnccodesc FROM cncco WHERE cnccodesc LIKE '%" + str(parametro2) + "%' ORDER BY cnccoccos"
                else:
                    sql_select = "SELECT cnccoccos, cnccodesc FROM cncco ORDER BY cnccoccos"
            elif flag == '23':
                # Unidad de Negocio
                parametro1 =  request.args.get('parametro1')
                parametro2 =  request.args.get('parametro2')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                logging.info('INFO : [%s] [%s] PARAMETRO 2[%s]', servicio, funcion, parametro2)

                if parametro1 is not None:
                    sql_select = "SELECT cnuneuneg, cnunedesc FROM cnune where cnuneuneg = " + str(parametro1) + " ORDER BY cnuneuneg"
                elif parametro2 is not None:
                    sql_select = "SELECT cnuneuneg, cnunedesc FROM cnune where cnunedesc LIKE '%" + str(parametro2) + "%' ORDER BY cnuneuneg"
                else:
                    sql_select = "SELECT cnuneuneg, cnunedesc FROM cnune ORDER BY cnuneuneg"
            elif flag == '24':
                # Convenios bancarios
                parametro1 =  request.args.get('parametro1')
                parametro2 =  request.args.get('parametro2')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                logging.info('INFO : [%s] [%s] PARAMETRO 2[%s]', servicio, funcion, parametro2)

                if parametro1 is not None:
                    sql_select = "SELECT gbcnvccnv, cncondesc FROM gbcnv JOIN cncon ON gbcnvcreg = cnconcorr WHERE gbcnvccnv = " + str(parametro1) + " AND cnconpref = 2 ORDER BY gbcnvccnv"
                elif parametro2 is not None:
                    sql_select = "SELECT gbcnvccnv, cncondesc FROM gbcnv JOIN cncon ON gbcnvcreg = cnconcorr WHERE cncondesc LIKE '%" + str(parametro2) + "%' AND cnconpref = 2 ORDER BY gbcnvccnv"
                else:
                    sql_select = "SELECT gbcnvccnv, cncondesc FROM gbcnv JOIN cncon ON gbcnvcreg = cnconcorr WHERE cnconpref = 2 ORDER BY gbcnvccnv"
            elif flag == '25':
                # Cuentas Bancarias Habilitadas por Regional
                parametro1 =  request.args.get('parametro1')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)

                if parametro1 is not None:
                    sql_select = "SELECT tsccbcbco, tsccbncta FROM tsccb where tsccbcbco = " + str(parametro1) + " AND tsccbstat = 1 AND tsccbuneg IN (SELECT cnuneuneg FROM cnune WHERE cnunecreg = " + str(parametro2) + ") ORDER BY tsccbncta"
                else:
                    sql_select = "SELECT tsccbcbco, tsccbncta FROM tsccb WHERE tsccbstat = 1 AND tsccbuneg IN (SELECT cnuneuneg FROM cnune) ORDER BY tsccbncta"
            elif flag == '26':
                # Regional
                parametro1 =  request.args.get('parametro1')
                parametro2 =  request.args.get('parametro2')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                logging.info('INFO : [%s] [%s] PARAMETRO 2[%s]', servicio, funcion, parametro2)

                if parametro1 is not None:
                    sql_select = "SELECT cnunecreg, cncondesc FROM cnune, cncon WHERE cnunecreg = " + str(parametro1) + " AND cnconpref = 2 AND cnconcorr > 0 ORDER BY cnunecreg"
                elif parametro2 is not None:
                    sql_select = "SELECT cnunecreg, cncondesc FROM cnune, cncon WHERE cncondesc LIKE '%" + str(parametro2) + "%' AND cnconpref = 2 AND cnconcorr > 0 ORDER BY cnunecreg"
                else:
                    sql_select = "SELECT cnunecreg, cncondesc FROM cnune, cncon WHERE cnconpref = 2 AND cnconcorr > 0 ORDER BY cnunecreg"
            elif flag == '27':
                # Financiador
                parametro1 =  request.args.get('parametro1')
                parametro2 =  request.args.get('parametro2')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                logging.info('INFO : [%s] [%s] PARAMETRO 2[%s]', servicio, funcion, parametro2)

                if parametro1 is not None:
                    sql_select = "SELECT epfincfin, gbagenomb FROM epfin JOIN gbage ON epfincfin = gbagecage WHERE epfincfin = " + str(parametro1) + " ORDER BY epfincfin"
                elif parametro2 is not None:
                    sql_select = "SELECT epfincfin, gbagenomb FROM epfin JOIN gbage ON epfincfin = gbagecage WHERE gbagenomb LIKE '" + str(parametro2) + "' ORDER BY epfincfin"
                else:
                    sql_select = "SELECT epfincfin, gbagenomb FROM epfin JOIN gbage ON epfincfin = gbagecage ORDER BY epfincfin"
            elif flag == '28': 
                # Proyectos
                parametro1 =  request.args.get('parametro1')
                parametro2 =  request.args.get('parametro2')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                logging.info('INFO : [%s] [%s] PARAMETRO 2[%s]', servicio, funcion, parametro2)

                if parametro1 is not None:
                    sql_select = "SELECT epprycpry, epprynomb FROM eppry where epprycpry = " + str(parametro1) + " ORDER BY epprycpry"
                elif parametro2 is not None:
                    sql_select = "SELECT epprycpry, epprynomb FROM eppry where epprynomb LIKE '%" + str(parametro2) + "%' ORDER BY epprycpry"
                else:
                    sql_select = "SELECT epprycpry, epprynomb FROM eppry ORDER BY epprycpry"
            elif flag == '29':
                # Programas
                parametro1 =  request.args.get('parametro1')
                parametro2 =  request.args.get('parametro2')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                logging.info('INFO : [%s] [%s] PARAMETRO 2[%s]', servicio, funcion, parametro2)

                if parametro1 is not None and parametro2 is not None:
                    sql_select = "SELECT epprgcprg, epprgdesc FROM epprg where epprgcpry = " + str(parametro1) + "AND epprgcprg = " + str(parametro2)  + " ORDER BY epprgcprg"
                elif parametro1 is not None and parametro3 is not None:
                    sql_select = "SELECT epprgcprg, epprgdesc FROM epprg where epprgcpry = " + str(parametro1) + "AND epprgdesc LIKE '%" + str(parametro3) +  "%' ORDER BY epprgcprg"
                else:
                    sql_select = "SELECT epprgcprg, epprgdesc FROM epprg ORDER BY epprgcprg"
            elif flag == '30':
                # Chequera
                parametro1 =  request.args.get('parametro1')
                parametro2 =  request.args.get('parametro2')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                logging.info('INFO : [%s] [%s] PARAMETRO 2[%s]', servicio, funcion, parametro2)

                if parametro1 is not None:
                    sql_select = "SELECT tsocanoca, tsocadesc FROM tsoca where tsocanoca = " + str(parametro1) + " AND tsocastat = 1 ORDER BY tsocanoca"
                elif parametro2 is not None:
                    sql_select = "SELECT tsocanoca, tsocadesc FROM tsoca where tsocadesc LIKE '%" + str(parametro2) + "%' AND tsocastat = 1 ORDER BY tsocanoca"
                else:
                    sql_select = "SELECT tsocanoca, tsocadesc FROM tsoca WHERE tsocastat = 1 ORDER BY tsocanoca"
            elif flag == '31':
                # Financiador
                parametro1 =  request.args.get('parametro1')
                parametro2 =  request.args.get('parametro2')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                logging.info('INFO : [%s] [%s] PARAMETRO 2[%s]', servicio, funcion, parametro2)

                if parametro1 is not None:
                    sql_select = "SELECT epfincfin, gbagenomb FROM epfin JOIN gbage ON epfincfin = gbagecage WHERE epfincfin = " + str(parametro1) + ""
                elif parametro2 is not None:
                    sql_select = "SELECT epfincfin, gbagenomb FROM epfin JOIN gbage ON epfincfin = gbagenomb WHERE gbagenomb LIKE '%" + str(parametro2) + "%'"
                else:
                    sql_select = "SELECT epfincfin, gbagenomb FROM epfin JOIN gbage ON epfincfin = gbagecage"
            '''elif flag == '32':
                # Bancos
                parametro1 =  request.args.get('parametro1')
                parametro2 =  request.args.get('parametro2')
                logging.info('INFO : [%s] [%s] PARAMETRO 1[%s]', servicio, funcion, parametro1)
                logging.info('INFO : [%s] [%s] PARAMETRO 2[%s]', servicio, funcion, parametro2)

                if parametro1 is not None:
                    sql_select = "SELECT tsbcocbco, tsbconomb FROM tsbco where tsbcocbco = " + str(parametro1) + " ORDER BY tsbcocbco"
                elif parametro2 is not None:
                    sql_select = "SELECT tsbcocbco, tsbconomb FROM tsbco where tsbconomb LIKE '%" + str(parametro2) + "%' ORDER BY tsbcocbco"
                else:
                    sql_select = "SELECT tsbcocbco, tsbconomb FROM tsbco ORDER BY tsbcocbco"'''

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, sql_select)
        print(sql_select)

        db.conectar()
        rsp_select = db.query(sql_select)
        array = []
        i = 0

        logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, rsp_select)

        if rsp_select is None:
            mensaje = 'No se encuentran registros'
            result['mensaje'] = mensaje
            result['total'] = 0
            logging.info('INFO : [%s] [%s] [%s]', servicio, funcion, mensaje)
        else:
            for item in rsp_select:
                if flag == '1':
                    array.append({
                        'abreviacion' : str(item['gbconabre']).strip(),
                        'numeroCuenta' : str(item['tsccbncta']).strip()
                    })
                elif flag == '2':
                    array.append({
                        'correlativo' : str(item['tsconcorr']).strip(),
                        'descripcion' : str(item['tscondesc']).strip()
                    })
                elif flag == '3':
                    array.append({
                        'abreviacion' : str(item['tsconcorr']).strip(),
                        'numeroCuenta' : str(item['tscondesc']).strip()
                    })
                elif flag == '4':
                    array.append({
                        'correlativo' : str(item['tstmvcorr']).strip(),
                        'descripcion' : str(item['tstmvdesc']).strip()
                    })
                elif flag == '5':
                    array.append({
                        'correlativoConcepto' : str(item['gbconcorr']).strip(),
                        'descripcionConcepto' : str(item['gbcondesc']).strip()
                    })
                elif flag == '6':
                    array.append({
                        'numeroCheque' : str(item['tschanchq']).strip(),
                        'fechaEmision' : str(item['tschafech']).strip(),
                        'importe' : str(item['tschaimpo']).strip(),
                        'moneda' : str(item['tschacmon']).strip()
                    })
                elif flag == '7':
                    array.append({
                        'abreviacion' : str(item['tschanchq']).strip(),
                        'fechaEmision' : str(item['tschafech']).strip(),
                        'importe' : str(item['tschaimpo']).strip(),
                        'moneda' : str(item['tschacmon']).strip()
                    })
                elif flag == '8':
                    array.append({
                        'codigoAgenta' : str(item['gbagecage']).strip(),
                        'nombreRazonSocial' : str(item['gbagenomb']).strip()
                    })
                elif flag == '9':
                    array.append({
                        'numeroBanco' : str(item['tsccbcbco']).strip(),
                        'numeroCuenta' : str(item['tsccbncta']).strip(),
                        'unidadNegocio' : str(item['tsccbuneg']).strip()
                    })
                elif flag == '10':
                    array.append({
                        'codigoCuenta' : str(item['cnplccnta']).strip(),
                        'nombreCuenta' : str(item['cnplcnomb']).strip()
                    })
                elif flag == '11':
                    array.append({
                        'tipoAnalisis' : str(item['cncnptcon']).strip(),
                        'numeroAnalisis' : str(item['cncnpncon']).strip(),
                        'descripcion' : str(item['cncnpdesc']).strip()
                    })
                elif flag == '12':
                    array.append({
                        'tipoDocumentoContable' : str(item['cntdctdoc']).strip(),
                        'descripcion' : str(item['cntdcdesc']).strip()
                    })
                elif flag == '13':
                    array.append({
                        'codigoUsuario' : str(item['adusrusrn']).strip(),
                        'nombreUsuario' : str(item['adusrnomb']).strip()
                    })
                elif flag == '14':
                    array.append({
                        'claseCuenta' : str(item['cptcpclsc']).strip(),
                        'codigoTipoCuenta' : str(item['cptcpctcp']).strip(),
                        'descripcion' : str(item['cptcpdesc']).strip()
                    })
                elif flag == '15':
                    array.append({
                        'claseCuenta' : str(item['cpaplclsc']).strip(),
                        'codigoAplicacion' : str(item['cpaplcapl']).strip(),
                        'descripcion' : str(item['cpapldesc']).strip()
                    })
                elif flag == '16':
                    array.append({
                        'codigoFormato' : str(item['tsfcbfmto']).strip(),
                        'descripcion' : str(item['tsfcbdesc']).strip()
                    })
                elif flag == '20':
                    array.append({
                        'numeroCaja' : str(item['cjmcjncja']).strip(),
                        'descripcion' : str(item['cjmcjdesc']).strip()
                    })
                elif flag == '21':
                    array.append({
                        'tipoDocumento' : str(item['iptdctdoc']).strip(),
                        'descripcion' : str(item['iptdcdesc']).strip()
                    })
                elif flag == '22':
                    array.append({
                        'centroCosto' : str(item['cnccoccos']).strip(),
                        'descripcion' : str(item['cnccodesc']).strip()
                    })
                elif flag == '23':
                    array.append({
                        'unidadNegocio' : str(item['cnuneuneg']).strip(),
                        'descripcion' : str(item['cnunedesc']).strip()
                    })
                elif flag == '24':
                    array.append({
                        'cuentaConvenio' : str(item['gbcnvccnv']).strip(),
                        'descripcion' : str(item['cncondesc']).strip()
                    })
                elif flag == '25':
                    array.append({
                        'numeroBanco' : str(item['tsccbcbco']).strip(),
                        'numeroCuenta' : str(item['tsccbncta']).strip()
                    })
                elif flag == '26':
                    array.append({
                        'codigoRegional' : str(item['cnunecreg']).strip(),
                        'descripcion' : str(item['cncondesc']).strip()
                    })
                elif flag == '27':
                    array.append({
                        'financiadorEnAgenda' : str(item['epfincfin']).strip(),
                        'nombreRazonSocial' : str(item['gbagenomb']).strip()
                    })
                elif flag == '28':
                    array.append({
                        'codigoProyecto' : str(item['epprycpry']).strip(),
                        'nombreProyecto' : str(item['epprynomb']).strip()
                    })
                elif flag == '29':
                    array.append({
                        'abreviacion' : str(item['gbconabre']).strip(),
                        'numeroCuenta' : str(item['tsccbncta']).strip()
                    })
                elif flag == '30':
                    array.append({
                        'numeroChequera' : str(item['tsocanoca']).strip(),
                        'descripcion' : str(item['tsocadesc']).strip()
                    })
                elif flag == '31':
                    array.append({
                        'financiadorEnAgenda' : str(item['epfincfin']).strip(),
                        'nombreRazonSocial' : str(item['gbagenomb']).strip()
                    })
                elif flag == '32':
                    array.append({
                        'abreviacion' : str(item['gbconabre']).strip(),
                        'numeroCuenta' : str(item['tsccbncta']).strip()
                    })
                
        result['total'] = len(array)

        if len(array) == 0:
            result['mensaje'] = "No se encontraron registros"
        else:
            result['mensaje'] = "Cargado Correctamente"
            result['data'] = array
            logging.info('INFO : [%s] [%s] DATA[%s]', servicio, funcion, result['data'])

    except Exception as ex:
        result['status'] = 500
        result['mensaje'] = str(ex)
        print(result['mensaje'])
    finally:
        db.desconectar()
    
    return json.dumps(result, cls=CustomJSONEncoder), result['status']


#############################################################

