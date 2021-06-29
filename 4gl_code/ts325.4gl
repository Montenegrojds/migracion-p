################################################################################
# PROGRAMA: ts325.4gl
# VERSION : 5.1.0
# FECHA   : 02/09/97,02/04/98,03/07/98,24,03/99
# OBJETIVO: Debitos/Abonos a Cuentas en Bancos
# AUTOR   : MDR - CCS
# COMPILAR: ts325 ts901 ts000 ts900 ad800 gb000 gb001 gb002 cn800 cn900
################################################################################
DATABASE tbsai
	GLOBALS "gbglobs.4gl"
        DEFINE  t1       RECORD LIKE tstdc.*,
		t2       RECORD LIKE tsccb.*,
                t3       RECORD LIKE tstmv.*,
                t4       RECORD LIKE iplco.*,
                t5       RECORD LIKE ippol.*,
                t6       RECORD LIKE cnprm.*,
                t7       RECORD LIKE ipctl.*,
                t9       RECORD LIKE tsctl.*,
                g_crdi          LIKE ipctl.ipctlcrdi,
		g_bank          LIKE gbcon.gbcondesc,
		g_dtmv          LIKE incon.incondesc,
		g_abre          LIKE gbcon.gbconabre,
		g_abre1         LIKE gbcon.gbconabre,
		g_crfa          LIKE iplco.iplcocrdf,
		g_mdoc          CHAR(1),
		g_etiq          CHAR(4),
		g_ddoc          CHAR(30),
		g_msg           CHAR(70),
                g_item          LIKE cntcn.cntcnitem,
	       	g_cctb          LIKE cntcn.cntcncctb,
		g_ccos		LIKE cntcn.cntcnccos,
		g_scaa          LIKE cntcn.cntcnscaa,
                g_glosa         LIKE cntcn.cntcndesc,
                g_desc          LIKE cntcn.cntcndesc,
                g_mcco          LIKE cnplc.cnplcmcco,
                g_tcon          LIKE cnplc.cnplctcon,
		g_uncc		SMALLINT,
                g_freg          LIKE tsdep.tsdepftra,
		g_cpry          LIKE tscba.tscbacpry,
		g_cprg          LIKE tscba.tscbacprg,
		g_cfin          LIKE tscba.tscbacfin,
		g_ccuf          LIKE iplco.iplcoccuf,
		g_tdse          LIKE gbcon.gbcondesc,
		cntr		SMALLINT,
                #################################
                # variables generales NO BORRAR #
                #################################
                t0            RECORD LIKE gbpmt.*,
                t01           RECORD LIKE gbrne.*,
		t02	      RECORD LIKE cnpmf.*,
                at0           RECORD LIKE gbpmt.*,
	        #---------------------------------#
	        g_nmod               CHAR(16),
	        g_titu               CHAR(33),
	        g_descmon            CHAR(20),
		g_vers	             CHAR(6),
                g_uaut               CHAR(3),
		g_spool		     CHAR(15),
	        #---------------------------------#
	        g_band               SMALLINT,
                i                    SMALLINT,
                g_flag               SMALLINT,
                g_marca              SMALLINT,
                g_user               CHAR(3),
                g_nive               SMALLINT,
                g_mgui               CHAR(1),
                g_hora               CHAR(8),
                g_fpro               DATE

MAIN DEFER INTERRUPT IF NOT f0000_open_database_gb000() THEN EXIT PROGRAM END IF
	LET g_mtflag = 0
		
        OPTIONS
        --* ON CLOSE APPLICATION CONTINUE, 
        PROMPT LINE 23,
		ERROR   LINE 24
        SET LOCK MODE TO WAIT
        # WHENEVER ERROR  CONTINUE
        OPEN FORM ts325_01 FROM "ts325a"
        DISPLAY FORM ts325_01
	LET g_fpro = TODAY
        LET g_user = arg_val(1)
        LET g_mgui = arg_val(2)
        LET g_nive = arg_val(3)
        LET g_freg = "01/01/1900"
    --* LET g_mgui = "N"
        CALL f6050_buscar_empresa_ts325()
        #-----------------------------------------------------------------------
	LET g_nmod = "TESORERIA"
	LET g_titu = "DEBITO/ABONO A CUENTA BANCARIA"
	LET g_vers = "5.1.36"
--*	LET g_vers = "6.0.0"
	CALL f6100_cabecera_gb000(t0.gbpmtnomb,g_nmod,g_titu,t0.gbpmtfdia,
				  g_vers)
        #-----------------------------------------------------------------------
	IF NOT f0300_usuario_gb000(g_user) THEN
	    LET g_msg =  "No tiene Autorizacion"
	    CALL qx031_msgadvertencia_gb000(g_msg,2)
	    EXIT PROGRAM
        END IF
	IF NOT f1000_clave_gb000(t0.gbpmtnomb,t0.gbpmtcusr,96) THEN
	    LET g_msg =  "Acceso Denegado, llame a su proveedor de Software "
	    CALL qx031_msgadvertencia_gb000(g_msg,2)
	    EXIT PROGRAM
	END IF
        CALL f7000_crear_temporal_ad800()
        CALL f8000_crear_temporal_cn800()
	CALL f7000_crear_temporal_cn001()
        CALL f0250_declarar_puntero_ts325()
	CALL f0250_declarar_puntero_cn001()
        CALL f0300_proceso_ts325()
END MAIN

#########################
# DECLARACION DE PUNTEROS
#########################

FUNCTION f0250_declarar_puntero_ts325()
	DEFINE	s1	CHAR(600)
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

FUNCTION f0300_proceso_ts325()
        DEFINE 	l_ndoc  LIKE tstdc.tstdcndoc,
	       	l_impt  LIKE tstdc.tstdcimpt,
	       	l_desc  CHAR(7),
	       	l_cdin  CHAR(40),
                l_pref  LIKE cctrn.cctrnpref,
                l_corr  LIKE cctrn.cctrncorr,
		l_cnta  LIKE cnrpl.cnrplcnta,
	       	l_flag  SMALLINT,
		l_band  SMALLINT,
	       	l_fld   SMALLINT,
               	l_key   SMALLINT,
               	l_exit  SMALLINT,
                l_freg  LIKE cpmcp.cpmcpfreg,
                l_tcof  LIKE gbhtc.gbhtctcof,
                l_tcco  LIKE gbhtc.gbhtctcco,
                l_tcve  LIKE gbhtc.gbhtctcve,
                l_ctrl  CHAR(9),
                l_msg   CHAR(40)

	WHILE TRUE
        CALL f6000_limpiar_menu_ts325()
        IF g_freg = "01/01/1900" THEN
           LET g_freg = t0.gbpmtfdia
        END IF
        INPUT BY NAME t1.tstdcntra WITHOUT DEFAULTS
		ON KEY (CONTROL-C,INTERRUPT)
                        LET int_flag = TRUE
			EXIT INPUT
                ON KEY (CONTROL-B)
                        CALL f4000_consulta_ts325()
                        IF t1.tstdcntra IS NOT NULL THEN
                            EXIT INPUT
                        END IF
	END INPUT
	IF int_flag THEN
	    RETURN
	END IF
        CALL f5000_buscar_registro_ts325()
        IF qx100_querix_gb000() THEN
            LET l_ctrl = "CONTROL-R"
            LET l_msg = " <CTRL-R> Documento Fiscal"  CLIPPED
        ELSE
            LET l_ctrl = "CONTROL-F"
            LET l_msg = " <CTRL-F> Documento Fiscal" CLIPPED
        END IF
        INPUT BY NAME t1.tstdcndoc,t1.tstdcftra,t1.tstdccbco,t1.tstdcncta,
		      t1.tstdcpref,t1.tstdccorr,t1.tstdccmon,t1.tstdcimpt,
		      t1.tstdctcam,g_mdoc      ,t1.tstdcgls1,t1.tstdcgls2,
		      t1.tstdcgls3
                WITHOUT DEFAULTS
		ON KEY (CONTROL-C,INTERRUPT)
		        LET int_flag = TRUE
			EXIT INPUT
                ON KEY (F1,CONTROL-P)
                        CALL f4000_accesos_rapidos_ad800(g_user,8,2,g_nive)
		ON KEY (CONTROL-E)
                        IF g_marca THEN
	                    IF t0.gbpmtfdia >= t1.tstdcftra THEN
				LET l_band = TRUE
 				IF g_mdoc = "F" OR g_mdoc = "B"  THEN
 				    CALL f0321_fecha_doc_fiscal_valida_gb000
 				              (t4.iplcoftra,t1.tstdcftra,FALSE)
 				              RETURNING l_band
                                END IF
                                IF l_band THEN
				    IF g_uncc THEN
				        LET l_cdin = NULL
                                        IF NOT f0330_validar_ts325() THEN
                                            CALL qx031_msgadvertencia_gb000
                                                 (g_msg,2)      
			                    LET int_flag = TRUE
		                            EXIT INPUT
                                        END IF
			                CALL f0402_autorizacion_ad800
				             (g_user,96,2,t1.tstdcimpt,
					      t1.tstdccmon,l_cdin,16,1,
					      t1.tstdcftra,162,t1.tstdcntra)
			    	              RETURNING g_uaut,g_flag
			                IF g_flag THEN
                                            IF f3000_borrar_ts325() THEN
			                        LET int_flag = TRUE
		                                EXIT INPUT
					    END IF
			                END IF
			            END IF
				ELSE
                                    LET g_msg =  "No puede revertir... Fecha ",
                                        "de Desactivacion Contable mayor ",
                                        "o igual a la del Dia"
                                    CALL qx030_msgadvetencia_gb000(g_msg)      
                                END IF
			    ELSE
				LET g_msg =  "No puede revertir por incompatibilidad ",
				      "de fechas"
				CALL qx030_msgadvetencia_gb000(g_msg)      
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
                        IF INFIELD(tstdcpref) THEN
                            CALL f0200_selec_cursor_ts900(3,0,0)
                                      RETURNING t1.tstdcpref,g_dtmv
                            DISPLAY BY NAME t1.tstdcpref,g_dtmv
                        END IF
                        IF INFIELD(tstdccmon) THEN
                            CALL f0200_selec_cursor_ts900(5,10,0)
                                      RETURNING t1.tstdccmon,g_descmon
                            DISPLAY BY NAME t1.tstdccmon,g_descmon
			    NEXT FIELD tstdccmon
                        END IF
                        IF INFIELD(tstdccorr) THEN
			    IF g_band > 0 THEN
                                CALL f0200_selec_cursor_ts901
					  (1,g_user,t1.tstdcpref)
                                          RETURNING t1.tstdccorr,t3.tstmvdesc
			    ELSE
                                CALL f0200_selec_cursor_ts900(4,t1.tstdcpref,0)
                                          RETURNING t1.tstdccorr,t3.tstmvdesc
			    END IF
                            DISPLAY BY NAME t1.tstdccorr,t3.tstmvdesc
                        END IF
		ON KEY (CONTROL-F)
		    CALL f0343_mostrar_libros_ts325(l_msg)
		    
	--* ON KEY (CONTROL-R)
	--*    CALL f0343_mostrar_libros_ts325(l_msg)    
			
			   
                ON KEY (CONTROL-T)
                        IF g_mcco = "S" AND t1.tstdcpref > 0 AND t1.tstdccorr >0
                           AND NOT g_marca THEN
                            MESSAGE " "
                            IF t1.tstdcpref = 1 OR t1.tstdcpref = 2 THEN
                                CALL f0410_proceso_unidad_negocio_cn800
                                          (t1.tstdccorr,t3.tstmvdesc,
					   t2.tsccbuneg,g_user,14,5)
                                          RETURNING g_flag
                                MESSAGE " <CTRL-T> Unidad de Negocio"
                            END IF
                        END IF
                BEFORE INPUT
                        LET l_ndoc = t1.tstdcndoc
                        LET l_exit = FALSE
			IF t1.tstdcftra IS NULL THEN
			    LET t1.tstdcftra = t0.gbpmtfdia
			    DISPLAY BY NAME t1.tstdcftra
			END IF
			IF g_marca THEN
                            #------------ Validar Unidad de Negocio -----------#
                            LET g_uncc = TRUE
                            IF g_mcco = "S" THEN
                                LET g_uncc = f5100_validar_uneg_ccos_cn800
                                                  (g_user)
                            END IF
                            IF NOT f5090_buscar_adhuu_ts325(t1.tstdcuneg) THEN
                                LET g_msg =  "Usuario no habilitado en la U/N ",
                                      t1.tstdcuneg USING "<<<<"
                                CALL qx030_msgadvetencia_gb000(g_msg)      
                                LET g_uncc = FALSE
                            END IF
			    #----------- Validar Cierre contable ------------#
                            IF t6.cnprmfdes IS NOT NULL THEN
                            	IF t1.tstdcftra <= t6.cnprmfdes THEN
				    LET g_msg =  "Periodo contable cerrado...",
                                                 " No puede modificar"
                                    CALL qx030_msgadvetencia_gb000(g_msg)
                               	    LET l_exit = TRUE
                            	END IF
			    END IF
			    #------------------------------------------------#
                            LET t0.gbpmtfdia = t1.tstdcftra
                            CALL f5010_buscar_gbhtc_ts325(t1.tstdcftra)
                                     RETURNING g_flag,l_tcof,l_tcco,l_tcve
                            IF NOT g_flag THEN
                                NEXT FIELD tstdcftra
                            END IF
                            LET t0.gbpmttcof = l_tcof
                            LET t0.gbpmttcco = l_tcco
                            LET t0.gbpmttcve = l_tcve
                          ELSE
                            LET t1.tstdcftra = g_freg
                            LET t0.gbpmtfdia = g_freg
                            DISPLAY BY NAME t1.tstdcftra
			END IF
			IF g_mdoc <> "N" THEN
			    MESSAGE l_msg
 			END IF
                AFTER FIELD tstdcndoc
			{IF l_exit THEN 
			    LET int_flag = TRUE
			    EXIT INPUT
			END IF }
                        IF g_marca THEN
                            LET t1.tstdcndoc = l_ndoc
                            LET int_flag = FALSE
                            EXIT INPUT
                        END IF
               BEFORE FIELD tstdcftra
                      LET l_freg = t1.tstdcftra
                      IF g_marca THEN
                          NEXT FIELD cpmcpuneg
                      END IF
               AFTER FIELD tstdcftra
                      IF t1.tstdcftra IS NOT NULL THEN
                          IF t1.tstdcftra < at0.gbpmtfini THEN
                              LET g_msg =  "Fecha de Gestion Pasada"
                              CALL qx030_msgadvetencia_gb000(g_msg)
                              LET t1.tstdcftra = l_freg
                              NEXT FIELD tstdcftra
                          END IF
                          IF t1.tstdcftra > at0.gbpmtfdia THEN
                              LET g_msg =  "La Fecha no puede ser Mayor ",
                                    "a la Fecha del Sistema"
                              CALL qx030_msgadvetencia_gb000(g_msg)      
                              LET t1.tstdcftra = l_freg
                              NEXT FIELD tstdcftra
                          END IF
			  #----------- Validar Cierre contable ------------#
                          IF t6.cnprmfdes IS NOT NULL THEN
                              IF t1.tstdcftra <= t6.cnprmfdes THEN
				  LET g_msg =  "Periodo contable cerrado"
				  CALL qx030_msgadvetencia_gb000(g_msg)
                                  LET t1.tstdcftra = l_freg
                                  NEXT FIELD tstdcftra
                              END IF
			  END IF
			  #------------------------------------------------#
                          IF t1.tstdcftra <> at0.gbpmtfdia THEN
                              IF t1.tstdcftra <> l_freg THEN
                                  LET l_cdin = "Fecha del Sistema: ",
                                                at0.gbpmtfdia," -- ",
                                               "Fecha Modificada: ",
                                                t1.tstdcftra
                                  CALL f0400_autorizacion_ad800
                                            (g_user,96,13,0,0,l_cdin,
                                             16,1,t1.tstdcftra)
                                          RETURNING g_uaut,g_flag
                                  IF NOT g_flag THEN
                                      LET g_msg =  "Necesita Autorizacion para ",
                                            "Modificar Fecha"
                                      CALL qx030_msgadvetencia_gb000(g_msg)      
                                      LET t1.tstdcftra = l_freg
                                      NEXT FIELD tstdcftra
                                  END IF
                              END IF
                              LET t0.gbpmtfdia = t1.tstdcftra
                              CALL f5010_buscar_gbhtc_ts325(t1.tstdcftra)
                                        RETURNING g_flag,l_tcof,l_tcco,l_tcve
                              IF NOT g_flag THEN
                                  LET t1.tstdcftra = l_freg
                                  NEXT FIELD tstdcftra
                              END IF
                              LET t0.gbpmttcof = l_tcof
                              LET t0.gbpmttcco = l_tcco
                              LET t0.gbpmttcve = l_tcve
                          ELSE
                              LET t0.* = at0.*
                          END IF
                      ELSE
                          LET t1.tstdcftra = at0.gbpmtfdia
                          LET t0.* = at0.*
                      END IF
                      LET g_freg = t1.tstdcftra
                      DISPLAY BY NAME t1.tstdcftra

                AFTER FIELD tstdccbco
                        IF t1.tstdccbco IS NULL THEN
                            NEXT FIELD tstdccbco
                        END IF
			CALL f5010_buscar_gbcon_ts325(11,t1.tstdccbco,1)
				  RETURNING g_bank,g_flag
			IF NOT g_flag THEN
			    IF qx100_querix_gb000() THEN
				    --* CALL fgl_winmessage( "Advertencia", "No existe", "exclamation" )
				ELSE 
				    LET g_msg =  "No existe"
				    CALL qx030_msgadvetencia_gb000(g_msg)
				END IF
			    NEXT FIELD tstdccbco
			END IF
			DISPLAY BY NAME g_bank
		BEFORE FIELD tstdcncta
			IF g_mcco = "S" AND t1.tstdcpref > 0 AND t1.tstdccorr >0
			THEN
			    MESSAGE " <CTRL-T> Unidad de Negocio"
			END IF
                AFTER FIELD tstdcncta
                        IF t1.tstdcncta IS NULL THEN
                            NEXT FIELD tstdcncta
                        END IF
			IF NOT f5020_buscar_tsccb_ts325() THEN
			    NEXT FIELD tstdcncta
			END IF
                        IF NOT f5090_buscar_adhuu_ts325(t2.tsccbuneg) THEN
                            LET g_msg =  "Usuario no habilitado en la U/N ",
                                  t2.tsccbuneg USING "<<<<"
                            CALL qx030_msgadvetencia_gb000(g_msg)      
                            NEXT FIELD tstdcncta
                        END IF
	                CALL f5010_buscar_gbcon_ts325(10,t2.tsccbcmon,0)
			          RETURNING g_abre1,g_flag
	                DISPLAY BY NAME g_abre1
			LET t1.tstdcuneg = t2.tsccbuneg
                BEFORE FIELD tstdcpref
                        MESSAGE " "
                        IF t1.tstdcpref > 0 THEN
                            LET l_pref = t1.tstdcpref
                            IF g_mcco = "S" THEN
                                MESSAGE " <CTRL-T> Unidad de Negocio"
                            END IF
                        ELSE
                            LET l_pref = 0
                        END IF
                AFTER FIELD tstdcpref
			IF t1.tstdcpref IS NULL THEN
			    NEXT FIELD tstdcpref
			END IF
                        IF t1.tstdcpref <> l_pref THEN
                            DELETE FROM tmptdi WHERE capl = l_pref
                        END IF
			IF t1.tstdcpref > 2 THEN
				 
				    LET g_msg =  "Valor incorrecto"
				    CALL qx030_msgadvetencia_gb000(g_msg)
				
			    
			    NEXT FIELD tstdcpref
			ELSE
			    IF t1.tstdcpref = 2 THEN
			        LET g_mdoc = "N"
				INITIALIZE t4.*,t5.*,g_etiq,g_ddoc TO NULL
			        DISPLAY BY NAME g_mdoc,g_etiq,g_ddoc
			    END IF
			END IF
			CALL f5030_buscar_tscon_ts325()
			DISPLAY BY NAME g_dtmv
			#------------------------------------------------------#
                        IF t1.tstdccorr > 0 THEN
                            IF NOT f5040_buscar_tstmv_ts325() THEN
                                LET g_mcco = NULL
                                NEXT FIELD tstdccorr
                            END IF
                            IF NOT f5070_buscar_cnplc_ts325(t3.tstmvctbl) THEN
                                LET g_msg =  "La cuenta: ",t3.tstmvctbl," del tipo ",
                                      "mov no esta definida en el Plan de ",
                                      "Cuentas"
                                CALL qx030_msgadvetencia_gb000(g_msg)      
                                NEXT FIELD tstdcpref
                            END IF
                        ELSE
                            LET g_mcco = NULL
                        END IF
                        IF g_mcco = "S" AND t1.tstdcpref <> l_pref THEN
                            IF NOT f0410_proceso_unidad_negocio_cn800
                                        (t1.tstdccorr,t3.tstmvdesc,
					 t2.tsccbuneg,g_user,14,5) THEN
                                
                                 
								    LET g_msg =  "Debe ingresar Centro de Costo"
								    CALL qx030_msgadvetencia_gb000(g_msg)
								
                                NEXT FIELD tstdcpref
                            END IF
                        END IF
                BEFORE FIELD tstdccorr
                        MESSAGE " "
                        IF t1.tstdccorr > 0 THEN
                            LET l_corr = t1.tstdccorr
                            IF g_mcco = "S" THEN
                                MESSAGE " <CTRL-T> Unidad de Negocio"
                            END IF
                        ELSE
                            LET l_corr = 0
                        END IF
                AFTER FIELD tstdccorr
                        IF t1.tstdccorr IS NULL THEN
                            NEXT FIELD tstdccorr
                        END IF
                        IF t1.tstdccorr <> l_corr THEN
                            DELETE FROM tmptdi WHERE capl = l_corr
                        END IF
                        IF NOT f5040_buscar_tstmv_ts325() THEN
                            NEXT FIELD tstdccorr
                        END IF
                        DISPLAY BY NAME t3.tstmvdesc
                        IF NOT f5070_buscar_cnplc_ts325(t3.tstmvctbl) THEN
                            LET g_msg =  "La cuenta: ",t3.tstmvctbl," del tipo mov ",
                                  "no esta definida en el Plan de Cuentas"
                            CALL qx030_msgadvetencia_gb000(g_msg)      
                            NEXT FIELD tstdccorr
                        END IF
                        IF g_mcco = "S" AND t1.tstdccorr <> l_corr THEN
                            IF NOT f0410_proceso_unidad_negocio_cn800
                                        (t1.tstdccorr,t3.tstmvdesc,
					 t2.tsccbuneg,g_user,14,5) THEN
					 			
								    LET g_msg =  "Debe ingresar Centro de Costo"
								    CALL qx030_msgadvetencia_gb000(g_msg)
								
                                
                                NEXT FIELD tstdccorr
                            END IF
                        END IF
		BEFORE FIELD tstdccmon
                        MESSAGE " "
                        IF g_mcco = "S" AND t1.tstdcpref > 0 AND t1.tstdccorr >0			THEN
                            MESSAGE " <CTRL-T> Unidad de Negocio"
                        END IF
                AFTER FIELD tstdccmon
			IF t1.tstdccmon IS NULL THEN
			    NEXT FIELD tstdccmon
			END IF
	   		CALL f5010_buscar_gbcon_ts325(10,t1.tstdccmon,1) 
				  RETURNING g_descmon,g_flag
			DISPLAY BY NAME g_descmon
	   		CALL f5010_buscar_gbcon_ts325(10,t1.tstdccmon,0) 
				  RETURNING g_abre,g_flag
			DISPLAY BY NAME g_abre
			IF NOT g_flag THEN
				 
				    LET g_msg =  "No existe"
				    CALL qx030_msgadvetencia_gb000(g_msg)
				
			    
			    NEXT FIELD tstdccmon
			END IF	
			LET t1.tstdccmoc = t2.tsccbcmon
	   		CALL f5010_buscar_gbcon_ts325(10,t1.tstdccmoc,0) 
				  RETURNING g_abre1,g_flag
			IF NOT g_flag THEN 
			    
			     
				    LET g_msg =  "No existe Moneda de Cuenta Bancaria"
				    CALL qx030_msgadvetencia_gb000(g_msg)
				
			    NEXT FIELD tstdccmon
			END IF	
		AFTER FIELD tstdcimpt
                        IF t1.tstdcimpt IS NULL OR t1.tstdcimpt <= 0 THEN
			    NEXT FIELD tstdcimpt
                        END IF
                        IF t1.tstdccmon = t1.tstdccmoc THEN
                            LET t1.tstdctcam = t0.gbpmttcof
			    LET t1.tstdcimpo = t1.tstdcimpt
			    DISPLAY BY NAME t1.tstdctcam,t1.tstdcimpo
			ELSE
			    CALL f2700_convertir_vias_ts325()
                        END IF
                AFTER FIELD tstdctcam
			IF t1.tstdctcam IS NULL OR t1.tstdctcam <= 0 THEN
			    NEXT FIELD tstdctcam
			END IF
			LET t1.tstdccmoc = t2.tsccbcmon
	   		CALL f5010_buscar_gbcon_ts325(10,t1.tstdccmoc,0) 
				  RETURNING g_abre1,g_flag
			CALL f2700_convertir_vias_ts325()
			DISPLAY BY NAME g_abre1
			IF t1.tstdcpref = 2 THEN
                            LET l_key = fgl_lastkey()
                            LET l_fld = (l_key = fgl_keyval("ESC")) OR
                                        (l_key = fgl_keyval("ACCEPT"))   OR
                                        (l_key = fgl_keyval("LEFT"))   OR
                                        (l_key = fgl_keyval("UP")) 
                            IF NOT l_fld THEN
			        NEXT FIELD tstdcgls1
		            END IF
		        END IF
                AFTER FIELD g_mdoc
                        IF g_mdoc IS NULL THEN
                            NEXT FIELD g_mdoc
                        END IF
                        IF g_mdoc NOT MATCHES "[FPBN]" THEN
                         
						    LET g_msg =  "Valor incorrecto"
						    CALL qx030_msgadvetencia_gb000(g_msg)
						 
			    
                            NEXT FIELD g_mdoc
                        END IF
                        LET l_key = fgl_lastkey()
                        LET l_fld = (l_key = fgl_keyval("ESC")) OR
                                    (l_key = fgl_keyval("ACCEPT"))   OR
                                    (l_key = fgl_keyval("LEFT"))   OR
                                    (l_key = fgl_keyval("UP")) 
                        IF NOT l_fld THEN
			    LET l_flag = FALSE
                            MESSAGE " "
			    CASE
			    WHEN g_mdoc = "F"
				 #---------------------------------------------#
                                 IF f0310_libro_de_compras_ts325() THEN
				     LET g_etiq = "No.:"
                                     LET g_ddoc = t4.iplconfac
					          USING "<<<<<<<<<<<<<<<"
                                     INITIALIZE t5.* TO NULL
				 ELSE
				 	 
					    LET g_msg =  "Debe ingresar datos de la Factura"
					    CALL qx030_msgadvetencia_gb000(g_msg)
					               
				     INITIALIZE g_etiq,g_ddoc TO NULL
			             LET l_flag = TRUE
				 END IF
				 #---------------------------------------------#
			    WHEN g_mdoc = "P"
				 #---------------------------------------------#
				 IF t5.ippolnpol IS NULL THEN
				     LET t5.ippolnomb = g_bank
				     LET t5.ippolftra = t0.gbpmtfdia
				 END IF
				 CALL f0300_input_ippol_ip001
				           (t5.*       ,t1.tstdcimpt,
					    t1.tstdccmon,t0.gbpmtiiva)
					   RETURNING t5.*
				 IF t5.ippolnpol IS NOT NULL THEN
				     LET g_etiq = "No.:"
                                     LET g_ddoc = t5.ippolnpol
                                     INITIALIZE t4.* TO NULL
				 ELSE
                                     
                      
					    LET g_msg =  "Debe ingresar datos de la Poliza"
					    CALL qx030_msgadvetencia_gb000(g_msg)
					 
				     INITIALIZE g_etiq,g_ddoc TO NULL
				     LET l_flag = TRUE
                                 END IF
				 #---------------------------------------------#
			    WHEN g_mdoc = "B"
				 #---------------------------------------------#
				 IF t4.iplcoafac IS NULL THEN
				     LET t4.iplcoprov = g_bank
                     
				     LET t4.iplcotiva = t0.gbpmtiiva
				 END IF
                                 IF t1.tstdccmon = 2 THEN
                                     LET l_impt = f0100_redondeo_gb000
                                                   (t1.tstdcimpt*t0.gbpmttcof,2)
				 ELSE
				     LET l_impt = t1.tstdcimpt
				 END IF
				 CALL f0310_input_iplco_bsp_ip001
					   (t4.*,l_impt,t1.tstdcftra,11,16)
					   RETURNING t4.*
				 IF t4.iplcoafac IS NOT NULL THEN
				     LET g_etiq = "No.:"
                                     LET g_ddoc = t4.iplcoafac CLIPPED
                                     INITIALIZE t5.* TO NULL
				 ELSE
                                     
                     
					    LET g_msg =  "Debe ingresar datos del Boleto"
					    CALL qx030_msgadvetencia_gb000(g_msg)
					              
				     INITIALIZE g_etiq,g_ddoc TO NULL
				     LET l_flag = TRUE
				 END IF
				 #---------------------------------------------#
			    WHEN g_mdoc = "N"
				 #---------------------------------------------#
			         INITIALIZE t4.*,t5.*,g_etiq,g_ddoc TO NULL
				 #---------------------------------------------#
			    END CASE
			    DISPLAY BY NAME g_etiq,g_ddoc
			    IF l_flag THEN
                                NEXT FIELD g_mdoc
			    END IF
			END IF
			MESSAGE " <CTRL-F> Documento Fiscal"
		--* MESSAGE " <CTRL-R> Documento Fiscal"
		AFTER FIELD tstdcgls1
			IF t1.tstdcpref = 2 THEN
                            LET l_key = fgl_lastkey()
                            LET l_fld = (l_key = fgl_keyval("LEFT")) OR
                                        (l_key = fgl_keyval("UP")) 
                            IF l_fld THEN
			        NEXT FIELD tstdctcam
		            END IF
		        END IF
                AFTER INPUT
                        IF t1.tstdccbco IS NULL THEN
                            NEXT FIELD tstdccbco
                        END IF
                        IF t1.tstdcncta IS NULL THEN
                            NEXT FIELD tstdcncta
                        END IF
			IF NOT f5020_buscar_tsccb_ts325() THEN
			    NEXT FIELD tstdcncta
			END IF
			IF t1.tstdcpref IS NULL THEN
			    NEXT FIELD tstdcpref
			END IF
                        IF t1.tstdccorr IS NULL THEN
                            NEXT FIELD tstdccorr
                        END IF
                        IF g_mcco = "S" THEN
                            SELECT * FROM tmptdi
                                    WHERE capl = t1.tstdccorr
                            IF status = NOTFOUND THEN
                            	
								    LET g_msg =  "Debe ingresar Unidad de Negocio"
								    CALL qx030_msgadvetencia_gb000(g_msg)
								
                                
                                NEXT FIELD tstdccorr
                            END IF
                        END IF
                        IF NOT f5040_buscar_tstmv_ts325() THEN
                            NEXT FIELD tstdccorr
                        END IF
                        IF t1.tstdcimpt IS NULL THEN
			    NEXT FIELD tstdcimpt
                        END IF
			IF t1.tstdctcam IS NULL OR t1.tstdctcam <= 0 THEN
			    NEXT FIELD tstdctcam
			END IF
                        IF g_mdoc IS NULL THEN
                            NEXT FIELD g_mdoc
                        END IF
			LET l_flag = FALSE
			CASE
			    WHEN g_mdoc = "F"
				 #---------------------------------------------#
                                 IF t4.iplconruc IS NULL THEN
				     LET l_flag = TRUE
                                 END IF
				 #---------------------------------------------#
			    WHEN g_mdoc = "P"
				 #---------------------------------------------#
				 IF t5.ippolnpol IS NULL THEN
				     LET l_flag = TRUE
				 END IF
				 #---------------------------------------------#
			    WHEN g_mdoc = "B"
				 #---------------------------------------------#
				 IF t4.iplcoafac IS NULL THEN
				     LET l_flag = TRUE
				 END IF
				 #---------------------------------------------#
                        END CASE
			IF l_flag THEN
                            NEXT FIELD g_mdoc
			END IF
			IF t1.tstdcpref = 1 THEN
			    IF NOT f5100_disponible_ts000
			               (t1.tstdccbco,t1.tstdcncta,t1.tstdcimpo)
                            THEN
			            NEXT FIELD tstdcimpt
			    END IF
			END IF
                       	#------------------------------------------------------#
                       	IF t02.cnpmfmtfc = "S" THEN
                            INITIALIZE l_cnta TO NULL
                            SELECT cnrplcnta INTO l_cnta
                                FROM cnrpl
                               WHERE cnrplcctb = t3.tstmvctbl
                            IF STATUS = NOTFOUND THEN
                            	IF NOT f0300_distribucion_flujo_caja_cn001
                                       (t1.tstdcimpo,t1.tstdccmon) THEN
                                    NEXT FIELD tstdcgls3
				END IF
			    ELSE
                                DELETE FROM tmpdfc
                                INSERT INTO tmpdfc
                                        VALUES(l_cnta,100,t1.tstdcimpo)
                            END IF
                       	END IF
                      	
                       	#------------------------------------------------------#
                        MESSAGE " "
	END INPUT
	IF int_flag THEN
	    LET int_flag = FALSE
            CONTINUE WHILE
        END IF
	IF g_marca = FALSE THEN
            IF f1000_altas_ts325() THEN
                CALL f8000_imprimir_comprobante_ts325()
            END IF
        ELSE
            CALL f8000_imprimir_comprobante_ts325()
	END IF
	END WHILE
END FUNCTION

FUNCTION f0343_mostrar_libros_ts325(l_msg)
	DEFINE l_msg  CHAR(40),
		   l_impt LIKE tstdc.tstdcimpt
	IF g_mdoc <> "N" AND t1.tstdcimpt <> 0 THEN
                            MESSAGE " "
			    CASE
			        WHEN g_mdoc = "F"
				     #-----------------------------------------#
				     IF t4.iplconruc IS NOT NULL THEN
                                         CALL f0310_libro_de_compras_ts325()
					           RETURNING g_flag
				         IF g_flag THEN
					     LET g_etiq = "No.:"
                                             LET g_ddoc = t4.iplconfac
						         USING "<<<<<<<<<<<<<<<"
				         END IF
				     END IF
				     #-----------------------------------------#
			        WHEN g_mdoc = "P"
				     #-----------------------------------------#
				     IF t5.ippolnpol IS NOT NULL THEN
				         CALL f0300_input_ippol_ip001
				                   (t5.*        ,t1.tstdcimpt,
						    t1.tstdccmon,t0.gbpmtiiva)
						   RETURNING t5.*
				         IF t5.ippolnpol IS NOT NULL THEN
					     LET g_etiq = "No.:"
                                             LET g_ddoc = t5.ippolnpol
					 END IF
				     END IF
				     #-----------------------------------------#
			        WHEN g_mdoc = "B"
				     #-----------------------------------------#
				     IF t4.iplcoafac IS NOT NULL THEN
                                         IF t1.tstdccmon = 2 THEN
                                             LET l_impt = f0100_redondeo_gb000
                                                   (t1.tstdcimpt*t0.gbpmttcof,2)
				         ELSE
				             LET l_impt = t1.tstdcimpt
				         END IF
				         CALL f0310_input_iplco_bsp_ip001
					        (t4.*,l_impt,t1.tstdcftra,11,16)
						   RETURNING t4.*
				         IF t4.iplcoafac IS NOT NULL THEN
					     LET g_etiq = "No.:"
                                             LET g_ddoc = t4.iplcoafac CLIPPED
                                         END IF
				     END IF
				     MESSAGE l_msg
				     #-----------------------------------------#
			    END CASE
	END IF
END FUNCTION
--------- sfe ---------

FUNCTION f0310_libro_de_compras_ts325()
        DEFINE 	l1      RECORD LIKE iplco.*,
		l2	RECORD LIKE iplco.*,
		l_nnit	LIKE gbpmt.gbpmtnruc,
               	l_neto  DECIMAL(14,2),
               	l_impt  DECIMAL(14,2),
               	l_mone  LIKE gbcon.gbcondesc,
               	l_abre  LIKE gbcon.gbconabre,
	       	l_tdoc  LIKE iptdc.iptdcdesc,
	       	l_tdse  LIKE iptdc.iptdcdesc,
	       	l_tcom  LIKE iptdc.iptdcdesc,
		l_modn	LIKE iplco.iplcomodn,
		l_nopr	LIKE iplco.iplconopr,
		l_ntra	LIKE iplco.iplcontra,
		l_ente	CHAR(1),
                l_key   SMALLINT,
                l_fld   SMALLINT
            
	MESSAGE " "
        LET l1.* = t4.*
        INITIALIZE l_mone,l_abre TO NULL
        
        LET int_flag = FALSE
        OPEN WINDOW w1_ts325b AT 10,1 WITH FORM "ts325b"
         	    ATTRIBUTE (FORM LINE 1,MESSAGE LINE LAST)
        INPUT BY NAME t4.iplcotcom, t4.iplcotdoc,t4.iplcotdse,
                      t4.iplconruc, t4.iplcoftra,t4.iplcoprov,
                      t4.iplconfac, t4.iplconord,t4.iplcocctl,
                      t4.iplcoccuf, t1.tstdctcam,
		      t4.iplcoimpt,t4.iplcoidsc,t4.iplcoiice,t4.iplcoiexe,l_ente
                WITHOUT DEFAULTS
                ON KEY (CONTROL-C,INTERRUPT)
                        LET int_flag = TRUE
			EXIT INPUT
			
               ON KEY (CONTROL-Y)
                       	IF INFIELD(iplcotcom) THEN
                            MESSAGE "                             "
                            CALL f0300_lectura_qr_ip006(l2.*,8)
                                RETURNING g_flag,l2.*,l_nnit
                            IF g_flag THEN
                                IF l_nnit <> t0.gbpmtnruc THEN
                                    ERROR "NIT no corresponde a la Empresa"
                                    NEXT FIELD iplconruc
                                END IF
                                LET t4.iplcoftra = l2.iplcoftra
                                LET t4.iplconruc = l2.iplconruc
                                LET t4.iplconfac = l2.iplconfac
                                LET t4.iplconord = l2.iplconord
                                LET t4.iplcocctl = l2.iplcocctl
                                LET t4.iplcoimpt = l2.iplcoimpt
                                LET t4.iplcoidsc = l2.iplcoidsc
                                LET t4.iplcoiice = l2.iplcoiice
                                LET t4.iplcoiexe = l2.iplcoiexe
                                LET t4.iplconeto = l2.iplconeto
                                INITIALIZE t4.iplcoccuf,t4.iplcotdse,g_tdse
                                        TO NULL
                                DISPLAY BY NAME t4.iplcoftra,t4.iplconruc,
                                                t4.iplconfac,t4.iplconord,
                                                t4.iplcocctl,t4.iplcoimpt,
					        t4.iplcoidsc,t4.iplcoiice,
						t4.iplcoiexe,
                                                t4.iplcoccuf,t4.iplcotdse,
                                                g_tdse
				DISPLAY t4.iplconeto TO l_neto
                            END IF
                            MESSAGE " <CTRL-Y> Lector QR"
                       	END IF
                
		{ON KEY (CONTROL-G)
			IF INFIELD(iplcotcom) THEN
                            IF t7.ipctlvsfe <= t1.tstdcftra THEN
			    MESSAGE "                             "
			    CALL f0300_lectura_qr_sfe_ip006(l2.*,11) 
				RETURNING g_flag,l2.*,l_nnit
			    IF g_flag THEN
				IF l_nnit <> t0.gbpmtnruc THEN
				    ERROR "NIT no corresponde a la Empresa"
				    NEXT FIELD cofprnomb
				END IF
				LET t4.iplcoccuf = l2.iplcoccuf
				LET t4.iplconfac = l2.iplconfac
				LET t4.iplcotdoc = l2.iplcotdoc
				LET t4.iplcotdse = l2.iplcotdse
                                INITIALIZE t4.iplconord,t4.iplcocctl TO NULL
				DISPLAY BY NAME t4.iplcoccuf,t4.iplcotdse,
						t4.iplconfac,t4.iplcotdoc,
                                                t4.iplconord,t4.iplcocctl
                                CALL f5050_buscar_iptdc_co305() 
                                     RETURNING g_flag,l_tdoc 
                                CALL f4545_buscar_gbcon_gb906(401,t4.iplcotdse)
                                RETURNING g_flag,g_tdse
                                DISPLAY BY NAME l_tdoc,g_tdse
			    END IF
			    MESSAGE " <CTRL> Y: Lector QR SFV  G:Lector QR SFE"
                            END IF
                        END IF}


		ON KEY (CONTROL-V)
                        IF INFIELD(iplcotcom) THEN
                           CALL f0200_selec_cursor_cp900(4,111)
                                   RETURNING t4.iplcotcom,l_tcom
                           DISPLAY BY NAME t4.iplcotcom,l_tcom
                           NEXT FIELD iplcotcom
                        END IF

                        IF INFIELD(iplcotdoc) THEN
			    CALL f0200_selec_cursor_ts900(21,0,0)
			              RETURNING t4.iplcotdoc,l_tdoc
                            DISPLAY BY NAME t4.iplcotdoc,l_tdoc
     			    NEXT FIELD iplcotdoc
                        END IF
                        IF INFIELD(iplcotdse) THEN
                            CALL f0200_selec_cursor_ts900(5,401,0)
                            RETURNING t4.iplcotdse,g_tdse
                            DISPLAY BY NAME t4.iplcotdse,g_tdse
                        END IF
                        IF INFIELD(iplcoccuf) THEN
                            CALL f006_ampliar_ccuf_ip906
                            (t4.iplcoccuf,14,20)
                            RETURNING g_flag,g_ccuf
                            LET t4.iplcoccuf = g_ccuf
                            DISPLAY BY NAME t4.iplcoccuf
                        END IF


                BEFORE INPUT
	                CALL f5010_buscar_gbcon_ts325(10,1,0)
			          RETURNING l_abre,g_flag
                        IF t4.iplcoiice IS NULL THEN
                            LET t4.iplcoiice = 0 
                        END IF
                        IF t4.iplcoiexe IS NULL THEN
                            LET t4.iplcoiexe = 0
                        END IF
                        IF NOT f5020_buscar_gbcon_ts325(111,t4.iplcotcom) THEN
                        END IF
                        LET l_tcom = g_desc
                        CALL f5050_buscar_iptdc_co305() RETURNING g_flag,l_tdoc
                        LET l_neto = t4.iplcoimpt - t4.iplcoidsc - t4.iplcoiice
                                     - t4.iplcoiexe
                        CALL f4545_buscar_gbcon_gb906(401,t4.iplcotdse)
                        RETURNING g_flag,g_tdse
                        IF t4.iplcotdse > 0 THEN
                            DISPLAY BY NAME g_tdse
                        END IF
                        DISPLAY BY NAME l_abre,l_tdoc,l_neto,l_tcom
			IF t4.iplcoafac IS NULL THEN
			    LET t4.iplcoafac = "0"
			END IF

                        DISPLAY BY NAME t4.iplcocctl
			IF t4.iplcoafac <> "0" THEN
                            IF t4.iplcocctl <> "0" THEN
                                LET g_msg =  "El Codigo de Control tiene que",
                                             " ser Cero"
                                CALL qx030_msgadvetencia_gb000(g_msg)
                                NEXT FIELD iplcocctl
                            END IF
                        END IF
                        DISPLAY BY NAME t4.iplcocctl
                        IF t4.iplcotdoc = 20 THEN
                            INITIALIZE t4.iplconord,t4.iplcocctl TO NULL
                            DISPLAY BY NAME t4.iplconord,t4.iplcocctl
                        END IF

                BEFORE FIELD iplcoprov
                        IF t4.iplcoprov IS NULL THEN
                            LET t4.iplcoprov = g_bank
                        END IF
                        MESSAGE " <CTRL-Y> QR SFV  <CTRL-G> QR SFE"

                AFTER FIELD iplcotcom
                        IF t4.iplcotcom IS NULL OR t4.iplcotcom = 0 THEN
                            NEXT FIELD iplcotcom
                        END IF
                        IF NOT f5020_buscar_gbcon_ts325(111,t4.iplcotcom) THEN
                            LET g_msg =  "No existe"
                            CALL qx030_msgadvetencia_gb000(g_msg)
                            NEXT FIELD iplcotcom
                        END IF
                        LET l_tcom = g_desc
                        DISPLAY BY NAME l_tcom

                AFTER FIELD iplcotdoc
                        LET l_key = fgl_lastkey()
                        LET l_fld = (l_key = fgl_keyval("LEFT"))   OR
                                    (l_key = fgl_keyval("UP"))
                        IF l_fld THEN
                            NEXT FIELD iplcotcom
                        END IF
			IF t4.iplcotdoc IS NULL THEN
			    NEXT FIELD iplcotdoc
			END IF
                        CALL f5050_buscar_iptdc_co305() RETURNING g_flag,l_tdoc
			IF NOT g_flag THEN
			    LET g_msg =  "No existe"
			    CALL qx030_msgadvetencia_gb000(g_msg)
			    NEXT FIELD iplcotdoc
			END IF
			DISPLAY BY NAME l_tdoc
                        IF t4.iplcotdoc <> 20 THEN
			    IF t4.iplcotdoc > 1 AND t4.iplcotdoc < 20 THEN
			        LET g_msg =  "Valor no permitido"
			        CALL qx030_msgadvetencia_gb000(g_msg)
			        NEXT FIELD iplcotdoc
			    END IF
			END IF
                        IF t4.iplcotdoc = 20 THEN
                            IF t7.ipctlvsfe <= t1.tstdcftra THEN
                                INITIALIZE t4.iplconord,t4.iplcocctl
                                        TO NULL
                                DISPLAY BY NAME t4.iplconord,t4.iplcocctl
                                NEXT FIELD iplcotdse
                            ELSE
                                LET g_msg =  "Facturacion en Linea no esta ",
                                             "Activa"
                                CALL qx031_msgadvertencia_gb000(g_msg,0)
                                NEXT FIELD iplcotdoc
                            END IF
                        ELSE
                            INITIALIZE t4.iplcoccuf,t4.iplcotdse,g_tdse
                                    TO NULL
                            DISPLAY BY NAME t4.iplcoccuf,t4.iplcotdse,g_tdse
                            NEXT FIELD iplconruc
                        END IF
 
                AFTER FIELD iplcotdse
                        IF t4.iplcotdse IS NULL OR t4.iplcotdse = 0 THEN
                            NEXT FIELD iplcotdse
                        END IF
                        CALL f4545_buscar_gbcon_gb906(401,t4.iplcotdse)
                        RETURNING g_flag,g_tdse
                        IF NOT g_flag THEN
                            LET g_msj = "No existe el tipo de sector"
                            CALL qx030_msgadvetencia_gb000(g_msj)
                            NEXT FIELD iplcotdse
                        END IF
                        IF t4.iplcotdse = 24 THEN
                            LET g_msj = "Tipo de sector no permitido"
                            CALL qx030_msgadvetencia_gb000(g_msj)
                            NEXT FIELD iplcotdse
                        END IF
                        DISPLAY BY NAME g_tdse

		BEFORE FIELD iplconruc
                        MESSAGE " <CTRL> Y: Lector QR SFV  G:Lector QR SFE"
                AFTER FIELD iplconruc
                        LET l_key = fgl_lastkey()
                        LET l_fld = (l_key = fgl_keyval("LEFT"))   OR
                                    (l_key = fgl_keyval("UP"))
                        IF l_fld THEN
                            IF t4.iplcotdoc = 20 THEN
                                NEXT FIELD iplcotdse
                            ELSE
                                NEXT FIELD iplcotdoc
                            END IF
                        END IF
                        IF t4.iplconruc IS NULL THEN
                            NEXT FIELD iplconruc
                        END IF
			IF t4.iplconruc IS NOT NULL THEN
			    IF NOT f0320_solo_numeros_en_char_gb000
				        (t4.iplconruc) THEN
				LET g_msg =  "Valor incorrecto"
				CALL qx030_msgadvetencia_gb000(g_msg)
				NEXT FIELD iplconruc
			    END IF
			END IF
			MESSAGE " "
                        IF g_marca THEN
                            LET t4.iplconruc = l1.iplconruc
                            LET int_flag = FALSE
                            EXIT INPUT
                        END IF

                BEFORE FIELD iplcoftra
			IF t4.iplcoftra IS NULL THEN
			    LET t4.iplcoftra = t0.gbpmtfdia
			END IF
                AFTER FIELD iplcoftra
                        IF t4.iplcoftra IS NULL THEN
                            NEXT FIELD iplcoftra
                        END IF
                        LET t4.iplcoftra = f0310_fecha_gb000(t4.iplcoftra)
			DISPLAY BY NAME t4.iplcoftra
			IF NOT f0321_fecha_doc_fiscal_valida_gb000
				    (t4.iplcoftra,t1.tstdcftra,TRUE) THEN
                             NEXT FIELD iplcoftra
                        END IF

                AFTER FIELD iplcoprov
                        IF t4.iplcoprov IS NULL THEN
                            NEXT FIELD iplcoprov
                        END IF

                AFTER FIELD iplconfac
                        LET l_key = fgl_lastkey()
                        LET l_fld = (l_key = fgl_keyval("LEFT"))   OR
                                    (l_key = fgl_keyval("UP"))
                        IF l_fld THEN
                            NEXT FIELD iplcoprov
                        END IF

                        IF t4.iplconfac IS NULL OR t4.iplconfac <= 0 THEN
                            NEXT FIELD iplconfac
                        END IF
                        IF t4.iplcotdoc = 20 THEN
                            NEXT FIELD iplcoccuf
                        ELSE
                            NEXT FIELD iplconord
                        END IF

                AFTER FIELD iplconord
                        LET l_key = fgl_lastkey()
                        LET l_fld = (l_key = fgl_keyval("LEFT"))   OR
                                    (l_key = fgl_keyval("UP"))
                        IF l_fld THEN
                            NEXT FIELD iplconfac
                        END IF
                        IF t4.iplconord > 0 AND t4.iplconord < 10  THEN
                            NEXT FIELD iplconord
                        END IF
                        IF t4.iplconord IS NULL OR t4.iplconord = 0 THEN
                            NEXT FIELD iplconord
                        END IF
                        NEXT FIELD iplcocctl

		AFTER FIELD iplcocctl 
                        LET l_key = fgl_lastkey()
                        LET l_fld = (l_key = fgl_keyval("LEFT"))   OR
                                    (l_key = fgl_keyval("UP"))
                        IF l_fld THEN
                            NEXT FIELD iplconord
                        END IF

			IF t4.iplcocctl IS NULL THEN
			    LET t4.iplcocctl = "0"
			ELSE
			    CALL f0323_guiones_cctl_gb000(t4.iplcocctl)
				RETURNING g_flag,t4.iplcocctl
			    IF NOT g_flag THEN
				LET g_msj = " Codigo de Control Incorrecto !"
				CALL qx030_msgadvetencia_gb000(g_msj)
				NEXT FIELD iplcocctl
			    END IF 
			END IF
			DISPLAY BY NAME t4.iplcocctl
                        NEXT FIELD tstdctcam
 
                AFTER FIELD iplcoccuf
                        LET l_key = fgl_lastkey()
                        LET l_fld = (l_key = fgl_keyval("LEFT"))   OR
                        (l_key = fgl_keyval("UP"))
                        IF l_fld THEN
                            NEXT FIELD iplconfac
                        END IF

                        IF t4.iplcoccuf IS NOT NULL THEN
                            IF NOT f0420_solo_hexadecimal_en_char_gb000
                                  (t4.iplcoccuf)
                            THEN
                                LET g_msj = "CUF/CAED No es Hexadecimal"
                                CALL qx030_msgadvetencia_gb000(g_msj)
                                NEXT FIELD iplcoccuf
                            END IF
                        END IF

                BEFORE FIELD tstdctcam
                        IF t1.tstdctcam IS NULL THEN
                            LET t1.tstdctcam = t0.gbpmttcof
			    DISPLAY BY NAME t1.tstdctcam
                        END IF
                AFTER FIELD tstdctcam
                        LET l_key = fgl_lastkey()
                        LET l_fld = (l_key = fgl_keyval("LEFT"))   OR
                                    (l_key = fgl_keyval("UP"))
                        IF l_fld THEN
                            IF t4.iplcotdoc = 20 THEN
                                NEXT FIELD iplcoccuf
                            ELSE
                                NEXT FIELD iplcocctl
                            END IF
                        END IF
                        IF t1.tstdctcam IS NULL OR t1.tstdctcam <= 0 THEN
                            NEXT FIELD tstdctcam
                        END IF
                BEFORE FIELD iplcoimpt
                        IF t4.iplcoimpt IS NULL THEN
                            LET t4.iplcoimpt = t1.tstdcimpt
                            IF t1.tstdccmon = 2 THEN
                                LET t4.iplcoimpt = f0100_redondeo_gb000
                                                   (t4.iplcoimpt*t1.tstdctcam,2)
                            END IF
                        END IF
                AFTER FIELD iplcoimpt
                        IF t4.iplcoimpt IS NULL OR t4.iplcoimpt <= 0 THEN
                            NEXT FIELD iplcoimpt
                        END IF
                        LET l_neto = t4.iplcoimpt - t4.iplcoidsc - t4.iplcoiice
                                     - t4.iplcoexen
                        DISPLAY BY NAME l_neto

                BEFORE FIELD iplcoidsc
                       IF t4.iplcoidsc IS NULL THEN
                           LET t4.iplcoidsc = 0
                           DISPLAY BY NAME t4.iplcoidsc
                       END IF
               AFTER FIELD iplcoidsc
                       IF t4.iplcoidsc IS NULL THEN
                           LET t4.iplcoidsc = 0
                           DISPLAY BY NAME t4.iplcoidsc
                       END IF

                       IF t4.iplcoimpt > 0 THEN
                           IF t4.iplcoidsc >= t4.iplcoimpt THEN
                               LET g_msg =  "Descuento no puede ser mayor ",
                                            "igual al importe de la factura"
                               CALL qx030_msgadvetencia_gb000(g_msg)      
                               NEXT FIELD iplcoidsc
                           END IF
                       END IF
                       LET l_neto = t4.iplcoimpt - t4.iplcoidsc
                       DISPLAY BY NAME l_neto

                AFTER FIELD iplcoiice
                        IF t4.iplcoiice IS NULL OR t4.iplcoiice < 0 THEN
                            LET t4.iplcoiice = 0
		            DISPLAY BY NAME t4.iplcoiice
                        END IF
                        LET l_neto = t4.iplcoimpt - t4.iplcoiice - t4.iplcoexen
                        DISPLAY BY NAME l_neto
                BEFORE FIELD iplcoiexe
                        IF NOT f007_validad_sector_ip906(t4.iplcotdse)
                        THEN
                            LET t4.iplcoiexe = t4.iplcoimpt
                            DISPLAY BY NAME t4.iplcoiexe
                        END IF

                AFTER FIELD iplcoiexe
                        IF t4.iplcoiexe IS NULL OR t4.iplcoiexe < 0 THEN
                            LET t4.iplcoexen = 0
		            DISPLAY BY NAME t4.iplcoiexe
                        END IF
                        LET l_neto = t4.iplcoimpt - t4.iplcoidsc - t4.iplcoiice
                                     - t4.iplcoiexe
                        DISPLAY BY NAME l_neto
                AFTER INPUT
                        IF t4.iplconfac IS NULL THEN
                            NEXT FIELD iplconfac
                        END IF
                        IF t4.iplcoccuf IS NOT NULL THEN
                            IF NOT f0420_solo_hexadecimal_en_char_gb000
                                  (t4.iplcoccuf)
                            THEN
                                LET g_msj = "CUF/CAED No es Hexadecimal"
                                CALL qx030_msgadvetencia_gb000(g_msj)
                                NEXT FIELD iplcoccuf
                            END IF
                        END IF
                        IF t4.iplcotdoc IS NULL THEN
                            NEXT FIELD iplcotdoc
                        END IF
                        IF t4.iplcotdoc = 20 THEN
                            IF t4.iplcotdse IS NULL OR t4.iplcotdse = 0 THEN
                                NEXT FIELD iplcotdse
                            END IF
                        END IF
                        IF t4.iplcoftra IS NULL THEN
                            NEXT FIELD iplcoftra
                        END IF
                        IF t4.iplcoprov IS NULL THEN
                            NEXT FIELD iplcoftra
                        END IF
                        IF t4.iplcocctl IS NULL THEN
			    LET t4.iplcocctl = "0"
                        END IF
                        IF t4.iplcotcom IS NULL OR t4.iplcotcom = 0 THEN
                            NEXT FIELD iplcotcom
                        END IF
                        IF t4.iplcotdoc = 20 THEN
                            IF t4.iplcotdse IS NULL THEN
			        NEXT FIELD iplcotdse
                            END IF
                        ELSE
                            IF t4.iplconord > 0 AND t4.iplconord < 10  THEN
                                NEXT FIELD iplconord
                            END IF
                            IF t4.iplconord IS NULL OR t4.iplconord = 0 THEN
                                NEXT FIELD iplconord
                            END IF
                        END IF
                        IF t4.iplcoccuf IS NOT NULL THEN
                            IF NOT f0420_solo_hexadecimal_en_char_gb000
                                  (t4.iplcoccuf)
                            THEN
                                LET g_msj = "CUF/CAED No es Hexadecimal"
                                CALL qx030_msgadvetencia_gb000(g_msj)
                                NEXT FIELD iplcoccuf
                            END IF
                        END IF
                        IF t1.tstdctcam IS NULL THEN
                            NEXT FIELD tstdctcam
                        END IF
                        IF t4.iplcoimpt IS NULL THEN
                            NEXT FIELD iplcoimpt
                        END IF
                        IF t4.iplcoiice IS NULL THEN
                            LET t4.iplcoiice = 0
                        END IF
                        IF t4.iplcoiexe IS NULL THEN
                            LET t4.iplcoiexe = 0
                        END IF
                        IF NOT f007_validad_sector_ip906(t4.iplcotdse)
                        THEN
                            LET t4.iplcoiexe = t4.iplcoimpt
                            DISPLAY BY NAME t4.iplcoiexe
                        END IF

                        IF t4.iplcoimpt - t4.iplcoidsc - t4.iplcoiice 
                                        - t4.iplcoiexe < 0 THEN
                            LET g_msg =  "Valores incorrectos"
                            CALL qx030_msgadvetencia_gb000(g_msg)
                            NEXT FIELD iplcoimpt
                        END IF
                        #---------------- Control del importe -----------------#
                        LET l_impt = t1.tstdcimpt
                        IF t1.tstdccmon = 2 THEN
                            LET l_impt = f0100_redondeo_gb000
					      (l_impt*t1.tstdctcam,2)
                        END IF
                        IF t4.iplcoimpt - t4.iplcoidsc > l_impt 
			    THEN
                            LET g_msg =  "Valor incorrecto"
                            CALL qx030_msgadvetencia_gb000(g_msg)
                            NEXT FIELD iplcoimpt
                        END IF
                        #------------------------------------------------------#
                        IF t4.iplcotdoc = 20 THEN
			    SELECT iplcomodn,iplconopr,iplcontra
			      INTO l_modn,l_nopr,l_ntra
			      FROM iplco
			     WHERE iplconruc = t4.iplconruc 
                               AND iplconord = YEAR(t4.iplcoftra)
			       AND iplconfac = t4.iplconfac
			       AND iplcotdoc = t4.iplcotdoc
                        ELSE
			    SELECT iplcomodn,iplconopr,iplcontra
			      INTO l_modn,l_nopr,l_ntra
			      FROM iplco
			     WHERE iplconruc = t4.iplconruc 
                               AND iplconord = t4.iplconord
			       AND iplconfac = t4.iplconfac
			       AND iplcotdoc = t4.iplcotdoc
                        END IF
			IF STATUS = 0 THEN
			    IF g_marca = FALSE THEN
				LET g_msg =  "Factura ya fue Registrada"
				CALL qx031_msgadvertencia_gb000(g_msg,2)
				NEXT FIELD iplconfac
			    ELSE
				IF NOT (l_modn=96 AND l_nopr=t1.tstdcntra AND
					l_ntra=t1.tstdcntra) THEN
				    LET g_msg =  "Factura ya fue Registrada"
				    CALL qx031_msgadvertencia_gb000(g_msg,2)
				    NEXT FIELD iplconfac
				END IF
			    END IF
			END IF
                        #------------------------------------------------------#
	END INPUT
	CLOSE WINDOW w1_ts325b
	IF int_flag THEN
	    LET int_flag = FALSE
            LET t4.* = l1.*
            IF t4.iplconruc IS  NULL THEN
                RETURN FALSE
            END IF
	END IF
        IF t4.iplcotdoc = 20 THEN
            IF LENGTH(g_ccuf) > 50 THEN
                LET t4.iplcoccuf = g_ccuf
            END IF
            LET t4.iplconord = YEAR(t4.iplcoftra)
        END IF

	LET t4.iplcotiva = t0.gbpmtiiva
	LET t4.iplconeto = t4.iplcoimpt - t4.iplcoidsc - t4.iplcoiice 
                          - t4.iplcoiexe
        IF NOT f007_validad_sector_ip906(t4.iplcotdse)
        THEN
            LET t4.iplcotiva = 0
        END IF
	LET t4.iplcocrdf = t4.iplconeto * (t4.iplcotiva / 100)
        LET t4.iplcocrdf = f0100_redondeo_gb000(t4.iplcocrdf,2)
        RETURN TRUE
END FUNCTION
------- fin sfe -------
--------------------------- sin sfe --------------------------
{
FUNCTION f0310_libro_de_compras_ts325()
        DEFINE 	l1      RECORD LIKE iplco.*,
		l2	RECORD LIKE iplco.*,
		l_nnit	LIKE gbpmt.gbpmtnruc,
               	l_neto  DECIMAL(14,2),
               	l_impt  DECIMAL(14,2),
               	l_mone  LIKE gbcon.gbcondesc,
               	l_abre  LIKE gbcon.gbconabre,
	       	l_tdoc  LIKE iptdc.iptdcdesc,
	       	l_tcom  LIKE iptdc.iptdcdesc,
		l_modn	LIKE iplco.iplcomodn,
		l_nopr	LIKE iplco.iplconopr,
		l_ntra	LIKE iplco.iplcontra,
		l_ente	CHAR(1)
            
	MESSAGE " "
        LET l1.* = t4.*
        INITIALIZE l_mone,l_abre TO NULL
        
        LET int_flag = FALSE
        OPEN WINDOW w1_ts325b AT 10,1 WITH FORM "ts325b"
         	    ATTRIBUTE (FORM LINE 1,MESSAGE LINE LAST)
        INPUT BY NAME t4.iplcotcom,t4.iplconruc,t4.iplconfac,t4.iplconord,
                      t4.iplcotdoc,
		      t4.iplcoftra,t4.iplcocctl,t4.iplcoprov,t1.tstdctcam,
		      t4.iplcoimpt,t4.iplcoidsc,t4.iplcoiice,t4.iplcoiexe,l_ente
                WITHOUT DEFAULTS
                ON KEY (CONTROL-C,INTERRUPT)
                        LET int_flag = TRUE
			EXIT INPUT
			
               ON KEY (CONTROL-Y)
                       	IF INFIELD(iplconruc) THEN
                            MESSAGE "                             "
                            CALL f0300_lectura_qr_ip006(l2.*,7)
                                RETURNING g_flag,l2.*,l_nnit
                            IF g_flag THEN
                                IF l_nnit <> t0.gbpmtnruc THEN
                                    ERROR "NIT no corresponde a la Empresa"
                                    NEXT FIELD iplconruc
                                END IF
                                LET t4.iplcoftra = l2.iplcoftra
                                LET t4.iplconruc = l2.iplconruc
                                LET t4.iplconfac = l2.iplconfac
                                LET t4.iplconord = l2.iplconord
                                LET t4.iplcocctl = l2.iplcocctl
                                LET t4.iplcoimpt = l2.iplcoimpt
                                LET t4.iplcoidsc = l2.iplcoidsc
                                LET t4.iplcoiice = l2.iplcoiice
                                LET t4.iplcoiexe = l2.iplcoiexe
                                LET t4.iplconeto = l2.iplconeto
                                DISPLAY BY NAME t4.iplcoftra,t4.iplconruc,
                                                t4.iplconfac,t4.iplconord,
                                                t4.iplcocctl,t4.iplcoimpt,
					        t4.iplcoidsc,t4.iplcoiice,
						t4.iplcoiexe
				DISPLAY t4.iplconeto TO l_neto
                            END IF
                            MESSAGE " <CTRL-Y> Lector QR"
                       	END IF
		ON KEY (CONTROL-V)
                        IF INFIELD(iplcotcom) THEN
                           CALL f0200_selec_cursor_cp900(4,111)
                                   RETURNING t4.iplcotcom,l_tcom
                           DISPLAY BY NAME t4.iplcotcom,l_tcom
                           NEXT FIELD iplcotcom
                        END IF

                        IF INFIELD(iplcotdoc) THEN
			    CALL f0200_selec_cursor_ts900(21,0,0)
			              RETURNING t4.iplcotdoc,l_tdoc
                            DISPLAY BY NAME t4.iplcotdoc,l_tdoc
     			    NEXT FIELD iplcotdoc
                        END IF
                BEFORE INPUT
	                CALL f5010_buscar_gbcon_ts325(10,1,0)
			          RETURNING l_abre,g_flag
                        IF t4.iplcoiice IS NULL THEN
                            LET t4.iplcoiice = 0 
                        END IF
                        IF t4.iplcoiexe IS NULL THEN
                            LET t4.iplcoiexe = 0
                        END IF
                        IF NOT f5020_buscar_gbcon_ts325(111,t4.iplcotcom) THEN
                        END IF
                        LET l_tcom = g_desc
                        CALL f5050_buscar_iptdc_co305() RETURNING l_tdoc,g_flag
                        LET l_neto = t4.iplcoimpt - t4.iplcoidsc - t4.iplcoiice
                                     - t4.iplcoiexe
                        DISPLAY BY NAME l_abre,l_tdoc,l_neto,l_tcom
			IF t4.iplcoafac IS NULL THEN
			    LET t4.iplcoafac = "0"
			END IF
                AFTER FIELD iplcotcom
                        IF t4.iplcotcom IS NULL OR t4.iplcotcom = 0 THEN
                            NEXT FIELD iplcotcom
                        END IF
                        IF NOT f5020_buscar_gbcon_ts325(111,t4.iplcotcom) THEN
                            LET g_msg =  "No existe"
                            CALL qx030_msgadvetencia_gb000(g_msg)
                            NEXT FIELD iplcotcom
                        END IF
                        LET l_tcom = g_desc
                        DISPLAY BY NAME l_tcom
		BEFORE FIELD iplconruc
			MESSAGE " <CTRL-Y> Lector QR"
                AFTER FIELD iplconruc
                        IF t4.iplconruc IS NULL THEN
                            NEXT FIELD iplconruc
                        END IF
			IF t4.iplconruc IS NOT NULL THEN
			    IF NOT f0320_solo_numeros_en_char_gb000
				        (t4.iplconruc) THEN
				LET g_msg =  "Valor incorrecto"
				CALL qx030_msgadvetencia_gb000(g_msg)
				NEXT FIELD iplconruc
			    END IF
			END IF
			MESSAGE " "
                        IF g_marca THEN
                            LET t4.iplconruc = l1.iplconruc
                            LET int_flag = FALSE
                            EXIT INPUT
                        END IF
                AFTER FIELD iplconfac
                        IF t4.iplconfac IS NULL OR t4.iplconfac <= 0 THEN
                            NEXT FIELD iplconfac
                        END IF
                AFTER FIELD iplconord
                        IF t4.iplconord IS NULL OR t4.iplconord <= 0 THEN
                            NEXT FIELD iplconord
                        END IF
                AFTER FIELD iplcotdoc
			IF t4.iplcotdoc IS NULL THEN
			    NEXT FIELD iplcotdoc
			END IF
                        CALL f5050_buscar_iptdc_co305() RETURNING l_tdoc,g_flag
			IF NOT g_flag THEN
			    LET g_msg =  "No existe"
			    CALL qx030_msgadvetencia_gb000(g_msg)
			    NEXT FIELD iplcotdoc
			END IF
			DISPLAY BY NAME l_tdoc
			IF t4.iplcotdoc > 1 AND t4.iplcotdoc < 20 THEN
			    LET g_msg =  "Valor no permitido"
			    CALL qx030_msgadvetencia_gb000(g_msg)
			    NEXT FIELD iplcotdoc
			END IF
                BEFORE FIELD iplcoftra
			IF t4.iplcoftra IS NULL THEN
			    LET t4.iplcoftra = t0.gbpmtfdia
			END IF
                AFTER FIELD iplcoftra
                        IF t4.iplcoftra IS NULL THEN
                            NEXT FIELD iplcoftra
                        END IF
                        LET t4.iplcoftra = f0310_fecha_gb000(t4.iplcoftra)
			DISPLAY BY NAME t4.iplcoftra
			IF NOT f0321_fecha_doc_fiscal_valida_gb000
				    (t4.iplcoftra,t1.tstdcftra,TRUE) THEN
                                NEXT FIELD iplcoftra
                        END IF
                AFTER FIELD iplcocctl
			IF t4.iplcocctl IS NULL THEN
			    LET t4.iplcocctl = "0"
			ELSE
			    CALL f0323_guiones_cctl_gb000(t4.iplcocctl)
				RETURNING g_flag,t4.iplcocctl
			    IF NOT g_flag THEN
				LET g_msg =  "Codigo de Control Incorrecto !!"
				CALL qx030_msgadvetencia_gb000(g_msg)
				NEXT FIELD iplcocctl
			    END IF 
			END IF
                        DISPLAY BY NAME t4.iplcocctl
			IF t4.iplcoafac <> "0" THEN
                            IF t4.iplcocctl <> "0" THEN
                                LET g_msg =  "El Codigo de Control tiene que ser Cero"
                                CALL qx030_msgadvetencia_gb000(g_msg)
                                NEXT FIELD iplcocctl
                            END IF
                        END IF
                        DISPLAY BY NAME t4.iplcocctl
                BEFORE FIELD iplcoprov
                        IF t4.iplcoprov IS NULL THEN
                            LET t4.iplcoprov = g_bank
                        END IF
                AFTER FIELD iplcoprov
                        IF t4.iplcoprov IS NULL THEN
                            NEXT FIELD iplcoprov
                        END IF
                BEFORE FIELD tstdctcam
                        IF t1.tstdctcam IS NULL THEN
                            LET t1.tstdctcam = t0.gbpmttcof
			    DISPLAY BY NAME t1.tstdctcam
                        END IF
                AFTER FIELD tstdctcam
                        IF t1.tstdctcam IS NULL OR t1.tstdctcam <= 0 THEN
                            NEXT FIELD tstdctcam
                        END IF
                BEFORE FIELD iplcoimpt
                        IF t4.iplcoimpt IS NULL THEN
                            LET t4.iplcoimpt = t1.tstdcimpt
                            IF t1.tstdccmon = 2 THEN
                                LET t4.iplcoimpt = f0100_redondeo_gb000
                                                   (t4.iplcoimpt*t1.tstdctcam,2)
                            END IF
                        END IF
                AFTER FIELD iplcoimpt
                        IF t4.iplcoimpt IS NULL OR t4.iplcoimpt <= 0 THEN
                            NEXT FIELD iplcoimpt
                        END IF
                        LET l_neto = t4.iplcoimpt - t4.iplcoidsc - t4.iplcoiice
                                     - t4.iplcoexen
                        DISPLAY BY NAME l_neto
                BEFORE FIELD iplcoidsc
                       IF t4.iplcoidsc IS NULL THEN
                           LET t4.iplcoidsc = 0
                           DISPLAY BY NAME t4.iplcoidsc
                       END IF
               AFTER FIELD iplcoidsc
                       IF t4.iplcoidsc IS NULL THEN
                           LET t4.iplcoidsc = 0
                           DISPLAY BY NAME t4.iplcoidsc
                       END IF
                       IF t4.iplcoimpt > 0 THEN
                           IF t4.iplcoidsc >= t4.iplcoimpt THEN
                               LET g_msg =  "Descuento no puede ser mayor igual",
                                     " al importe de la factura"
                               CALL qx030_msgadvetencia_gb000(g_msg)      
                               NEXT FIELD iplcoidsc
                           END IF
                       END IF
                       LET l_neto = t4.iplcoimpt - t4.iplcoidsc
                       DISPLAY BY NAME l_neto

                AFTER FIELD iplcoiice
                        IF t4.iplcoiice IS NULL OR t4.iplcoiice < 0 THEN
                            LET t4.iplcoiice = 0
		            DISPLAY BY NAME t4.iplcoiice
                        END IF
                        LET l_neto = t4.iplcoimpt - t4.iplcoiice - t4.iplcoexen
                        DISPLAY BY NAME l_neto
                AFTER FIELD iplcoiexe
                        IF t4.iplcoiexe IS NULL OR t4.iplcoiexe < 0 THEN
                            LET t4.iplcoexen = 0
		            DISPLAY BY NAME t4.iplcoiexe
                        END IF
                        LET l_neto = t4.iplcoimpt - t4.iplcoidsc - t4.iplcoiice
                                     - t4.iplcoiexe
                        DISPLAY BY NAME l_neto
                AFTER INPUT
                        IF t4.iplconfac IS NULL THEN
                            NEXT FIELD iplconfac
                        END IF
                        IF t4.iplconord IS NULL THEN
                            NEXT FIELD iplconord
                        END IF
                        IF t4.iplcotdoc IS NULL THEN
                            NEXT FIELD iplcotdoc
                        END IF
                        IF t4.iplcoftra IS NULL THEN
                            NEXT FIELD iplcoftra
                        END IF
                        IF t4.iplcoprov IS NULL THEN
                            NEXT FIELD iplcoftra
                        END IF
                        IF t4.iplcocctl IS NULL THEN
			    LET t4.iplcocctl = "0"
                        END IF
                        IF t4.iplcotcom IS NULL OR t4.iplcotcom = 0 THEN
                            NEXT FIELD iplcotcom
                        END IF
                        IF t1.tstdctcam IS NULL THEN
                            NEXT FIELD tstdctcam
                        END IF
                        IF t4.iplcoimpt IS NULL THEN
                            NEXT FIELD iplcoimpt
                        END IF
                        IF t4.iplcoiice IS NULL THEN
                            LET t4.iplcoiice = 0
                        END IF
                        IF t4.iplcoexen IS NULL THEN
                            LET t4.iplcoexen = 0
                        END IF
                        IF t4.iplcoimpt - t4.iplcoidsc - t4.iplcoiice 
                                        - t4.iplcoexen <= 0 THEN
                            LET g_msg =  "Valores incorrectos"
                            CALL qx030_msgadvetencia_gb000(g_msg)
                            NEXT FIELD iplcoimpt
                        END IF
                        #---------------- Control del importe -----------------#
                        LET l_impt = t1.tstdcimpt
                        IF t1.tstdccmon = 2 THEN
                            LET l_impt = f0100_redondeo_gb000
					      (l_impt*t1.tstdctcam,2)
                        END IF
                        IF t4.iplcoimpt - t4.iplcoidsc > l_impt 
			    THEN
                            LET g_msg =  "Valor incorrecto"
                            CALL qx030_msgadvetencia_gb000(g_msg)
                            NEXT FIELD iplcoimpt
                        END IF
                        #------------------------------------------------------#
			SELECT iplcomodn,iplconopr,iplcontra
				INTO l_modn,l_nopr,l_ntra
				FROM  iplco
				WHERE iplconord = t4.iplconord
				  AND iplconfac = t4.iplconfac
			IF status = 0 THEN
			    IF g_marca = FALSE THEN
				LET g_msg =  "Factura ya fue Registrada"
				CALL qx030_msgadvetencia_gb000(g_msg)
				NEXT FIELD iplconfac
			    ELSE
				IF NOT (l_modn=96 AND l_nopr=t1.tstdcntra AND
					l_ntra=t1.tstdcntra) THEN
				    LET g_msg =  "Factura ya fue Registrada"
				    CALL qx030_msgadvetencia_gb000(g_msg)
				    NEXT FIELD iplconfac
				END IF
			    END IF
			END IF
                        #------------------------------------------------------#
	END INPUT
	CLOSE WINDOW w1_ts325b
	IF int_flag THEN
	    LET int_flag = FALSE
            LET t4.* = l1.*
            IF t4.iplconruc IS  NULL THEN
                RETURN FALSE
            END IF
	END IF
	LET t4.iplconeto = t4.iplcoimpt - t4.iplcoidsc - t4.iplcoiice 
                          - t4.iplcoiexe
	LET t4.iplcotiva = t0.gbpmtiiva
	LET t4.iplcocrdf = t4.iplconeto * (t4.iplcotiva / 100)
        LET t4.iplcocrdf = f0100_redondeo_gb000(t4.iplcocrdf,2)
        RETURN TRUE
END FUNCTION
}

------------------------- fin sin sfe --------------------------

###################
# ALTA DE REGISTROS
###################

FUNCTION f1010_altas_documento_fiscal_ts325()
	DEFINE	l_flag	SMALLINT
	LET l_flag = FALSE
	CASE
	    WHEN g_mdoc = "F" 
                 #-------------------------------------------------------------#
	         LET t4.iplcomodn = 96
	         LET t4.iplcoexen = t4.iplcoiexe + t4.iplcoidsc

	         LET t4.iplconopr = t1.tstdcntra
	         LET t4.iplcontra = t1.tstdcntra
		 LET t4.iplcouneg = t1.tstdcuneg
	         LET t4.iplcouser = t1.tstdcuser
	         LET t4.iplcohora = t1.tstdchora
	         LET t4.iplcofpro = t1.tstdcfpro
	         LET t4.iplcocesp = 0

		 #-------------------------------------------------------------#
		 INITIALIZE cntr TO NULL
                 IF t4.iplcotdoc = 20 THEN
		     SELECT COUNT(*) INTO cntr
			    FROM iplco
		      WHERE iplconruc = t4.iplconruc 
                        AND iplconord = YEAR(t4.iplcoftra)
		        AND iplconfac = t4.iplconfac
		        AND iplcotdoc = t4.iplcotdoc
                 ELSE
		     SELECT COUNT(*) INTO cntr
			    FROM iplco
		      WHERE iplconruc = t4.iplconruc 
                        AND iplconord = t4.iplconord
		        AND iplconfac = t4.iplconfac
		        AND iplcotdoc = t4.iplcotdoc
                 END IF
		 IF cntr > 0 THEN
		     LET g_msg =  "Factura ya fue registrado"
		     CALL qx030_msgadvetencia_gb000(g_msg)
		     LET l_flag = TRUE
		 END IF
		 #-------------------------------------------------------------#
	         INSERT INTO iplco VALUES (t4.*)
                 IF NOT f0500_error_gb000(status,"iplco") THEN
			 LET l_flag = TRUE
                 END IF
	         #-------------------------------------------------------------#
	    WHEN g_mdoc = "P" 
	         #-------------------------------------------------------------#
	         LET t5.ippolmorg = 96
	         LET t5.ippolnopr = t1.tstdcntra
	         LET t5.ippoltorg = t1.tstdcntra
		 LET t5.ippoluneg = t1.tstdcuneg
	         LET t5.ippoluser = t1.tstdcuser
	         LET t5.ippolhora = t1.tstdchora
	         LET t5.ippolfpro = t1.tstdcfpro
		 IF NOT f1000_altas_ippol_ip001(t5.*) THEN
			 LET l_flag = TRUE
		 END IF
	         #-------------------------------------------------------------#
	    WHEN g_mdoc = "B" 
	         #-------------------------------------------------------------#
	         LET t4.iplcomodn = 96
	         LET t4.iplcoexen = t4.iplcoiexe + t4.iplcoidsc
	         LET t4.iplconopr = t1.tstdcntra
	         LET t4.iplcontra = t1.tstdcntra
		 LET t4.iplcouneg = t1.tstdcuneg
	         LET t4.iplcouser = t1.tstdcuser
	         LET t4.iplcohora = t1.tstdchora
	         LET t4.iplcofpro = t1.tstdcfpro
	         --LET t4.iplcotcom = 0
	         LET t4.iplcocesp = 0

		 IF NOT f1010_altas_iplco_bsp_ip001(t4.*) THEN
			 LET l_flag = TRUE
		 END IF
	         #-------------------------------------------------------------#
	END CASE
	IF l_flag THEN
	    RETURN FALSE
	END IF
	RETURN TRUE
END FUNCTION

###########################
# MODIFICACION DE REGISTROS
###########################

FUNCTION f2700_convertir_vias_ts325()
	IF t1.tstdccmon = 1 AND t1.tstdccmoc = 2 THEN
	    LET t1.tstdcimpo = t1.tstdcimpt / t1.tstdctcam
	    LET t1.tstdcimpo = f0100_redondeo_gb000(t1.tstdcimpo,2)
	END IF
	IF t1.tstdccmon = 2 AND t1.tstdccmoc = 1 THEN
	    LET t1.tstdcimpo = t1.tstdcimpt * t1.tstdctcam
	    LET t1.tstdcimpo = f0100_redondeo_gb000(t1.tstdcimpo,2)
	END IF
        DISPLAY BY NAME t1.tstdcimpo
END FUNCTION

##################
# BORRAR REGISTROS
##################

FUNCTION f0330_validar_ts325()

        IF t1.tstdcmorg <> 96 THEN
	    LET g_msg =  "Transaccion generada por otro Modulo...  ",
                         "No puede revertir"
            RETURN FALSE
        END IF
        #----------------------------------------------------------------------#
        IF t2.tsccbuneg <> t1.tstdcuneg THEN
            LET g_msg =  "No puede revertir... La cuenta bancaria ha ",
                         "cambiado de U/N"
            RETURN FALSE
        END IF
        #----------------- Validar Cierre Contable ----------------------------#
        IF t6.cnprmfdes IS NOT NULL THEN
            IF t1.tstdcftra <= t6.cnprmfdes THEN
		LET g_msg =  "Periodo contable cerrado... No ",
                             "puede revertir"
            	RETURN FALSE
            END IF
	END IF
        #----------------------------------------------------------------------#
	### Validar Notas de Debito
        LET cntr = 0
	SELECT COUNT(*) INTO cntr
		FROM  ipnta
		WHERE ipntamoro = 96
		  AND ipntatoro = t1.tstdcntra
		  AND ipntastat = 0
	IF cntr > 0 THEN
	    LET g_msg =  "Transaccion con Notas de Debito"
	    RETURN FALSE
	END IF
        RETURN TRUE	
END FUNCTION

###################
# CONSULTA DE DATOS
###################

FUNCTION f4000_consulta_ts325()
        DEFINE query_1 CHAR(200),
               s1      CHAR(200)
        CLEAR FORM
        MESSAGE "Deme el criterio de seleccion y presione <ESC>"
        CONSTRUCT query_1 ON tstdcntra,tstdcndoc,tstdcftra,tstdccbco,
			     tstdcncta,tstdcpref,tstdccorr
                        FROM tstdcntra,tstdcndoc,tstdcftra,tstdccbco,
			     tstdcncta,tstdcpref,tstdccorr
        IF int_flag THEN
            LET int_flag = FALSE
            CLEAR FORM
            LET t1.tstdcntra = NULL
            DISPLAY BY NAME t1.tstdcntra
            MESSAGE " "
            RETURN
        END IF
        MESSAGE " "
        LET s1 = "SELECT * FROM tstdc WHERE ",query_1 CLIPPED,
                 " AND tstdcpref < 3 AND tstdcmrcb = 0 ORDER BY tstdcntra"
        PREPARE tstdc_s FROM s1
        DECLARE tstdc_set SCROLL CURSOR FOR tstdc_s
        OPEN    tstdc_set
        FETCH FIRST tstdc_set INTO t1.*
        IF status = NOTFOUND THEN
            LET g_msg =  "REGISTRO NO ENCONTRADO"
            CALL qx030_msgadvetencia_gb000(g_msg)
            CLEAR FORM
            LET t1.tstdcntra = NULL
            DISPLAY BY NAME t1.tstdcntra
            RETURN
        END IF
        CALL f6300_display_datos_ts325()
        MENU "CONSULTAR"
        COMMAND "Anterior" " "
                FETCH PREVIOUS tstdc_set INTO t1.*
                IF status = NOTFOUND THEN
                        LET g_msg =  "PRIMER REGISTRO"
                        CALL qx030_msgadvetencia_gb000(g_msg)
                        FETCH FIRST tstdc_set INTO t1.*
                END IF
                CALL f6300_display_datos_ts325()
        COMMAND "Siguiente" " "
                FETCH NEXT tstdc_set INTO t1.*
                IF status = NOTFOUND THEN
                        LET g_msg =  "ULTIMO REGISTRO"
                        CALL qx030_msgadvetencia_gb000(g_msg)
                        FETCH LAST tstdc_set INTO t1.*
                END IF
                CALL f6300_display_datos_ts325()
        COMMAND "Primero" " "
                FETCH FIRST tstdc_set INTO t1.*
                CALL f6300_display_datos_ts325()
        COMMAND "Ultimo" " "
                FETCH LAST tstdc_set INTO t1.*
                CALL f6300_display_datos_ts325()
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

FUNCTION f5000_buscar_registro_ts325()
        SELECT * INTO t1.*
                FROM  tstdc
                WHERE tstdcntra = t1.tstdcntra
                  AND tstdcpref < 3
                  AND tstdcmrcb = 0
	IF status = NOTFOUND THEN
            LET t1.tstdcntra = NULL
            DISPLAY BY NAME t1.tstdcntra
            RETURN
	END IF
        LET g_marca = TRUE
        CALL f6300_display_datos_ts325()
END FUNCTION

FUNCTION f5010_buscar_gbcon_ts325(l_pfij,l_corr,band)
	DEFINE 	l_pfij  LIKE gbcon.gbconpfij,
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
FUNCTION f5020_buscar_gbcon_ts325(l_pfij,l_corr)
	DEFINE 	l_pfij  LIKE gbcon.gbconpfij,
	       	l_corr  LIKE gbcon.gbconcorr,
	       	l_desc  LIKE gbcon.gbcondesc,
	       	l_abre  LIKE gbcon.gbconabre,
	       	band    SMALLINT
	SELECT gbcondesc INTO g_desc
		FROM  gbcon
		WHERE gbconpfij = l_pfij
		  AND gbconcorr = l_corr
		  AND gbconcorr > 0
	IF status = NOTFOUND THEN
	    RETURN FALSE
	END IF
	RETURN TRUE
END FUNCTION

FUNCTION f5010_buscar_gbhtc_ts325(l_fech)
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
       LET g_msg =  "No puede recuperar los Tipos de Cambio para la fecha: ",l_fech
       CALL qx030_msgadvetencia_gb000(g_msg)
       CLOSE q_gbhtc
       RETURN FALSE,0,0,0
   END IF
   CLOSE q_gbhtc
   RETURN TRUE,l_tcof,l_tcco,l_tcve
END FUNCTION

FUNCTION f5020_buscar_tsccb_ts325()
	INITIALIZE t2.* TO NULL
	SELECT * INTO t2.*
	        FROM  tsccb
	        WHERE tsccbcbco = t1.tstdccbco
		  AND tsccbncta = t1.tstdcncta
	IF status = NOTFOUND THEN
	    LET g_msg =  "No existe"
	    CALL qx030_msgadvetencia_gb000(g_msg)
	    RETURN FALSE
	END IF
	IF t2.tsccbstat = 2 THEN
	    LET g_msg =  "Cuenta deshabilitada"
	    CALL qx030_msgadvetencia_gb000(g_msg)
	    RETURN FALSE
	END IF
	RETURN TRUE
END FUNCTION

FUNCTION f5030_buscar_tscon_ts325()
	LET g_dtmv = NULL
	SELECT tscondesc INTO g_dtmv
		FROM  tscon
		WHERE tsconpref = 10
		  AND tsconcorr = t1.tstdcpref
END FUNCTION

FUNCTION f5040_buscar_tstmv_ts325()
	DEFINE	l1	RECORD LIKE admus.*
        INITIALIZE t3.* TO NULL
        SELECT * INTO t3.*
                FROM tstmv
                WHERE tstmvpref = t1.tstdcpref
                  AND tstmvcorr = t1.tstdccorr
                  AND tstmvcorr > 0
        IF status = NOTFOUND THEN
            LET g_msg =  "No Existe tipo de movimiento"
            CALL qx030_msgadvetencia_gb000(g_msg)
            RETURN FALSE
        END IF
	IF g_band > 0 THEN
            SELECT * INTO l1.*
		    FROM  admus
                    WHERE admususrn = g_user
                      AND admusmodn = 96          
                      AND admuspref = t1.tstdcpref
                      AND admuscorr = t1.tstdccorr
	    IF status = NOTFOUND THEN
		LET g_msg =  "Tipo de concepto no habilitado para usuario"
		CALL qx030_msgadvetencia_gb000(g_msg)
                RETURN FALSE
            END IF
        END IF
        RETURN TRUE
END FUNCTION

FUNCTION f5050_buscar_iptdc_co305()
       DEFINE  l_desc  LIKE iptdc.iptdcdesc
       SELECT iptdcdesc INTO l_desc
               FROM  iptdc
               WHERE iptdctdoc = t4.iplcotdoc
       IF status = NOTFOUND THEN
           RETURN FALSE," "
       END IF
       RETURN TRUE,l_desc
END FUNCTION


{FUNCTION f5050_buscar_iptdc_co305()
	DEFINE 	l_desc	LIKE iptdc.iptdcdesc
        INITIALIZE l_desc TO NULL
        IF t4.iplconord IS NULL OR t4.iplconord = 0 THEN
            SELECT gbcondesc INTO l_desc
              FROM gbcon
             WHERE gbconpfij = 400
               AND gbconcorr = t4.iplcotdoc
            IF status = NOTFOUND THEN
                RETURN FALSE,l_desc
            END IF
        ELSE
            SELECT iptdcdesc INTO l_desc
              FROM  iptdc
             WHERE iptdctdoc = t4.iplcotdoc
            IF status = NOTFOUND THEN
                RETURN FALSE,l_desc
            END IF
        END IF
	RETURN TRUE,l_desc
END FUNCTION
}
FUNCTION f5060_buscar_documento_fiscal_ts325()
	DEFINE 	l_npol  LIKE ippol.ippolnpol,
	       	l_nbol  LIKE iplco.iplcoafac
	LET g_mdoc = "N"
        INITIALIZE t4.*,t5.*,g_etiq,g_ddoc TO NULL
	#------------------------------ Factura -------------------------------#
        SELECT * INTO t4.*
                FROM  iplco
                WHERE iplcomodn = 96
                  AND iplconopr = t1.tstdcntra
                  AND iplcontra = t1.tstdcntra
		  AND (iplcotdoc = 1 OR iplcotdoc > 19)
	IF status = 0 THEN
	    LET g_etiq = "No.:"
            LET g_ddoc = t4.iplconfac USING "<<<<<<<<<<<<<<<"
	    LET g_mdoc = "F"
	    RETURN
	END IF
	#------------------------------ Poliza --------------------------------#
	LET l_npol = ""
	SELECT MIN(ippolnpol) INTO l_npol
	        FROM  ippol
	        WHERE ippolmorg = 96
	          AND ippolnopr = t1.tstdcntra
		  AND ippoltorg = t1.tstdcntra
	IF l_npol IS NOT NULL THEN
            SELECT * INTO t5.*
                    FROM  ippol
                    WHERE ippolnpol = l_npol
	    IF status = 0 THEN
	        LET g_etiq = "No.:"
                LET g_ddoc = t5.ippolnpol
	        LET g_mdoc = "P"
	        RETURN
	    END IF
	END IF
	#------------------------------ Boleto --------------------------------#
	LET l_nbol = 0
	SELECT MIN(iplcoafac) INTO l_nbol
	        FROM  iplco
	        WHERE iplcomodn = 96
	          AND iplconopr = t1.tstdcntra
		  AND iplcontra = t1.tstdcntra
		  AND iplcotdoc = 5
	IF l_nbol IS NULL THEN LET l_nbol = 0 END IF
	IF l_nbol > 0 THEN
            SELECT * INTO t4.*
                    FROM  iplco
                    WHERE iplcoafac = l_nbol
		      AND iplcotdoc = 5
	    IF status = 0 THEN
		LET g_etiq = "No.:"
                LET g_ddoc = t4.iplcoafac CLIPPED
	        LET g_mdoc = "B"
	    END IF
	END IF
END FUNCTION

FUNCTION f5070_buscar_cnplc_ts325(l_cnta)
        DEFINE  l_cnta  LIKE cnplc.cnplccnta
        INITIALIZE g_mcco,g_tcon TO NULL
        SELECT cnplcmcco,cnplctcon INTO g_mcco,g_tcon
                FROM  cnplc
                WHERE cnplccnta = l_cnta
        IF status = NOTFOUND THEN
            RETURN FALSE
        ELSE
            RETURN TRUE
        END IF
END FUNCTION

FUNCTION f5080_validar_cuenta_ts325(l_cctb,l_ccos,l_scaa)
        DEFINE  l_cctb  LIKE cntcn.cntcncctb,
                l_ccos  LIKE cntcn.cntcnccos,
                l_scaa  LIKE cntcn.cntcnscaa
        IF NOT f5070_buscar_cnplc_ts325(l_cctb) THEN
            LET g_msg =  "Cuenta: ",l_cctb," no esta definida en el Plan de Cuentas"
            CALL qx030_msgadvetencia_gb000(g_msg)
            RETURN FALSE,0,0
        END IF
        IF g_mcco = "S" THEN
            IF l_ccos IS NULL OR l_ccos <= 0 THEN
                LET g_msg =  "Falta Centro de Costo"
                CALL qx030_msgadvetencia_gb000(g_msg)
                RETURN FALSE,0,0
            END IF
	ELSE
            LET l_ccos = 0
	END IF
        IF g_tcon > 0 THEN
            IF l_scaa IS NULL OR l_scaa <= 0 THEN
                LET g_msg =  "Falta Analisis Adicional"
                CALL qx030_msgadvetencia_gb000(g_msg)
                RETURN FALSE,0,0
            END IF
        ELSE
            LET l_scaa = 0
        END IF
        RETURN TRUE,l_ccos,l_scaa
END FUNCTION

FUNCTION f5090_buscar_adhuu_ts325(l_uneg)
        DEFINE  l_uneg  LIKE adhuu.adhuuuneg
        SELECT * FROM adhuu
                WHERE adhuuusrn = g_user
                  AND adhuuuneg = l_uneg
        IF status = NOTFOUND THEN
            RETURN FALSE
        END IF
        RETURN TRUE
END FUNCTION

FUNCTION f5100_buscar_cnune_ts325(l_uneg)
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

FUNCTION f6000_limpiar_menu_ts325()
	IF g_mtflag = 0 THEN
	    CLEAR FORM
	END IF
        INITIALIZE t1.*,t4.*,t5.*,g_etiq,g_ddoc,g_mcco,g_uncc TO NULL
	INITIALIZE g_cpry,g_cprg,g_cfin TO NULL
	LET g_marca = FALSE
	LET g_mdoc = "N"
	LET g_crfa = 0  
	IF g_mtflag = 0 THEN
	    MESSAGE " "
	    DISPLAY BY NAME g_etiq,g_ddoc
	    DELETE FROM adtmp
            DELETE FROM tmptdi
            DELETE FROM tmp1tdi
            DELETE FROM tmpdfc
            DELETE FROM tmpunf
            DELETE FROM tmpdtd
	END IF
END FUNCTION

FUNCTION f6050_buscar_empresa_ts325()
        SELECT * INTO t0.* FROM gbpmt
        SELECT * INTO t01.* FROM gbrne
        SELECT * INTO t02.* FROM cnpmf
        SELECT * INTO t6.* FROM cnprm
        SELECT * INTO t9.* FROM tsctl
        SELECT * INTO t7.* FROM ipctl
        SELECT ipctlcrdi INTO g_crdi FROM ipctl
        SELECT COUNT(*) INTO g_band
                FROM admus
                WHERE admususrn = g_user
                  AND admusmodn = 96
        IF g_band IS NULL THEN LET g_band = 0 END IF
        LET at0.* = t0.*
END FUNCTION

FUNCTION f6300_display_datos_ts325()
	IF g_mtflag = 0 THEN
            DISPLAY BY NAME t1.tstdcntra,t1.tstdcndoc,t1.tstdcftra,t1.tstdccbco,
                            t1.tstdcncta,t1.tstdcpref,t1.tstdccorr,t1.tstdccmon,
			    t1.tstdcimpt,t1.tstdctcam,t1.tstdcimpo,t1.tstdcgls1,
			    t1.tstdcgls2,t1.tstdcgls3
	END IF
	CALL f5010_buscar_gbcon_ts325(11,t1.tstdccbco,1) RETURNING g_bank,g_flag
	CALL f5010_buscar_gbcon_ts325(10,t1.tstdccmon,1) 
		  RETURNING g_descmon,g_flag
	CALL f5010_buscar_gbcon_ts325(10,t1.tstdccmon,0) RETURNING g_abre,g_flag
	CALL f5020_buscar_tsccb_ts325() RETURNING g_flag
	CALL f5010_buscar_gbcon_ts325(10,t1.tstdccmoc,0) 
		  RETURNING g_abre1,g_flag
	CALL f5030_buscar_tscon_ts325()
        CALL f5040_buscar_tstmv_ts325() RETURNING g_flag
	CALL f5070_buscar_cnplc_ts325(t3.tstmvctbl) RETURNING g_flag
        CALL f5060_buscar_documento_fiscal_ts325()
	#----------------------------------------------------------------------#
	LET g_crfa = 0
	IF g_mdoc = "F" OR g_mdoc = "B" THEN
	    SELECT SUM(iplcocrdf) INTO g_crfa
		    FROM  iplco
		    WHERE iplcomodn = 96
		      AND iplconopr = t1.tstdcntra
		      AND iplcontra = t1.tstdcntra
	    IF g_crfa IS NULL THEN LET g_crfa = 0 END IF
	END IF
	#----------------------------------------------------------------------#
	IF g_mtflag = 0 THEN 
            DISPLAY BY NAME g_bank,g_abre,g_dtmv,t3.tstmvdesc,g_mdoc,g_abre1,
			    g_descmon,g_etiq,g_ddoc
	END IF
        #----------------- Distribucion de Centros de Costo -------------------#
        DELETE FROM tmptdi
        DELETE FROM tmp1tdi

        INSERT INTO tmptdi
        SELECT cntdicapl,cntdiitem,cntdiuneg,
               cntdiccos,cntdipdis,cntdiimpt
                FROM  cntdi
                WHERE cntdimodn = 96
                  AND cntdittra = 34
                  AND cntdintra = t1.tstdcntra

        INSERT INTO tmp1tdi
        SELECT cntdicapl,cntdiitem,cntdiuneg,
               cntdiccos,cntdipdis,cntdiimpt
                FROM  cntdi
                WHERE cntdimodn = 96
                  AND cntdittra = 34
                  AND cntdintra = t1.tstdcntra
END FUNCTION

###############
# OTRAS RUTINAS
###############
