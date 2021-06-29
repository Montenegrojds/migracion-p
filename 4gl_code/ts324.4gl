###############################################################################
# PROGRAMA: ts324.4gl
# VERSION : 5.1.0
# FECHA   : 01/04/98,03/07/98,25/03/99
# OBJETIVO: Rechazo de Cheque
# AUTOR   : MDR,CCS
# COMPILAR: ts324.4gl ts000.4gl ts900.4gl ad800.4gl 
#                     gb000.4gl gb001.4gl gb002.4gl
###############################################################################
DATABASE tbsai
	GLOBALS "gbglobs.4gl"
        DEFINE  t1       RECORD LIKE tstdc.*,
		t2       RECORD LIKE tstdr.*,
                t3       RECORD LIKE tsccb.*,
                t4       RECORD LIKE cnprm.*,
                t9       RECORD LIKE tsctl.*,
		g_ichq          LIKE tscha.tschaimpo,
		g_stat          LIKE tscha.tschastat,
		g_bank          LIKE gbcon.gbcondesc,
		g_bcoc          LIKE gbcon.gbcondesc,
		g_monc          LIKE gbcon.gbconabre,
		g_mont          LIKE gbcon.gbconabre,
                g_item          LIKE cntcn.cntcnitem,
	       	g_cctb          LIKE cntcn.cntcncctb,
		g_adic          LIKE cntcn.cntcnscaa,
                g_glosa         LIKE cntcn.cntcndesc,
		g_uneg		LIKE cnune.cnuneuneg, #U/N del cheque
		g_tdst		INTEGER,
		g_uncc		SMALLINT,
		g_cpry          LIKE tscba.tscbacpry,
		g_cprg          LIKE tscba.tscbacprg,
		g_cfin          LIKE tscba.tscbacfin,
		cntr		SMALLINT,
                #################################
                # variables generales NO BORRAR #
                #################################
                t0            RECORD LIKE gbpmt.*,
                t01           RECORD LIKE gbpmt.*,
		t02	      RECORD LIKE gbrne.*,
	       #---------------------------------#
	        g_nmod               CHAR(16),
	        g_titu               CHAR(33),
		g_vers	             CHAR(6),
                g_uaut               CHAR(3),
	       #---------------------------------#
                i                    SMALLINT,
                g_flag               SMALLINT,
                g_marca              SMALLINT,
                g_fact               CHAR(1),
                g_user               CHAR(3),
                g_nive               SMALLINT,
                g_mgui               CHAR(1),
                g_hora               CHAR(8),
                g_fpro               DATE,
                #g_msj                CHAR(79),
                g_freg               LIKE tstdc.tstdcftra,
		g_spool		     CHAR(20)

MAIN DEFER INTERRUPT IF NOT f0000_open_database_gb000() THEN EXIT PROGRAM END IF
        OPTIONS PROMPT LINE 23,
          --* ON CLOSE APPLICATION CONTINUE,
		ERROR  LINE 24
        SET LOCK MODE TO WAIT
	LET g_mtflag = 0
        #WHENEVER ERROR CONTINUE
        OPEN FORM ts324_01 FROM "ts324a"
        DISPLAY FORM ts324_01
        LET g_freg = "01/01/1900"
	LET g_fpro = TODAY
        LET g_user = arg_val(1)
        LET g_mgui = arg_val(2)
--*     LET g_mgui = "N"        
        LET g_nive = arg_val(3)
        CALL f6050_buscar_empresa_ts324()
       #-----------------------------------------------------------------------
	LET g_nmod = "TESORERIA"
	LET g_titu = "RECHAZO DE CHEQUES"
	LET g_vers = "5.1.10"
--*	LET g_vers = "6.0.1"
	CALL f6100_cabecera_gb000(t0.gbpmtnomb,g_nmod,g_titu,t0.gbpmtfdia,
				  g_vers)
       #-----------------------------------------------------------------------
	IF NOT f0300_usuario_gb000(g_user) THEN
	    CALL qx031_msgadvertencia_gb000(" No tiene Autorizacion",2)
	    EXIT PROGRAM
        END IF
	IF NOT f1000_clave_gb000(t0.gbpmtnomb,t0.gbpmtcusr,96) THEN
	    CALL qx031_msgadvertencia_gb000(" Acceso Denegado, llame a su proveedor de Software",2)
	    EXIT PROGRAM
	END IF
        CALL f7000_crear_temporal_ad800()
        CALL f0250_declarar_puntero_ts324()
        CALL f0300_proceso_ts324()
END MAIN

#########################
# DECLARACION DE PUNTEROS
#########################

FUNCTION f0250_declarar_puntero_ts324()
        DECLARE q_adtmp CURSOR FOR
                SELECT * FROM adtmp
                        ORDER BY item
END FUNCTION

#################
# PROCESO CENTRAL
#################

FUNCTION f0300_proceso_ts324()
        DEFINE	l_ndoc  LIKE tstdc.tstdcndoc,
	      	l_desc  CHAR(7),
	      	l_cdin  CHAR(40),
	      	l_exit  SMALLINT,
                l_freg  LIKE cpmcp.cpmcpfreg,
                l_tcof  LIKE gbhtc.gbhtctcof,
                l_tcco  LIKE gbhtc.gbhtctcco,
                l_tcve  LIKE gbhtc.gbhtctcve

	WHILE TRUE
        CALL f6000_limpiar_menu_ts324()
        IF g_freg = "01/01/1900" THEN
           LET g_freg = t0.gbpmtfdia
        END IF
        INPUT BY NAME t1.tstdcntra WITHOUT DEFAULTS
		ON KEY (CONTROL-C,INTERRUPT)
                        LET int_flag = TRUE
			EXIT INPUT
                ON KEY (CONTROL-B)
                        CALL f4000_consulta_ts324()
                        IF t1.tstdcntra IS NOT NULL THEN
                            EXIT INPUT
                        END IF
	END INPUT
	IF int_flag THEN
	    RETURN
	END IF
        CALL f5000_buscar_registro_ts324()
        INPUT BY NAME t1.tstdcndoc,t1.tstdcfdoc,t1.tstdccbco,t1.tstdcncta,
                      t2.tstdrcbco,t2.tstdrncta,t2.tstdrnchq,t2.tstdrimpt,
                      t1.tstdctcam,t1.tstdcgls1,t1.tstdcgls2,t1.tstdcgls3
                WITHOUT DEFAULTS
		ON KEY (CONTROL-C,INTERRUPT)
		        LET int_flag = TRUE 
			EXIT INPUT
                ON KEY (F1,CONTROL-P)
                        CALL f4000_accesos_rapidos_ad800(g_user,8,2,g_nive)
		ON KEY (CONTROL-E)
                        IF g_marca THEN
	                    IF t0.gbpmtfdia >= t1.tstdcfdoc THEN
				IF g_uncc THEN
				    LET l_cdin = NULL
                                    IF NOT f0330_validar_ts324() THEN
				        CALL qx030_msgadvetencia_gb000(g_msj)
			                LET int_flag = TRUE
		                        EXIT INPUT
                                    END IF
			            CALL f0400_autorizacion_ad800
				         (g_user,96,2,t1.tstdcimpt,t1.tstdccmon,
					  l_cdin,16,1,t1.tstdcftra)
			    	              RETURNING g_uaut,g_flag
			            IF g_flag THEN
                                        IF f3000_borrar_ts324() THEN
			                    LET int_flag = TRUE
		                            EXIT INPUT
			                END IF
			            END IF
				END IF
			    ELSE
				LET g_msj = "No puede revertir por incompati",
                                            "bilidad de fechas"
				CALL qx030_msgadvetencia_gb000(g_msj)

	                    END IF
                        END IF
		ON KEY (CONTROL-V)
                        IF INFIELD(tstdccbco) THEN
			    CALL f0200_selec_cursor_ts900(5,11,0)
			              RETURNING t1.tstdccbco,g_bank
                            DISPLAY BY NAME t1.tstdccbco,g_bank
     		            NEXT FIELD tstdccbco
                        END IF
                        IF INFIELD(tstdcncta) THEN
			    CALL f0200_selec_cursor_ts900(1,t1.tstdccbco,0)
			              RETURNING l_desc,t1.tstdcncta
			    DISPLAY BY NAME t1.tstdcncta
     		            NEXT FIELD tstdcncta
                        END IF
                        IF INFIELD(tstdrcbco) THEN
			    CALL f0200_selec_cursor_ts900(5,11,0)
			              RETURNING t2.tstdrcbco,g_bcoc
                            DISPLAY BY NAME t2.tstdrcbco,g_bcoc
     		            NEXT FIELD tstdrcbco
                        END IF
                BEFORE INPUT
                        LET l_ndoc = t1.tstdcndoc
			LET l_exit = FALSE
			IF g_marca THEN
                            #------------ Validar Unidad de Negocio -----------#
                            LET g_uncc = TRUE
                            IF NOT f5050_buscar_adhuu_ts324(t1.tstdcuneg) THEN
                                LET g_msj = "Usuario no habilitado en la U/N ",
                                      t1.tstdcuneg USING "<<<<"
                                CALL qx030_msgadvetencia_gb000(g_msj)      
                                LET g_uncc = FALSE
                            END IF
                            IF NOT f5050_buscar_adhuu_ts324(g_uneg) THEN
                                LET g_msj = "Usuario no habilitado en la U/N ",
                                      g_uneg USING "<<<<"
                                CALL qx030_msgadvetencia_gb000(g_msj)      
                                LET g_uncc = FALSE
                            END IF
			   #----------- Validar Cierre contable ------------#
                           IF t4.cnprmfdes IS NOT NULL THEN
                               IF t1.tstdcfdoc <= t4.cnprmfdes THEN
				    LET g_msj = "Periodo contable cerrado...",
                                                " No puede modificar"
                                    CALL qx030_msgadvetencia_gb000(g_msj)
                               	    LET l_exit = TRUE
                               END IF
			   END IF
			   #------------------------------------------------#
                           LET t0.gbpmtfdia = t1.tstdcfdoc
                           CALL f5010_buscar_gbhtc_ts324(t1.tstdcfdoc)
                                     RETURNING g_flag,l_tcof,l_tcco,l_tcve
                           IF NOT g_flag THEN
                               NEXT FIELD tstdcfdoc
                           END IF
                           LET t0.gbpmttcof = l_tcof
                           LET t0.gbpmttcco = l_tcco
                           LET t0.gbpmttcve = l_tcve
                       ELSE
                           LET t1.tstdcfdoc = g_freg
                           LET t0.gbpmtfdia = g_freg
                           DISPLAY BY NAME t1.tstdcfdoc
			END IF
                AFTER FIELD tstdcndoc
			IF l_exit THEN 
			    LET int_flag = TRUE
			    EXIT INPUT
			END IF 
                        IF g_marca THEN
                            LET t1.tstdcndoc = l_ndoc
                            LET int_flag = FALSE
                            EXIT INPUT
                        END IF
                BEFORE FIELD tstdcfdoc
			IF t1.tstdcfdoc IS NULL THEN
			    LET t1.tstdcfdoc = t0.gbpmtfdia
			END IF
                AFTER FIELD tstdcfdoc
                        IF t1.tstdcfdoc IS NOT NULL THEN
                           LET t1.tstdcfdoc = f0310_fecha_gb000(t1.tstdcfdoc)
			   DISPLAY BY NAME t1.tstdcfdoc
			   IF t1.tstdcfdoc < t0.gbpmtfini THEN
				    LET g_msj = "Valor no permitido"
					CALL qx030_msgadvetencia_gb000(g_msj)
			       NEXT FIELD tstdcfdoc
			   END IF
                           IF t1.tstdcfdoc > t01.gbpmtfdia THEN
                              LET g_msj = "La Fecha no puede ser Mayor ",
                                    "a la Fecha del Sistema"
                              CALL qx030_msgadvetencia_gb000(g_msj)      
                              NEXT FIELD tstdcfdoc
                           END IF
			   #----------- Validar Cierre contable ------------#
                           IF t4.cnprmfdes IS NOT NULL THEN
                               IF t1.tstdcfdoc <= t4.cnprmfdes THEN
				   LET g_msj = "Periodo contable cerrado"
				   CALL qx030_msgadvetencia_gb000(g_msj)
                                   LET t1.tstdcfdoc = l_freg
                                   NEXT FIELD tstdcfdoc
			       END IF
			   END IF
			   #------------------------------------------------#
                           IF t1.tstdcfdoc <> t01.gbpmtfdia THEN
                              IF t1.tstdcfdoc <> l_freg THEN
                                  LET l_cdin = "Fecha del Sistema: ",
                                                t01.gbpmtfdia," -- ",
                                               "Fecha Modificada: ",
                                                t1.tstdcfdoc
                                  CALL f0400_autorizacion_ad800
                                            (g_user,12,13,0,0,l_cdin,
                                             16,1,t1.tstdcfdoc)
                                          RETURNING g_uaut,g_flag
                                  IF NOT g_flag THEN
                                      LET g_msj = "Necesita Autorizacion para ",
                                            "Modificar Fecha"
                                      CALL qx030_msgadvetencia_gb000(g_msj)      
                                      LET t1.tstdcfdoc = l_freg
                                      NEXT FIELD tstdcfdoc
                                  END IF
                              END IF
                              LET t0.gbpmtfdia = t1.tstdcfdoc
                              CALL f5010_buscar_gbhtc_ts324(t1.tstdcfdoc)
                                        RETURNING g_flag,l_tcof,l_tcco,l_tcve
                              IF NOT g_flag THEN
                                  LET t1.tstdcfdoc = l_freg
                                  NEXT FIELD tstdcfdoc
                              END IF
                              LET t0.gbpmttcof = l_tcof
                              LET t0.gbpmttcco = l_tcco
                              LET t0.gbpmttcve = l_tcve
                           ELSE
                              LET t0.* = t01.*
                           END IF
                        ELSE
                           LET t1.tstdcfdoc = t01.gbpmtfdia
                           LET t0.* = t01.*
                        END IF
                        LET g_freg = t1.tstdcfdoc
                        DISPLAY BY NAME t1.tstdcfdoc
                AFTER FIELD tstdccbco 
                        IF t1.tstdccbco IS NULL THEN
                            NEXT FIELD tstdccbco
                        END IF
			CALL f5010_buscar_gbcon_ts324(11,t1.tstdccbco,1)
				  RETURNING g_bank,g_flag
			IF NOT g_flag THEN
			    LET g_msj = "No existe"
				CALL qx030_msgadvetencia_gb000(g_msj)
			    NEXT FIELD tstdccbco
			END IF
			DISPLAY BY NAME g_bank
                AFTER FIELD tstdcncta
                        IF t1.tstdcncta IS NULL THEN
                            NEXT FIELD tstdcncta
                        END IF
			IF NOT f5020_buscar_tsccb_ts324() THEN
			    NEXT FIELD tstdcncta
			END IF
                        IF NOT f5050_buscar_adhuu_ts324(t3.tsccbuneg) THEN
                            LET g_msj = "Usuario no habilitado en la U/N ",
                                  t3.tsccbuneg USING "<<<<"
                            CALL qx030_msgadvetencia_gb000(g_msj)      
                            NEXT FIELD tstdcncta
                        END IF
	                CALL f5010_buscar_gbcon_ts324(10,t3.tsccbcmon,0)
			          RETURNING g_mont,g_flag
	                DISPLAY BY NAME g_mont
                AFTER FIELD tstdrcbco
                        IF t2.tstdrcbco IS NULL THEN
                            NEXT FIELD tstdrcbco
                        END IF
			CALL f5010_buscar_gbcon_ts324(11,t2.tstdrcbco,1)
				  RETURNING g_bcoc,g_flag
			IF NOT g_flag THEN
			    LET g_msj = "No existe"
				CALL qx030_msgadvetencia_gb000(g_msj)
			    NEXT FIELD tstdrcbco
			END IF
			DISPLAY BY NAME g_bcoc
                AFTER FIELD tstdrncta
                        IF t2.tstdrncta IS NULL THEN
                            NEXT FIELD tstdrncta
                        END IF
                AFTER FIELD tstdrnchq
                        IF t2.tstdrnchq IS NULL THEN
                            NEXT FIELD tstdrnchq
                        END IF
                        IF NOT f5030_buscar_tscha_ts324() THEN
						    LET g_msj = "No existe"
							CALL qx030_msgadvetencia_gb000(g_msj)
                            NEXT FIELD tstdrnchq
                        END IF
			LET g_flag = TRUE
			CASE g_stat
			      WHEN 1 
						    LET g_msj = "Cheque sin depositar"
							CALL qx030_msgadvetencia_gb000(g_msj)
			      WHEN 2 
						    LET g_msj = "Cheque ya esta rechazado"
							CALL qx030_msgadvetencia_gb000(g_msj)
			      WHEN 3 LET g_flag = FALSE
			      WHEN 4 
						    LET g_msj = "Cheque dado de baja"
							CALL qx030_msgadvetencia_gb000(g_msj)
			      WHEN 5 
						    LET g_msj = "Cheque anulado"
							CALL qx030_msgadvetencia_gb000(g_msj)
			      WHEN 6 
						    LET g_msj = "Cheque cambiado"
							CALL qx030_msgadvetencia_gb000(g_msj)
			END CASE
			IF g_flag THEN
                            NEXT FIELD tstdrnchq
			END IF
			#------------------------------------------------------#
			SELECT COUNT(*) INTO cntr
				FROM tscch
			       WHERE tscchcbco = t2.tstdrcbco
				 AND tscchncta = t2.tstdrncta
				 AND tscchnchq = t2.tstdrnchq
				 AND tscchmrcb = 0
			IF cntr > 0 THEN
			    LET g_msj = "Cheque ya fue certificado"
				CALL qx030_msgadvetencia_gb000(g_msj)
			    NEXT FIELD tstdrnchq
			END IF
			#------------------------------------------------------#
                        IF NOT f5050_buscar_adhuu_ts324(g_uneg) THEN
                            LET g_msj = "Usuario no habilitado en la U/N ",
                                  g_uneg USING "<<<<"
                            CALL qx030_msgadvetencia_gb000(g_msj)      
                            NEXT FIELD tstdrnchq
                        END IF
	                CALL f5010_buscar_gbcon_ts324(10,t2.tstdrcmon,0)
			          RETURNING g_monc,g_flag
	                DISPLAY BY NAME g_monc
			IF NOT f5040_buscar_tsdep_ts324() THEN
                            NEXT FIELD tstdcncta
			END IF
                AFTER FIELD tstdrimpt
			IF t2.tstdrimpt IS NULL OR t2.tstdrimpt <= 0 THEN
			    NEXT FIELD tstdrimpt
			END IF
			IF t2.tstdrimpt <> g_ichq THEN
			    LET g_msj = "No coincide con el importe del Cheque... ",
				  "Verificar!"
				CALL qx030_msgadvetencia_gb000(g_msj)  
			    NEXT FIELD tstdrimpt
			END IF
                BEFORE FIELD tstdctcam
			IF t1.tstdctcam IS NULL AND t2.tstdrcmon = t3.tsccbcmon
		        THEN
			    LET t1.tstdctcam = t0.gbpmttcof
			    LET t1.tstdcimpo = t2.tstdrimpt
			    DISPLAY BY NAME t1.tstdcimpo
			END IF
                AFTER FIELD tstdctcam
                        IF t1.tstdctcam IS NULL OR t1.tstdctcam <= 0 THEN
                            NEXT FIELD tstdctcam
                        END IF
			CALL f0310_importe_debito_ts324()
			DISPLAY BY NAME t1.tstdcimpo
                AFTER INPUT
			IF t1.tstdcfdoc IS NULL THEN
			    NEXT FIELD tstdcfdoc
			END IF
                        IF t1.tstdccbco IS NULL THEN
                            NEXT FIELD tstdccbco
                        END IF
                        IF t1.tstdcncta IS NULL THEN
                            NEXT FIELD tstdcncta
                        END IF
			IF NOT f5020_buscar_tsccb_ts324() THEN
			    NEXT FIELD tstdcncta
			END IF
                        IF t2.tstdrcbco IS NULL THEN
                            NEXT FIELD tstdrcbco
                        END IF
                        IF t2.tstdrncta IS NULL THEN
                            NEXT FIELD tstdrncta
                        END IF
                        IF t2.tstdrnchq IS NULL THEN
                            NEXT FIELD tstdrnchq
                        END IF
                        IF NOT f5030_buscar_tscha_ts324() THEN
						    LET g_msj = "No existe"
							CALL qx030_msgadvetencia_gb000(g_msj)
                            NEXT FIELD tstdrnchq
                        END IF
			LET g_flag = TRUE
			
			CASE g_stat
			      WHEN 1 
						    LET g_msj = "Cheque sin depositar"
							CALL qx030_msgadvetencia_gb000(g_msj)
			      WHEN 2 
						    LET g_msj = "Cheque ya esta rechazado"
							CALL qx030_msgadvetencia_gb000(g_msj)
			      WHEN 3 LET g_flag = FALSE
			      WHEN 4 
						    LET g_msj = "Cheque dado de baja"
							CALL qx030_msgadvetencia_gb000(g_msj)
			      WHEN 5 
						    LET g_msj = "Cheque anulado"
							CALL qx030_msgadvetencia_gb000(g_msj)
			      WHEN 6 
						    LET g_msj = "Cheque cambiado"
							CALL qx030_msgadvetencia_gb000(g_msj)
			END CASE
			IF g_flag THEN
			    NEXT FIELD nchq
			END IF
			#------------------------------------------------------#
			SELECT COUNT(*) INTO cntr
				FROM tscch
			       WHERE tscchcbco = t2.tstdrcbco
				 AND tscchncta = t2.tstdrncta
				 AND tscchnchq = t2.tstdrnchq
				 AND tscchmrcb = 0
			IF cntr > 0 THEN
			    LET g_msj = "Cheque ya fue certificado"
				CALL qx030_msgadvetencia_gb000(g_msj)
			    NEXT FIELD tstdrnchq
			END IF
			#------------------------------------------------------#
			IF NOT f5040_buscar_tsdep_ts324() THEN
                            NEXT FIELD tstdcncta
                        END IF
			IF t2.tstdrimpt IS NULL THEN
			    NEXT FIELD tstdrimpt
			END IF
			IF t2.tstdrimpt <> g_ichq THEN
			     LET g_msj = "No coincide con el importe del Cheque... ",
				  "Verificar!"
					CALL qx030_msgadvetencia_gb000(g_msj)
			    NEXT FIELD tstdrimpt
			END IF
			CALL f0310_importe_debito_ts324()
                        IF t1.tstdctcam IS NULL THEN
                            NEXT FIELD tstdctcam
                        END IF
                        #------------------------------------------------------#
			IF NOT f5100_disponible_ts000
			           (t1.tstdccbco,t1.tstdcncta,t1.tstdcimpo) THEN
			        NEXT FIELD tstdcncta
			END IF
                        #------------------------------------------------------#
	END INPUT
	IF int_flag THEN
	    LET int_flag = FALSE
            CONTINUE WHILE
        END IF
	IF g_marca = FALSE THEN
            IF f1000_altas_ts324() THEN
                CALL f8000_imprimir_comprobante_ts324()
            END IF
        ELSE
            CALL f8000_imprimir_comprobante_ts324()
	END IF
	END WHILE
END FUNCTION

FUNCTION f0310_importe_debito_ts324()
	LET t1.tstdcimpo = t2.tstdrimpt
	IF t2.tstdrcmon = 1 AND t3.tsccbcmon = 2 THEN
    	    LET t1.tstdcimpo = f0100_redondeo_gb000(t1.tstdcimpo/t1.tstdctcam,2)
	END IF
	IF t2.tstdrcmon = 2 AND t3.tsccbcmon = 1 THEN
    	    LET t1.tstdcimpo = f0100_redondeo_gb000(t1.tstdcimpo*t1.tstdctcam,2)
	END IF
END FUNCTION

###################
# ALTA DE REGISTROS
###################

###########################
# MODIFICACION DE REGISTROS
###########################

##################
# BORRAR REGISTROS
##################

FUNCTION f0330_validar_ts324()
	DEFINE l_ntra	INTEGER
        #----------------------------------------------------------------------#
        IF t1.tstdcuneg <> t3.tsccbuneg THEN
            LET g_msj = "No puede revertir... La cuenta bancaria ha cambiado",
                        " de U/N"
            RETURN FALSE
        END IF
        #------------------- Validar Fecha de cierre contable -----------------#
        IF t4.cnprmfdes IS NOT NULL THEN
            IF t1.tstdcfdoc <= t4.cnprmfdes THEN
	        LET g_msj = "Periodo contable cerrado... No ",
                            "puede revertir"
                RETURN FALSE
            END IF
	END IF
        #-------------------- Verificacion Rechazo posterior ------------------#
	LET l_ntra = 0
	SELECT MAX(tstdrntra) INTO l_ntra
		FROM  tstdr
		WHERE tstdrcbco = t2.tstdrcbco
		  AND tstdrncta = t2.tstdrncta
		  AND tstdrnchq = t2.tstdrnchq
		  AND tstdrmrcb = t2.tstdrmrcb
	IF l_ntra > t1.tstdcntra THEN
	    LET g_msj = "Cheque tiene movimiento posterior... No puede rever",
                        "tir!"
	    RETURN FALSE
        END IF
        RETURN TRUE	

END FUNCTION

###################
# CONSULTA DE DATOS
###################

FUNCTION f4000_consulta_ts324()
        DEFINE query_1 CHAR(200),
               s1      CHAR(200)
        CLEAR FORM
        MESSAGE "Deme el criterio de seleccion y presione <ESC>"
        CONSTRUCT query_1 ON tstdcntra,tstdcndoc,tstdcfdoc,tstdccbco,
			     tstdcncta,tstdrcbco,tstdrncta,tstdrnchq
                        FROM tstdcntra,tstdcndoc,tstdcfdoc,tstdccbco,
			     tstdcncta,tstdrcbco,tstdrncta,tstdrnchq
        IF int_flag THEN
            LET int_flag = FALSE
            CLEAR FORM
            LET t1.tstdcntra = NULL
            DISPLAY BY NAME t1.tstdcntra
            MESSAGE " "
            RETURN
        END IF
        MESSAGE " "
        LET s1 = "SELECT * FROM tstdc,tstdr WHERE tstdcntra = tstdrntra ",
		 "AND ",query_1 CLIPPED," AND tstdcpref=10 AND tstdccorr=5 ",
                 "AND tstdrmrcb = 0 ORDER BY tstdcntra"
        PREPARE tstdc_s FROM s1
        DECLARE tstdc_set SCROLL CURSOR FOR tstdc_s
        OPEN    tstdc_set
        FETCH FIRST tstdc_set INTO t1.*,t2.*
        IF status = NOTFOUND THEN
            LET g_msj = "REGISTRO NO ENCONTRADO"
            CALL qx030_msgadvetencia_gb000(g_msj)
            CLEAR FORM
            LET t1.tstdcntra = NULL
            DISPLAY BY NAME t1.tstdcntra
            RETURN
        END IF
        CALL f6300_display_datos_ts324()
        MENU "CONSULTAR"
        COMMAND "Anterior" " "
                FETCH PREVIOUS tstdc_set INTO t1.*,t2.*
                IF status = NOTFOUND THEN
                        LET g_msj = "PRIMER REGISTRO"
                        CALL qx030_msgadvetencia_gb000(g_msj)
                        FETCH FIRST tstdc_set INTO t1.*,t2.*
                END IF
                CALL f6300_display_datos_ts324()
        COMMAND "Siguiente" " "
                FETCH NEXT tstdc_set INTO t1.*,t2.*
                IF status = NOTFOUND THEN
                        LET g_msj = "ULTIMO REGISTRO"
                        CALL qx030_msgadvetencia_gb000(g_msj)
                        FETCH LAST tstdc_set INTO t1.*,t2.*
                END IF
                CALL f6300_display_datos_ts324()
        COMMAND "Primero" " "
                FETCH FIRST tstdc_set INTO t1.*,t2.*
                CALL f6300_display_datos_ts324()
        COMMAND "Ultimo" " "
                FETCH LAST tstdc_set INTO t1.*,t2.*
                CALL f6300_display_datos_ts324()
        COMMAND "FIN" " "
                EXIT MENU
        END MENU
        CLOSE tstdc_set
        FREE  tstdc_s
        DISPLAY "                                                       " AT 1,1
END FUNCTION

###################
# BUSQUEDA DE DATOS
###################

FUNCTION f5000_buscar_registro_ts324()
        SELECT * INTO t1.*
                FROM  tstdc
                WHERE tstdcntra = t1.tstdcntra
                  AND tstdcpref = 10
                  AND tstdccorr = 5
                  AND tstdcmrcb = 0
	IF status = NOTFOUND THEN
            LET t1.tstdcntra = NULL
	    IF g_mtflag = 0 THEN
                DISPLAY BY NAME t1.tstdcntra
	    END IF
            RETURN
	END IF
        SELECT * INTO t2.*
	        FROM  tstdr
                WHERE tstdrntra = t1.tstdcntra
                  AND tstdrmrcb = 0
	IF status = NOTFOUND THEN
            LET t1.tstdcntra = NULL
	    IF g_mtflag = 0 THEN
                DISPLAY BY NAME t1.tstdcntra
	    END IF
            RETURN
	END IF
        LET g_marca = TRUE
        CALL f6300_display_datos_ts324()
END FUNCTION

FUNCTION f5010_buscar_gbcon_ts324(l_pfij,l_corr,band)
	DEFINE l_pfij  LIKE gbcon.gbconpfij,
	       l_corr  LIKE gbcon.gbconcorr,
	       l_desc  LIKE gbcon.gbcondesc,
	       l_abre  LIKE gbcon.gbconabre,
	       band    SMALLINT
	SELECT gbcondesc,gbconabre INTO l_desc,l_abre
		FROM  gbcon
		WHERE gbconpfij = l_pfij
		  AND gbconcorr = l_corr
		  AND gbconcorr > 0
	IF status = NOTFOUND THEN
	    RETURN " ",FALSE
	END IF
	IF band THEN
	    RETURN l_desc,TRUE
	END IF
	RETURN l_abre,TRUE
END FUNCTION

FUNCTION f5010_buscar_gbhtc_ts324(l_fech)
   DEFINE  l_fech  LIKE gbhtc.gbhtcfech,
           l_tcof  LIKE gbhtc.gbhtctcof,
           l_tcco  LIKE gbhtc.gbhtctcco,
           l_tcve  LIKE gbhtc.gbhtctcve,
           l_fcha  LIKE gbhtc.gbhtcfech,
           l_hora  LIKE gbhtc.gbhtchora,
           l_rowid INTEGER,
           l_flag  SMALLINT,
           s1      CHAR(200)

   LET l_flag = FALSE
   #--------------------------------------------------------------------------#
   LET s1 = "SELECT ROWID,gbhtcfech,gbhtctcof,gbhtctcco,gbhtctcve",
            "  FROM  gbhtc",
            "  WHERE gbhtcfech <= ?",
            "  ORDER BY 2 DESC,1 DESC"
   PREPARE tmphtc_s FROM s1
   DECLARE q_gbhtc SCROLL CURSOR FOR tmphtc_s
   #--------------------------------------------------------------------------#
   OPEN q_gbhtc USING l_fech
   FETCH q_gbhtc INTO l_rowid,l_fcha,l_tcof,l_tcco,l_tcve
   IF status <> 0 THEN
       LET g_msj = "No puede recuperar los Tipos de Cambio para la fecha: ",l_fech
       CALL qx030_msgadvetencia_gb000(g_msj)
       CLOSE q_gbhtc
       RETURN FALSE,0,0,0
   END IF
   CLOSE q_gbhtc
   RETURN TRUE,l_tcof,l_tcco,l_tcve
END FUNCTION

FUNCTION f5020_buscar_tsccb_ts324()
	INITIALIZE t3.* TO NULL
	SELECT * INTO t3.*
	        FROM  tsccb
	        WHERE tsccbcbco = t1.tstdccbco
		  AND tsccbncta = t1.tstdcncta
	IF status = NOTFOUND THEN
	    LET g_msj = "No existe"
		CALL qx030_msgadvetencia_gb000(g_msj)
	    RETURN FALSE
	END IF
	IF t3.tsccbstat = 2 THEN
	    LET g_msj = "Cuenta deshabilitada"
	    CALL qx030_msgadvetencia_gb000(g_msj)
	    RETURN FALSE
	END IF
	RETURN TRUE
END FUNCTION

FUNCTION f5030_buscar_tscha_ts324()
        INITIALIZE g_ichq,t2.tstdrcmon,g_uneg,g_stat TO NULL
	SELECT tschaimpo,tschacmon,tschauneg,tschastat
                INTO  g_ichq,t2.tstdrcmon,g_uneg,g_stat
		FROM  tscha
	        WHERE tschacbco = t2.tstdrcbco
		  AND tschancta = t2.tstdrncta
		  AND tschanchq = t2.tstdrnchq
		  AND tschatchq = 2
        IF status  = NOTFOUND THEN
            RETURN FALSE
        END IF
        RETURN TRUE
END FUNCTION

FUNCTION f5040_buscar_tsdep_ts324()
	DEFINE	l_ntra	LIKE tsdch.tsdchntra
	LET l_ntra = 0
	SELECT MAX(tsdchntra) INTO l_ntra
		FROM  tsdch
	        WHERE tsdchcbco = t2.tstdrcbco
		  AND tsdchncta = t2.tstdrncta
		  AND tsdchnchq = t2.tstdrnchq
	IF l_ntra IS NULL THEN LET l_ntra = 0 END IF
        SELECT * FROM tsdep
                WHERE tsdepntra = l_ntra 
		  AND tsdepcbco = t1.tstdccbco
                  AND tsdepncta = t1.tstdcncta
		  AND tsdepmrcb = 0
        IF status = NOTFOUND THEN
	    LET g_msj = "Cheque no ha sido depositado en esta cuenta"
	    	CALL qx030_msgadvetencia_gb000(g_msj)
            RETURN FALSE
        END IF
        RETURN TRUE
END FUNCTION

FUNCTION f5050_buscar_adhuu_ts324(l_uneg)
        DEFINE  l_uneg  LIKE adhuu.adhuuuneg
        SELECT * FROM adhuu
                WHERE adhuuusrn = g_user
                  AND adhuuuneg = l_uneg
        IF status = NOTFOUND THEN
            RETURN FALSE
        END IF
        RETURN TRUE
END FUNCTION

FUNCTION f5060_buscar_cnune_ts324(l_uneg)
	DEFINE	l_uneg	LIKE cnune.cnuneuneg,
		l_desc	LIKE cnune.cnunedesc
	SELECT cnunedesc INTO l_desc
		FROM  cnune
		WHERE cnuneuneg = l_uneg
	RETURN l_desc
END FUNCTION

###################
# RUTINAS GENERALES
###################

FUNCTION f6000_limpiar_menu_ts324()
	IF g_mtflag = 0 THEN
	    CLEAR FORM
	END IF
        INITIALIZE t1.*,t2.*,g_uneg,g_uncc TO NULL
	INITIALIZE g_cpry,g_cprg,g_cfin TO NULL
	LET g_marca = FALSE
	IF g_mtflag = 0 THEN
	    DELETE FROM adtmp
	END IF
END FUNCTION

FUNCTION f6050_buscar_empresa_ts324()
        SELECT * INTO t0.* FROM gbpmt
        SELECT * INTO t02.* FROM gbrne
        SELECT * INTO t4.* FROM cnprm
        SELECT * INTO t9.* FROM tsctl
        LET t01.* = t0.*
END FUNCTION

FUNCTION f6300_display_datos_ts324()
	IF g_mtflag = 0 THEN
            DISPLAY BY NAME t1.tstdcntra,t1.tstdcndoc,t1.tstdcfdoc,t1.tstdccbco,
                            t1.tstdcncta,t2.tstdrcbco,t2.tstdrncta,t2.tstdrnchq,
		            t2.tstdrimpt,t1.tstdctcam,t1.tstdcimpo,t1.tstdcgls1,
                            t1.tstdcgls2,t1.tstdcgls3
	END IF
	CALL f5010_buscar_gbcon_ts324(11,t1.tstdccbco,1) RETURNING g_bank,g_flag
	CALL f5020_buscar_tsccb_ts324() RETURNING g_flag
	CALL f5010_buscar_gbcon_ts324(10,t3.tsccbcmon,0) RETURNING g_mont,g_flag
	CALL f5010_buscar_gbcon_ts324(11,t2.tstdrcbco,1) RETURNING g_bcoc,g_flag
	CALL f5010_buscar_gbcon_ts324(10,t2.tstdrcmon,0) RETURNING g_monc,g_flag
	IF g_mtflag = 0 THEN
	    DISPLAY BY NAME g_bank,g_mont,g_bcoc,g_monc
	END IF
        SELECT tschauneg INTO g_uneg
                FROM  tscha
                WHERE tschacbco = t2.tstdrcbco
                  AND tschancta = t2.tstdrncta
                  AND tschanchq = t2.tstdrnchq
                  AND tschatchq = 2
END FUNCTION

###############
# OTRAS RUTINAS
###############

FUNCTION f7000_conv_importes_ts324(l_impi,l_cmon)
        DEFINE l_impi  LIKE cntcn.cntcnimpi,
               l_impc  LIKE cntcn.cntcnimpc,
               l_cmon  LIKE tstdc.tstdccmon
        LET l_impc = l_impi
        IF l_cmon = 1 AND t0.gbpmtmimp = 2 THEN
            LET l_impi = f0100_redondeo_gb000((l_impi/t0.gbpmttcof),2)
        END IF
        IF l_cmon = 2 AND t0.gbpmtmimp = 1 THEN
            LET l_impi = f0100_redondeo_gb000((l_impi*t0.gbpmttcof),2)
        END IF
        IF l_cmon = 1 AND t0.gbpmtmcon = 2 THEN
            LET l_impc = f0100_redondeo_gb000((l_impc/t0.gbpmttcof),2)
        END IF
        IF l_cmon = 2 AND t0.gbpmtmcon = 1 THEN
            LET l_impc = f0100_redondeo_gb000((l_impc*t0.gbpmttcof),2)
        END IF
        RETURN l_impi,l_impc
END FUNCTION
