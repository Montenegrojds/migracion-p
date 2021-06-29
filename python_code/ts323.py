# PROGRAMA: ts323.4gl
"""FUNCTION f0310_calcular_totales_ts323()
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
"""

def f0310_calcular_totales_ts323():
    t1.tsdepichq = 0
    #if max_vi its not a number -> for i range(len(max_v1)):
    for i in range(max_v1):
        if p1[i].impt != None:    
            t1.tsdepichq = t1.tsdepichq + p1[i].impt
    t1.tsdepimpt = t1.tsdepichq
    t1.tsdepimpo = t1.tsdepimpt

    if  t1.tsdepcmon = 2 and  t2.tsccbcmon = 2:
        t1.tsdepimpo = f0100_redondeo_gb000(t1.tsdepimpo/t1.tsdeptcam,2) 
    elif t1.tsdepcmon = 2 and t2.tsccbcmon = 1:
        t1.tsdepimpo = f0100_redondeo_gb000(t1.tsdepimpo*t1.tsdeptcam,2)
    print(t1.tsdepichq,t1.tsdepimpo)   



def f0300_proceso_ts323():
    # DEFINE 	l_ndoc  LIKE tsdep.tsdepndoc
    while(True):
        pass







"""
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
"""


