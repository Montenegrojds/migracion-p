###############################################################################
# PROGRAMA: ts323.4gl
# VERSION : 5.1.0
# FECHA   : 02/09/97,03/07/98,25/03/99
# OBJETIVO: Deposito de Cheques Otros Bancos
# AUTOR   : MDR
# COMPILAR: ts323.4gl ts000.4gl ts900.4gl ad800.4gl
#                     gb000.4gl gb001.4gl gb002.4gl
###############################################################################
DATABASE tbsai
GLOBALS "gbglobs.4gl"
        DEFINE  t1       RECORD LIKE tsdep.*,
		t2       RECORD LIKE tsccb.*,
		t3       RECORD 
			  impo  LIKE tscha.tschaimpo,
			  cmon  LIKE tscha.tschacmon,
			  uneg	LIKE tscha.tschauneg,
			  stat  LIKE tscha.tschastat,
		          morg  LIKE tscha.tschamorg
			 END RECORD,
                t4       RECORD LIKE cnprm.*,
                t9       RECORD LIKE tsctl.*,
                p1       ARRAY[100] OF RECORD
			  cbco  LIKE tsdch.tsdchcbco,
			  dbco  LIKE gbcon.gbcondesc,
			  ncta  LIKE tsdch.tsdchncta,
			  nchq  LIKE tsdch.tsdchnchq,
			  impt  LIKE tsdch.tsdchimpt
                         END RECORD,
		max_v1          SMALLINT,
		g_bank          LIKE gbcon.gbcondesc,
		g_dmdp          LIKE gbcon.gbcondesc,
		g_amdp          LIKE gbcon.gbconabre,
		g_dmct          LIKE gbcon.gbcondesc,
		g_amct          LIKE gbcon.gbconabre,
                g_item          LIKE cntcn.cntcnitem,
	       	g_cctb          LIKE cntcn.cntcncctb,
		g_adic          LIKE cntcn.cntcnscaa,
                g_glosa         LIKE cntcn.cntcndesc,
		g_uncc		SMALLINT,
                g_freg          LIKE tsdep.tsdepftra,
		g_cpry          LIKE tscba.tscbacpry,
		g_cprg          LIKE tscba.tscbacprg,
		g_cfin          LIKE tscba.tscbacfin,
		g_tdst		INTEGER,
		cntr		SMALLINT,
                #################################
                # variables generales NO BORRAR #
                #################################
                t0            RECORD LIKE gbpmt.*,
                t01           RECORD LIKE gbpmt.*,
		t02	      RECORD LIKE gbrne.*,
		t03	      RECORD LIKE cnpmf.*,
	       #---------------------------------#
	        g_nmod               CHAR(16),
	        g_titu               CHAR(33),
		g_vers	             CHAR(6),
                g_uaut               CHAR(3),
	       #---------------------------------#
                i                    SMALLINT,
                g_flag               SMALLINT,
                g_marca              SMALLINT,
                g_user               CHAR(3),
                g_nive               SMALLINT,
                g_rows               SMALLINT,
                g_mgui               CHAR(1),
		g_spool		     CHAR(15),
                g_hora               CHAR(8),
                g_fpro               DATE


MAIN DEFER INTERRUPT IF NOT f0000_open_database_gb000() THEN EXIT PROGRAM END IF
	LET g_mtflag = 0
        OPTIONS PROMPT   LINE 23,
          --* ON CLOSE APPLICATION CONTINUE,
		ERROR    LINE 24,
                INSERT   KEY CONTROL-O,
                DELETE   KEY CONTROL-E,
                NEXT     KEY CONTROL-N,
                PREVIOUS KEY CONTROL-U
        SET LOCK MODE TO WAIT
        #WHENEVER ERROR CONTINUE
        OPEN FORM ts323_01 FROM "ts323a"
        DISPLAY FORM ts323_01
	LET g_fpro = TODAY
        LET g_user = arg_val(1)
        LET g_mgui = arg_val(2)
--*     LET g_mgui = "N"        
        LET g_nive = arg_val(3)
        LET g_freg = "01/01/1900"
        CALL f6050_buscar_empresa_ts323()
       #-----------------------------------------------------------------------
	LET g_nmod = "TESORERIA"
	LET g_titu = "DEPOSITO CHEQUES OTROS BANCOS"
	LET g_vers = "5.1.12s"
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
        CALL f0500_cursor_ts323()
        CALL f7000_crear_temporal_ad800()
        CALL f0250_declarar_puntero_ts323()
        CALL f0300_proceso_ts323()
END MAIN

#########################
# DECLARACION DE PUNTEROS
#########################

FUNCTION f0250_declarar_puntero_ts323()
	DEFINE	s1	CHAR(500)
        DECLARE q_adtmp CURSOR FOR
                SELECT * FROM adtmp
                        ORDER BY item
       	#----------------------------------------------------------------------#
       	LET s1 = "SELECT nout FROM tmpad1",
                 "           WHERE tipo = ?"
       	PREPARE set_tmpad1 FROM s1
       	DECLARE q_tmpad1 CURSOR FOR set_tmpad1
       	#----------------------------------------------------------------------#
END FUNCTION

#################
# PROCESO CENTRAL
#################

FUNCTION f0300_proceso_ts323()
        DEFINE 	l_ndoc  LIKE tsdep.tsdepndoc,
	       	l_desc  CHAR(7),
	       	l_cdin  CHAR(40),
	       	l_fld   SMALLINT,
               	l_key   SMALLINT,
               	l_exit  SMALLINT,
                l_freg  LIKE cpmcp.cpmcpfreg,
                l_tcof  LIKE gbhtc.gbhtctcof,
                l_tcco  LIKE gbhtc.gbhtctcco,
                l_tcve  LIKE gbhtc.gbhtctcve

	WHILE TRUE
        CALL f6000_limpiar_menu_ts323()
        IF g_freg = "01/01/1900" THEN
           LET g_freg = t0.gbpmtfdia
        END IF
        INPUT BY NAME t1.tsdepntra WITHOUT DEFAULTS
		ON KEY (CONTROL-C,INTERRUPT)
                        LET int_flag = TRUE
			EXIT INPUT
                ON KEY (CONTROL-B)
                        CALL f4000_consulta_ts323()
                        IF t1.tsdepntra IS NOT NULL THEN
                            EXIT INPUT
                        END IF
	END INPUT
	IF int_flag THEN
	    RETURN
	END IF
        CALL f5000_buscar_registro_ts323()
        MESSAGE " "
        IF g_marca THEN
            MESSAGE " CTRL-Z para reimprimir comprobante"
        END IF
        INPUT BY NAME t1.tsdepndoc,t1.tsdepftra,t1.tsdepcbco,t1.tsdepncta,
		      t1.tsdepcmon,t1.tsdeptcam,t1.tsdepgls1,
		      t1.tsdepgls2,t1.tsdepgls3
                WITHOUT DEFAULTS
		ON KEY (CONTROL-C,INTERRUPT)
			MESSAGE " "
		        LET int_flag = TRUE 
			EXIT INPUT
                ON KEY (F1,CONTROL-P)
                        CALL f4000_accesos_rapidos_ad800(g_user,8,2,g_nive)
		ON KEY (CONTROL-E)
                        IF g_marca AND g_uncc THEN
			    MESSAGE " "
	                    IF t0.gbpmtfdia >= t1.tsdepftra THEN
				LET l_cdin = NULL
                                IF NOT f0330_validar_ts323() THEN
				    CALL qx031_msgadvertencia_gb000(g_msj,2)
			            LET int_flag = TRUE
		                    EXIT INPUT
                                END IF
			        CALL f0402_autorizacion_ad800
					 (g_user,96,2,t1.tsdepimpt,t1.tsdepcmon,
					  l_cdin,16,1,t1.tsdepftra,161,
					  t1.tsdepntra)
			    	          RETURNING g_uaut,g_flag
			        IF g_flag THEN
                                    IF f3000_borrar_ts323() THEN
			                LET int_flag = TRUE
		                        EXIT INPUT
			            END IF
			        END IF
			    ELSE
				LET g_msj =  "No puede revertir por incompati",
                                             "bilidad de fechas"
				CALL qx030_msgadvetencia_gb000(g_msj)
	                    END IF
                        END IF
		ON KEY (CONTROL-V)
                        IF INFIELD(tsdepcbco) THEN
			    CALL f0200_selec_cursor_ts900(5,11,0)
			              RETURNING t1.tsdepcbco,g_bank
                            DISPLAY BY NAME t1.tsdepcbco,g_bank
     		            NEXT FIELD tsdepcbco
                        END IF
                        IF INFIELD(tsdepncta) THEN
			    CALL f0200_selec_cursor_ts900(1,t1.tsdepcbco,0)
			              RETURNING l_desc,t1.tsdepncta
			    DISPLAY BY NAME t1.tsdepncta
     		            NEXT FIELD tsdepncta
                        END IF
                        IF INFIELD(tsdepcmon) THEN
                            CALL f0200_selec_cursor_ts900(5,10,0)
                                      RETURNING t1.tsdepcmon,g_dmdp
                            DISPLAY BY NAME t1.tsdepcmon,g_dmdp
			    NEXT FIELD tsdepcmon
                        END IF
                ON KEY (CONTROL-T)
                        IF g_marca THEN
			    MESSAGE " "
                            CALL set_count(max_v1)
                            DISPLAY ARRAY p1 TO s1.* ATTRIBUTE(REVERSE)
                                  ON KEY (CONTROL-C,INTERRUPT)
                                      EXIT DISPLAY
                            END DISPLAY
			    LET int_flag = FALSE
                            MESSAGE " <CTRL-T> Detalle de Cheques"
                        END IF

                ON KEY (CONTROL-Z)
                        IF g_marca THEN
                            CALL f8000_imprimir_comprobante_ts323()
                        END IF

                BEFORE INPUT
			LET l_exit = FALSE
                        IF g_marca THEN
                            MESSAGE " <CTRL-T> Detalle de Cheques, <CTRL-Z> Reimprime"
                            #------------ Validar Unidad de Negocio -----------#
                            LET g_uncc = TRUE
                            IF NOT f5040_buscar_adhuu_ts323(t1.tsdepuneg) THEN
                                LET g_msj =  "Usuario no habilitado en la U/N ",
                                      t1.tsdepuneg USING "<<<<"
                                CALL qx030_msgadvetencia_gb000(g_msj)      
                                LET g_uncc = FALSE
                            END IF
			    #----------- Validar Cierre contable ------------#
                            IF t4.cnprmfdes IS NOT NULL THEN
                            	IF t1.tsdepftra <= t4.cnprmfdes THEN
				    LET g_msj =  "Periodo contable cerrado...",
                                    " No puede modificar"
                                    CALL qx030_msgadvetencia_gb000(g_msj)     
                               	    LET l_exit = TRUE
                                END IF
			    END IF
			    #------------------------------------------------#
                            LET t0.gbpmtfdia = t1.tsdepftra
                            CALL f5010_buscar_gbhtc_ts323(t1.tsdepftra)
                                     RETURNING g_flag,l_tcof,l_tcco,l_tcve
                            IF NOT g_flag THEN
                               NEXT FIELD tsdepftra
                            END IF
                            LET t0.gbpmttcof = l_tcof
                            LET t0.gbpmttcco = l_tcco
                            LET t0.gbpmttcve = l_tcve
                          ELSE
                            LET t1.tsdepftra = g_freg
                            LET t0.gbpmtfdia = g_freg
                            DISPLAY BY NAME t1.tsdepftra
                        END IF
			IF t1.tsdepftra IS NULL THEN
			    LET t1.tsdepftra = t0.gbpmtfdia
			    DISPLAY BY NAME t1.tsdepftra
			END IF
                        LET l_ndoc = t1.tsdepndoc
			DISPLAY BY NAME t1.tsdepichq,t1.tsdepimpo
                AFTER FIELD tsdepndoc
			MESSAGE " "
			IF l_exit THEN 
			    LET int_flag = TRUE
			    EXIT INPUT
			END IF 
                        IF g_marca THEN
                            LET t1.tsdepndoc = l_ndoc
                            LET int_flag = FALSE
                            EXIT INPUT
                        END IF
               BEFORE FIELD tsdepftra
                      LET l_freg = t1.tsdepftra
                      IF g_marca THEN
                          NEXT FIELD cpmcpuneg
                      END IF
               AFTER FIELD tsdepftra
                      IF t1.tsdepftra IS NOT NULL THEN
                          IF t1.tsdepftra < t01.gbpmtfini THEN
                              LET g_msj =  "Fecha de Gestion Pasada"
                              CALL qx030_msgadvetencia_gb000(g_msj)
                              LET t1.tsdepftra = l_freg
                              NEXT FIELD tsdepftra
                          END IF
                          IF t1.tsdepftra > t01.gbpmtfdia THEN
                              LET g_msj =  "La Fecha no puede ser Mayor ",
                                    "a la Fecha del Sistema"
                              CALL qx030_msgadvetencia_gb000(g_msj)      
                              LET t1.tsdepftra = l_freg
                              NEXT FIELD tsdepftra
                          END IF
			  #----------- Validar Cierre contable ------------#
                          IF t4.cnprmfdes IS NOT NULL THEN
                              IF t1.tsdepftra <= t4.cnprmfdes THEN
				  LET g_msj =  "Periodo contable cerrado"
				  CALL qx030_msgadvetencia_gb000(g_msj)
                                  LET t1.tsdepftra = l_freg
                                  NEXT FIELD tsdepftra
                              END IF
			  END IF
			  #------------------------------------------------#
                          IF t1.tsdepftra <> t01.gbpmtfdia THEN
                              IF t1.tsdepftra <> l_freg THEN
                                  LET l_cdin = "Fecha del Sistema: ",
                                                t01.gbpmtfdia," -- ",
                                               "Fecha Modificada: ",
                                                t1.tsdepftra
                                  CALL f0400_autorizacion_ad800
                                            (g_user,96,13,0,0,l_cdin,
                                             16,1,t1.tsdepftra)
                                          RETURNING g_uaut,g_flag
                                  IF NOT g_flag THEN
                                      LET g_msj =  "Necesita Autorizacion para ",
                                            "Modificar Fecha"
                                      CALL qx030_msgadvetencia_gb000(g_msj)      
                                      LET t1.tsdepftra = l_freg
                                      NEXT FIELD tsdepftra
                                  END IF
                              END IF

                              LET t0.gbpmtfdia = t1.tsdepftra
                              CALL f5010_buscar_gbhtc_ts323(t1.tsdepftra)
                                        RETURNING g_flag,l_tcof,l_tcco,l_tcve
                              IF NOT g_flag THEN
                                  LET t1.tsdepftra = l_freg
                                  NEXT FIELD tsdepftra
                              END IF
                              LET t0.gbpmttcof = l_tcof
                              LET t0.gbpmttcco = l_tcco
                              LET t0.gbpmttcve = l_tcve
                          ELSE
                              LET t0.* = t01.*
                          END IF
                      ELSE
                          LET t1.tsdepftra = t01.gbpmtfdia
                          LET t0.* = t01.*
                      END IF
                      LET g_freg = t1.tsdepftra
                      DISPLAY BY NAME t1.tsdepftra

                AFTER FIELD tsdepcbco
                        IF t1.tsdepcbco IS NULL THEN
                            NEXT FIELD tsdepcbco
                        END IF
			CALL f5010_buscar_gbcon_ts323(11,t1.tsdepcbco)
				  RETURNING g_bank,l_desc,g_flag
			IF NOT g_flag THEN
			    LET g_msj =  "No existe"
				CALL qx030_msgadvetencia_gb000(g_msj)	
			    NEXT FIELD tsdepcbco
			END IF
			DISPLAY BY NAME g_bank
                AFTER FIELD tsdepncta
                        IF t1.tsdepncta IS NULL THEN
                            NEXT FIELD tsdepncta
                        END IF
			IF NOT f5020_buscar_tsccb_ts323() THEN
			    NEXT FIELD tsdepncta
			END IF
                        IF NOT f5040_buscar_adhuu_ts323(t2.tsccbuneg) THEN
                            LET g_msj =  "Usuario no habilitado en la U/N ",
                                  t2.tsccbuneg USING "<<<<"
                            CALL qx030_msgadvetencia_gb000(g_msj)      
                            NEXT FIELD tsdepncta
                        END IF
	                CALL f5010_buscar_gbcon_ts323(10,t2.tsccbcmon)
			          RETURNING g_dmct,g_amct,g_flag
			LET g_amct[5,5] = ":"
                AFTER FIELD tsdepcmon
			IF t1.tsdepcmon IS NULL THEN
			    NEXT FIELD tsdepcmon
			END IF
			CALL f5010_buscar_gbcon_ts323(10,t1.tsdepcmon)
				  RETURNING g_dmdp,g_amdp,g_flag
			LET g_amdp[5,5] = ":"
			IF NOT g_flag THEN
			    LET g_msj =  "No existe"
				CALL qx030_msgadvetencia_gb000(g_msj)	
			    NEXT FIELD tsdepcmon
			END IF
			DISPLAY BY NAME g_dmdp,g_amdp,g_amct
			CALL f0310_calcular_totales_ts323()
			#------------- Validar con moneda de Cheques ----------#
			IF t1.tsdepichq > 0 THEN
			    FOR i=1 TO max_v1
				IF p1[i].ncta IS NOT NULL THEN
				    EXIT FOR
				END IF
			    END FOR
                            CALL f5030_buscar_tscha_ts323
				      (p1[i].cbco,p1[i].ncta,p1[i].nchq)
				      RETURNING g_flag
			    IF t1.tsdepcmon <> t3.cmon THEN
				    LET g_msj =  "No puede modificar moneda del deposito"
			        CALL qx030_msgadvetencia_gb000(g_msj)
			        NEXT FIELD tsdepcmon
			    END IF
			END IF
			#------------------------------------------------------#
                BEFORE FIELD tsdeptcam
			IF t1.tsdeptcam IS NULL AND t1.tsdepcmon = t2.tsccbcmon
		        THEN
			    LET t1.tsdeptcam = t0.gbpmttcof
			END IF
                AFTER FIELD tsdeptcam
                        IF t1.tsdeptcam IS NULL OR t1.tsdeptcam <= 0 THEN
                            NEXT FIELD tsdeptcam
                        END IF
			CALL f0310_calcular_totales_ts323()
                        LET l_key = fgl_lastkey()
                        LET l_fld = (l_key = fgl_keyval("ESC")) OR
                        			(l_key = fgl_keyval("ACCEPT")) OR
                                    (l_key = fgl_keyval("LEFT"))   OR
                                    (l_key = fgl_keyval("UP")) 
                        IF NOT l_fld THEN
                            CALL f0400_proceso_cheques_ts323()
                        END IF
		AFTER FIELD tsdepgls1
                        LET l_key = fgl_lastkey()
                        LET l_fld = (l_key = fgl_keyval("LEFT")) OR
                                    (l_key = fgl_keyval("UP")) 
                        IF l_fld THEN
                            CALL f0400_proceso_cheques_ts323()
                        END IF
                AFTER INPUT
                        IF t1.tsdepcbco IS NULL THEN
                            NEXT FIELD tsdepcbco
                        END IF
                        IF t1.tsdepncta IS NULL THEN
                            NEXT FIELD tsdepncta
                        END IF
			IF NOT f5020_buscar_tsccb_ts323() THEN
			    NEXT FIELD tsdepncta
			END IF
			IF t1.tsdepcmon IS NULL THEN
			    NEXT FIELD tsdepcmon
			END IF
                        IF t1.tsdeptcam IS NULL THEN
                            NEXT FIELD tsdeptcam
                        END IF
                        IF t1.tsdepichq IS NULL THEN
			    LET t1.tsdepichq = 0
                        END IF
			IF t1.tsdepimpt = 0 THEN
			    LET g_msj =  "Depositos...?"
				CALL qx030_msgadvetencia_gb000(g_msj)	
			    NEXT FIELD tsdeptcam
			END IF
	END INPUT
	IF int_flag THEN
	    LET int_flag = FALSE
            CONTINUE WHILE
        END IF
	IF g_marca = FALSE THEN
            IF f1000_altas_ts323() THEN
                CALL f8000_imprimir_comprobante_ts323()
            END IF
        ELSE
            CALL f8000_imprimir_comprobante_ts323()
	END IF
	END WHILE
END FUNCTION

FUNCTION f0310_calcular_totales_ts323()
	LET t1.tsdepichq = 0
	FOR i=1 TO max_v1
	    IF p1[i].impt IS NULL THEN
		CONTINUE FOR
	    END IF
	    LET t1.tsdepichq = t1.tsdepichq + p1[i].impt
	END FOR
	LET t1.tsdepimpt = t1.tsdepichq
	LET t1.tsdepimpo = t1.tsdepimpt
        IF t1.tsdepcmon = 1 AND t2.tsccbcmon = 2 THEN 
	    LET t1.tsdepimpo = f0100_redondeo_gb000(t1.tsdepimpo/t1.tsdeptcam,2)
	END IF
        IF t1.tsdepcmon = 2 AND t2.tsccbcmon = 1 THEN 
	    LET t1.tsdepimpo = f0100_redondeo_gb000(t1.tsdepimpo*t1.tsdeptcam,2)
	END IF
	DISPLAY BY NAME t1.tsdepichq,t1.tsdepimpo
END FUNCTION

FUNCTION f0400_proceso_cheques_ts323()
        DEFINE 	l_cbcd  LIKE tscdc.tscdccbcd,
		l_nctd	LIKE tscdc.tscdcnctd,
		l_curr  SMALLINT,
               	l_line  SMALLINT,
	       	l_desc  CHAR(7)
        CALL set_count(max_v1)
        INPUT ARRAY p1 WITHOUT DEFAULTS FROM s1.*
                ON KEY (CONTROL-C,INTERRUPT)
                        IF p1[l_curr].cbco IS NOT NULL THEN
			    CALL f5010_buscar_gbcon_ts323(11,p1[l_curr].cbco)
				      RETURNING p1[l_curr].dbco,l_desc,g_flag
			    IF NOT g_flag THEN
				NEXT FIELD cbco
			    END IF
			    IF p1[l_curr].cbco = t1.tsdepcbco THEN
				NEXT FIELD cbco
			    END IF
                            IF p1[l_curr].ncta IS NULL THEN  
                                NEXT FIELD ncta
                            END IF
                            IF p1[l_curr].nchq IS NULL THEN  
                                NEXT FIELD ncqh
                            END IF
                            IF f0410_repetidos_ts323(l_curr) THEN
			        NEXT FIELD nchq
			    END IF
                            IF NOT f5030_buscar_tscha_ts323
			       (p1[l_curr].cbco,p1[l_curr].ncta,p1[l_curr].nchq)
		            THEN
			        NEXT FIELD nchq
			    END IF
			    #--------------------------------------------------#
			    # Validacion si cheque emitido p/deposito en cuenta
			    IF t3.morg = 96 THEN
			        INITIALIZE l_cbcd,l_nctd TO NULL
			        SELECT tscdccbcd,tscdcnctd INTO l_cbcd,l_nctd
				       FROM  tscdc
				       WHERE tscdccbco = p1[l_curr].cbco 
				         AND tscdcncta = p1[l_curr].ncta 
				         AND tscdcnchq = p1[l_curr].nchq 
			        IF l_cbcd <> t1.tsdepcbco OR 
			           l_nctd <> t1.tsdepncta THEN
			            NEXT FIELD nchq
			        END IF
			    END IF
			    #--------------------------------------------------#
			    IF t1.tsdepcmon <> t3.cmon THEN
			        NEXT FIELD nchq
			    END IF
                            IF NOT f5040_buscar_adhuu_ts323(t3.uneg) THEN
                                LET g_msj =  "Usuario no habilitado en la U/N ",
                                      t3.uneg USING "<<<<"
                                CALL qx030_msgadvetencia_gb000(g_msj)      
                                NEXT FIELD nchq
                            END IF
			    LET g_flag = TRUE
			    CASE t3.stat
			          WHEN 3 LET g_msj =  "Cheque Depositado"
			          WHEN 4 LET g_msj =  "Cheque dado de Baja"
			          WHEN 5 LET g_msj =  "Cheque Anulado"
			          WHEN 6 LET g_msj =  "Cheque Cambiado"
			       OTHERWISE LET g_flag = FALSE
			    END CASE
			    CALL qx030_msgadvetencia_gb000(g_msj)
			    IF g_flag THEN
			        NEXT FIELD nchq
			    END IF
                            IF p1[l_curr].impt IS NULL OR
			       p1[l_curr].impt <= 0    THEN  
                                NEXT FIELD impt
                            END IF
			    IF p1[l_curr].impt <> t3.impo THEN
			        NEXT FIELD impt
			    END IF
			END IF
                        LET int_flag = TRUE
			EXIT INPUT
                ON KEY (F1,CONTROL-P)
                        CALL f4000_accesos_rapidos_ad800(g_user,8,2,g_nive)
		        DISPLAY p1[l_curr].* TO s1[l_line].*
                ON KEY (CONTROL-V)
                        IF INFIELD(cbco) THEN
			    CALL f0200_selec_cursor_ts900(5,11,0)
			              RETURNING p1[l_curr].cbco,p1[l_curr].dbco
			    DISPLAY p1[l_curr].* TO s1[l_line].*
     		            NEXT FIELD cbco
                        END IF
                        IF INFIELD(nchq) THEN
			    CALL f0200_selec_cursor_ts900
				      (7,p1[l_curr].cbco,p1[l_curr].ncta)
			              RETURNING l_desc,p1[l_curr].nchq
			    DISPLAY p1[l_curr].nchq TO s1[l_line].nchq
     		            NEXT FIELD nchq
                        END IF
                BEFORE ROW
                        LET l_curr = arr_curr()
                        LET l_line = scr_line()
                        CALL f5030_buscar_tscha_ts323
		  	       (p1[l_curr].cbco,p1[l_curr].ncta,p1[l_curr].nchq)
				  RETURNING g_flag
                        LET max_v1 = arr_count()
			CALL f0310_calcular_totales_ts323()
		AFTER DELETE
			CALL f0310_calcular_totales_ts323()
		AFTER INSERT
			CALL f0310_calcular_totales_ts323()
                AFTER FIELD cbco
			IF p1[l_curr].cbco IS NOT NULL THEN
			    CALL f5010_buscar_gbcon_ts323(11,p1[l_curr].cbco)
				  RETURNING p1[l_curr].dbco,l_desc,g_flag
			    IF NOT g_flag THEN
				LET g_msj =  "No existe"
				CALL qx030_msgadvetencia_gb000(g_msj)
				NEXT FIELD cbco
			    END IF
			    DISPLAY p1[l_curr].dbco TO s1[l_line].dbco
			    IF p1[l_curr].cbco = t1.tsdepcbco THEN
				LET g_msj =  "No puede ser igual al Banco del ",
				      "Deposito"
				      CALL qx030_msgadvetencia_gb000(g_msj)
				NEXT FIELD cbco
			    END IF
                            IF f0410_repetidos_ts323(l_curr) THEN
				LET g_msj =  "Cheque repetido"
					CALL qx030_msgadvetencia_gb000(g_msj)
			        NEXT FIELD nchq
			    END IF
			    IF p1[l_curr].ncta IS NULL THEN
			        NEXT FIELD ncta
			    END IF
			    IF p1[l_curr].nchq IS NOT NULL THEN
                                IF NOT f5030_buscar_tscha_ts323(p1[l_curr].cbco,
							        p1[l_curr].ncta,
							        p1[l_curr].nchq)
		                THEN
			            LET g_msj =  "No existe"
			            CALL qx030_msgadvetencia_gb000(g_msj)
			            NEXT FIELD nchq
			        END IF
                                IF NOT f5040_buscar_adhuu_ts323(t3.uneg) THEN
                                    LET g_msj =  "Usuario no habilitado en la U/N ",
                                          t3.uneg USING "<<<<"
                                    CALL qx030_msgadvetencia_gb000(g_msj)      
                                    NEXT FIELD nchq
                                END IF
			    END IF
			END IF
                BEFORE FIELD ncta
			IF p1[l_curr].cbco IS NULL THEN
			    NEXT FIELD cbco
			END IF
                AFTER FIELD ncta
			IF p1[l_curr].ncta IS NULL THEN
			    NEXT FIELD ncta
			END IF
                        IF f0410_repetidos_ts323(l_curr) THEN
			    LET g_msj =  "Cheque repetido"
			    CALL qx030_msgadvetencia_gb000(g_msj)
			    NEXT FIELD nchq
			END IF
			IF p1[l_curr].nchq IS NULL THEN
			    NEXT FIELD nchq
			ELSE
                            IF NOT f5030_buscar_tscha_ts323(p1[l_curr].cbco,
							    p1[l_curr].ncta,
							    p1[l_curr].nchq)
		            THEN
			        LET g_msj =  "No existe"
			        CALL qx030_msgadvetencia_gb000(g_msj)
			        NEXT FIELD nchq
			    END IF
                            IF NOT f5040_buscar_adhuu_ts323(t3.uneg) THEN
                                LET g_msj =  "Usuario no habilitado en la U/N ",
                                      t3.uneg USING "<<<<"
                                CALL qx030_msgadvetencia_gb000(g_msj)      
                                NEXT FIELD nchq
                            END IF
			END IF
                BEFORE FIELD nchq
			IF p1[l_curr].ncta IS NULL THEN
			    NEXT FIELD ncta
			END IF
                AFTER FIELD nchq
                        IF p1[l_curr].nchq IS NULL THEN
			    NEXT FIELD nchq
                        END IF
                        IF NOT f5030_buscar_tscha_ts323(p1[l_curr].cbco,
						        p1[l_curr].ncta,
						        p1[l_curr].nchq)
		        THEN
			    LET g_msj =  "No existe"
			    CALL qx030_msgadvetencia_gb000(g_msj)
			    NEXT FIELD nchq
			END IF
			#------------------------------------------------------#
			# Validacion si cheque emitido para deposito en cuenta
			IF t3.morg = 96 THEN
			    INITIALIZE l_cbcd,l_nctd TO NULL
			    SELECT tscdccbcd,tscdcnctd INTO l_cbcd,l_nctd
				   FROM  tscdc
				   WHERE tscdccbco = p1[l_curr].cbco 
				     AND tscdcncta = p1[l_curr].ncta 
				     AND tscdcnchq = p1[l_curr].nchq 
			    IF l_cbcd <> t1.tsdepcbco OR l_nctd <> t1.tsdepncta
			    THEN
				LET g_msj =  "Cheque debe ser depositado en la ",
				      "cuenta ",l_nctd CLIPPED
				    CALL qx030_msgadvetencia_gb000(g_msj)  
			        NEXT FIELD nchq
			    END IF
			END IF
			#------------------------------------------------------#
			IF t1.tsdepcmon <> t3.cmon THEN
			    LET g_msj =  "Moneda del Cheque distinta a la del Deposito"
			    CALL qx030_msgadvetencia_gb000(g_msj)
			    NEXT FIELD nchq
			END IF
                        IF NOT f5040_buscar_adhuu_ts323(t3.uneg) THEN
                            LET g_msj =  "Usuario no habilitado en la U/N ",
                                  t3.uneg USING "<<<<"
                            CALL qx030_msgadvetencia_gb000(g_msj)      
                            NEXT FIELD nchq
                        END IF
			LET g_flag = TRUE
			CASE t3.stat
			      WHEN 3 LET g_msj =  "Cheque Depositado"
			      WHEN 4 LET g_msj =  "Cheque dado de Baja"
			      WHEN 5 LET g_msj =  "Cheque Anulado"
			      WHEN 6 LET g_msj =  "Cheque Cambiado"
			   OTHERWISE LET g_flag = FALSE
			END CASE
			CALL qx030_msgadvetencia_gb000(g_msj)
			IF g_flag THEN
			    NEXT FIELD nchq
			END IF
                        IF f0410_repetidos_ts323(l_curr) THEN
			    LET g_msj =  "Cheque repetido"
			    CALL qx030_msgadvetencia_gb000(g_msj)
			    NEXT FIELD nchq
			END IF
			IF p1[l_curr].impt IS NULL THEN
			    NEXT FIELD impt
			END IF
                BEFORE FIELD impt
			IF p1[l_curr].nchq IS NULL THEN
			    NEXT FIELD nchq
			END IF
                AFTER FIELD impt
                        IF p1[l_curr].impt IS NULL OR p1[l_curr].impt <= 0 THEN
			    NEXT FIELD impt
                        END IF
			IF p1[l_curr].impt <> t3.impo THEN
			    LET g_msj =  "No coincide con el importe del Cheque... ",
				  "Verificar!"
				CALL qx030_msgadvetencia_gb000(g_msj)  
			    NEXT FIELD impt
			END IF
			CALL f0310_calcular_totales_ts323()
                 AFTER INPUT
                        LET max_v1 = arr_count()
			CALL f0310_calcular_totales_ts323()
        END INPUT
        LET max_v1 = arr_count()
        LET int_flag = FALSE
END FUNCTION

FUNCTION f0410_repetidos_ts323(l_curr) 
        DEFINE l_curr  SMALLINT
	FOR i=1 TO arr_count()
            IF (i<>l_curr) AND (p1[i].cbco = p1[l_curr].cbco) AND
                                (p1[i].ncta = p1[l_curr].ncta) AND
                                (p1[i].nchq = p1[l_curr].nchq) THEN
                RETURN TRUE
            END IF
	END FOR
	RETURN FALSE
END FUNCTION

FUNCTION f0500_cursor_ts323()
	DEFINE s1  CHAR(250)
        LET s1 = "SELECT tschaimpo,tschacmon,tschauneg,tschastat,tschamorg ",
		 "FROM tscha ",
	         "WHERE tschacbco=? AND tschancta=? AND tschanchq=? ",
		 "AND tschatchq = 2 FOR UPDATE"
        PREPARE tscha_s FROM s1
        DECLARE q_tscha CURSOR FOR tscha_s
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

FUNCTION f0330_validar_ts323()
	#----------------------------------------------------------------------#
       IF t1.tsdepuneg <> t2.tsccbuneg THEN
           LET g_msj = "No puede revertir... ",
                       "La cuenta bancaria ha cambiado de U/N"
           RETURN FALSE
       END IF
       #------------------- Validar Fecha de cierre contable -----------------#
       IF t4.cnprmfdes IS NOT NULL THEN
           IF t1.tsdepftra <= t4.cnprmfdes THEN
               LET g_msj = "Periodo contable cerrado... No ",
                           "puede revertir"
               IF g_mtflag = 0 THEN SLEEP 2 END IF
               RETURN FALSE
           END IF
       END IF
       RETURN TRUE

END FUNCTION

###################
# CONSULTA DE DATOS
###################

FUNCTION f4000_consulta_ts323()
        DEFINE query_1 CHAR(200),
               s1      CHAR(200)
        CLEAR FORM
        MESSAGE "Deme el criterio de seleccion y presione <ESC>"
        CONSTRUCT query_1 ON tsdepntra,tsdepndoc,tsdepftra,tsdepcbco,tsdepncta
                        FROM tsdepntra,tsdepndoc,tsdepftra,tsdepcbco,tsdepncta
        IF int_flag THEN
            LET int_flag = FALSE
            CLEAR FORM
            LET t1.tsdepntra = NULL
            DISPLAY BY NAME t1.tsdepntra
            MESSAGE " "
            RETURN
        END IF
        MESSAGE " "
        LET s1 = "SELECT * FROM tsdep WHERE ",query_1 CLIPPED,
                 " AND tsdeptdep = 2 AND tsdepmrcb = 0 ORDER BY tsdepntra"
        PREPARE tsdep_s FROM s1
        DECLARE tsdep_set SCROLL CURSOR FOR tsdep_s
        OPEN    tsdep_set
        FETCH FIRST tsdep_set INTO t1.*
        IF status = NOTFOUND THEN
            LET g_msj =  "REGISTRO NO ENCONTRADO"
            CALL qx030_msgadvetencia_gb000(g_msj)
            CLEAR FORM
            LET t1.tsdepntra = NULL
            DISPLAY BY NAME t1.tsdepntra
            RETURN
        END IF
        CALL f6300_display_datos_ts323()
        MENU "CONSULTAR"
        COMMAND "Anterior" " "
                FETCH PREVIOUS tsdep_set INTO t1.*
                IF status = NOTFOUND THEN
                        LET g_msj =  "PRIMER REGISTRO"
                        CALL qx030_msgadvetencia_gb000(g_msj)
                        FETCH FIRST tsdep_set INTO t1.*
                END IF
                CALL f6300_display_datos_ts323()
        COMMAND "Siguiente" " "
                FETCH NEXT tsdep_set INTO t1.*
                IF status = NOTFOUND THEN
                        LET g_msj =  "ULTIMO REGISTRO"
                        CALL qx030_msgadvetencia_gb000(g_msj)
                        FETCH LAST tsdep_set INTO t1.*
                END IF
                CALL f6300_display_datos_ts323()
        COMMAND "Primero" " "
                FETCH FIRST tsdep_set INTO t1.*
                CALL f6300_display_datos_ts323()
        COMMAND "Ultimo" " "
                FETCH LAST tsdep_set INTO t1.*
                CALL f6300_display_datos_ts323()
        COMMAND "FIN" " "
                EXIT MENU
        END MENU
        CLOSE tsdep_set
        FREE  tsdep_s
        DISPLAY "                                                       " AT 1,1
END FUNCTION

###################
# BUSQUEDA DE DATOS
###################

FUNCTION f5000_buscar_registro_ts323()
        SELECT * INTO t1.*
                FROM  tsdep
                WHERE tsdepntra = t1.tsdepntra
                  AND tsdeptdep = 2
                  AND tsdepmrcb = 0
	IF status = NOTFOUND THEN
            LET t1.tsdepntra = NULL
	    IF g_mtflag = 0 THEN
                DISPLAY BY NAME t1.tsdepntra
	    END IF
            RETURN
	END IF
        LET g_marca = TRUE
        CALL f6300_display_datos_ts323()
END FUNCTION

FUNCTION f5010_buscar_gbcon_ts323(l_pfij,l_corr)
	DEFINE l_pfij  LIKE gbcon.gbconpfij,
	       l_corr  LIKE gbcon.gbconcorr,
	       l_desc  LIKE gbcon.gbcondesc,
	       l_abre  LIKE gbcon.gbconabre
	SELECT gbcondesc,gbconabre INTO l_desc,l_abre
		FROM  gbcon
		WHERE gbconpfij = l_pfij
		  AND gbconcorr = l_corr
		  AND gbconcorr > 0
	IF status = NOTFOUND THEN
	    RETURN " "," ",FALSE
	END IF
	RETURN l_desc,l_abre,TRUE
END FUNCTION

FUNCTION f5010_buscar_gbhtc_ts323(l_fech)
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
	#----------------------------------------------------------------------#
   	LET s1 = "SELECT ROWID,gbhtcfech,gbhtctcof,gbhtctcco,gbhtctcve",
   		 "  FROM  gbhtc",
            	 "  WHERE gbhtcfech <= ?",
            	 "  ORDER BY 2 DESC,1 DESC"
   	PREPARE tmphtc_s FROM s1
   	DECLARE q_gbhtc SCROLL CURSOR FOR tmphtc_s
   	#----------------------------------------------------------------------#
   	OPEN q_gbhtc USING l_fech
   	FETCH q_gbhtc INTO l_rowid,l_fcha,l_tcof,l_tcco,l_tcve
   	IF status <> 0 THEN
            LET g_msj = "No puede recuperar los Tipos de ",
			"Cambio para la fecha: ",l_fech
	    CALL qx030_msgadvetencia_gb000(g_msj)
            CLOSE q_gbhtc
            RETURN FALSE,0,0,0
   	END IF
   	CLOSE q_gbhtc
   	RETURN TRUE,l_tcof,l_tcco,l_tcve
END FUNCTION

FUNCTION f5020_buscar_tsccb_ts323()
	INITIALIZE t2.* TO NULL
	SELECT * INTO t2.*
	        FROM  tsccb
	        WHERE tsccbcbco = t1.tsdepcbco
		  AND tsccbncta = t1.tsdepncta
	IF status = NOTFOUND THEN
	    LET g_msj = "No existe"
	    CALL qx030_msgadvetencia_gb000(g_msj)
	    RETURN FALSE
	END IF
	IF t2.tsccbstat = 2 THEN
	    LET g_msj = "Cuenta deshabilitada"
	    CALL qx030_msgadvetencia_gb000(g_msj)
	    RETURN FALSE
	END IF
	RETURN TRUE
END FUNCTION

FUNCTION f5030_buscar_tscha_ts323(l_cbco,l_ncta,l_nchq)
	DEFINE	l_cbco  LIKE tscha.tschacbco,
	      	l_ncta  LIKE tscha.tschancta,
	      	l_nchq  LIKE tscha.tschanchq
        INITIALIZE t3.* TO NULL
	SELECT tschaimpo,tschacmon,tschauneg,tschastat,tschamorg
		INTO  t3.*
		FROM  tscha
	        WHERE tschacbco = l_cbco
		  AND tschancta = l_ncta
		  AND tschanchq = l_nchq
		  AND tschatchq = 2
        IF status  = NOTFOUND THEN
            RETURN FALSE
        END IF
        RETURN TRUE
END FUNCTION

FUNCTION f5040_buscar_adhuu_ts323(l_uneg)
        DEFINE  l_uneg  LIKE adhuu.adhuuuneg
        SELECT * FROM adhuu
                WHERE adhuuusrn = g_user
                  AND adhuuuneg = l_uneg
        IF status = NOTFOUND THEN
            RETURN FALSE
        END IF
        RETURN TRUE
END FUNCTION

FUNCTION f5050_buscar_cnune_ts323(l_uneg)
	DEFINE	l_uneg	LIKE cnune.cnuneuneg,
		l_desc	LIKE cnune.cnunedesc
	SELECT cnunedesc INTO l_desc
		FROM  cnune
		WHERE cnuneuneg = l_uneg
	RETURN l_desc
END FUNCTION

FUNCTION f5100_buscar_detalle_ts323()
	DEFINE	l1      RECORD LIKE tsdch.*,
	      	l_desc	CHAR(7)
	INITIALIZE p1[1].* TO NULL
	FOR i=2 TO 100
	    LET p1[i].* = p1[1].*
	END FOR
	DECLARE q_tsdch CURSOR FOR
		SELECT * FROM tsdch
			WHERE tsdchntra = t1.tsdepntra
	LET i = 0
	FOREACH q_tsdch INTO l1.*
	    LET i = i + 1
	    LET p1[i].cbco = l1.tsdchcbco
	    CALL f5010_buscar_gbcon_ts323(11,l1.tsdchcbco)
		      RETURNING p1[i].dbco,l_desc,g_flag
	    LET p1[i].ncta = l1.tsdchncta
	    LET p1[i].nchq = l1.tsdchnchq
	    LET p1[i].impt = l1.tsdchimpt
	END FOREACH
	LET max_v1 = i
END FUNCTION

###################
# RUTINAS GENERALES
###################

FUNCTION f6000_limpiar_menu_ts323()
	IF g_mtflag = 0 THEN
	    CLEAR FORM
	END IF
        INITIALIZE t1.*,g_uncc TO NULL
	INITIALIZE g_cpry,g_cprg,g_cfin TO NULL
	LET g_marca = FALSE
	INITIALIZE p1[1].* TO NULL
	FOR i=2 TO 100
	    LET p1[i].* = p1[1].*
	END FOR
	LET max_v1 = 1
	IF g_mtflag = 0 THEN
	    DELETE FROM adtmp
	END IF
END FUNCTION

FUNCTION f6050_buscar_empresa_ts323()
        SELECT * INTO t0.* FROM gbpmt
        SELECT * INTO t02.* FROM gbrne
        SELECT * INTO t03.* FROM cnpmf
        SELECT * INTO t9.* FROM tsctl
        SELECT * INTO t4.* FROM cnprm
        LET t01.* = t0.*
END FUNCTION

FUNCTION f6300_display_datos_ts323()
	DEFINE l_desc  CHAR(5)
	IF g_mtflag = 0 THEN
            DISPLAY BY NAME t1.tsdepntra,t1.tsdepndoc,t1.tsdepftra,t1.tsdepcbco,
		            t1.tsdepncta,t1.tsdepcmon,t1.tsdeptcam,t1.tsdepgls1,
			    t1.tsdepgls2,t1.tsdepgls3,t1.tsdepichq,t1.tsdepimpo
	END IF
	CALL f5010_buscar_gbcon_ts323(11,t1.tsdepcbco)
		  RETURNING g_bank,l_desc,g_flag
	CALL f5020_buscar_tsccb_ts323() RETURNING g_flag
	CALL f5010_buscar_gbcon_ts323(10,t1.tsdepmcta)
		  RETURNING g_dmct,g_amct,g_flag
	LET g_amct[5,5] = ":"
	CALL f5010_buscar_gbcon_ts323(10,t1.tsdepcmon)
		  RETURNING g_dmdp,g_amdp,g_flag
	LET g_amdp[5,5] = ":"
	IF g_mtflag = 0 THEN
 	    DISPLAY BY NAME g_bank,g_dmdp,g_amdp,g_amct
	END IF
	CALL f5100_buscar_detalle_ts323()
	IF g_mtflag = 0 THEN 
	    FOR i=1 TO 4
	        IF i <= max_v1 THEN
	            DISPLAY p1[i].* TO s1[i].*
	        ELSE
	            DISPLAY p1[i].* TO s1[i].* ATTRIBUTE(NORMAL)
	        END IF
	    END FOR
	END IF
END FUNCTION

###############
# OTRAS RUTINAS
###############

FUNCTION f7000_conv_importes_ts323(l_impi,l_cmon)
        DEFINE l_impi  LIKE cntcn.cntcnimpi,
               l_impc  LIKE cntcn.cntcnimpc,
               l_cmon  LIKE tsdep.tsdepcmon
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
