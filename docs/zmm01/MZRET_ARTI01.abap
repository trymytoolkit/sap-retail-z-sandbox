*&---------------------------------------------------------------------*
*& Include MZRET_ARTI01 : modules PAI
*&---------------------------------------------------------------------*
MODULE exit_0100 INPUT.
  LEAVE PROGRAM.
ENDMODULE.

MODULE user_command_0100 INPUT.
  gv_save_ok = ok_code. CLEAR ok_code.
  CASE gv_save_ok.
    WHEN 'GO' OR 'ENTER' OR space.
      IF zret_s_art-article_id IS INITIAL.
        MESSAGE 'Renseignez un identifiant d''article'(e01) TYPE 'E'.
      ENDIF.
      PERFORM load_article USING zret_s_art-article_id.
      ts_main-activetab = 'TAB1'.
      gv_changed = abap_false.
      LEAVE TO SCREEN 0200.
    WHEN 'BACK' OR 'EXIT' OR 'CANC'.
      LEAVE PROGRAM.
  ENDCASE.
ENDMODULE.

" Retour / Quitter / Annuler : popup si données non sauvegardées
MODULE exit_0200 INPUT.
  DATA lv_answer TYPE c LENGTH 1.
  IF gv_changed = abap_true.
    CALL FUNCTION 'POPUP_TO_CONFIRM'
      EXPORTING
        titlebar       = 'Quitter'(p01)
        text_question  = 'Les données seront perdues. Quitter ?'(p02)
        text_button_1  = 'Oui'(p03)
        text_button_2  = 'Non'(p04)
        default_button = '2'
        display_cancel_button = space
      IMPORTING
        answer         = lv_answer
      EXCEPTIONS
        OTHERS         = 1.
    IF lv_answer <> '1'.
      RETURN.
    ENDIF.
  ENDIF.
  CLEAR: zret_s_art, gt_var, gv_changed.
  LEAVE TO SCREEN 0100.
ENDMODULE.

MODULE user_command_0200 INPUT.
  gv_save_ok = ok_code. CLEAR ok_code.
  CASE gv_save_ok.
    WHEN 'TAB1' OR 'TAB2' OR 'TAB3'.
      ts_main-activetab = gv_save_ok.
    WHEN 'SAVE'.
      PERFORM check_all.
      PERFORM save_article.
    WHEN 'ENTER' OR space.
      " contrôle des champs, sans sauvegarde
  ENDCASE.
ENDMODULE.

" Contrôles de l'onglet Données de base (message E = curseur sur le champ)
MODULE check_0210 INPUT.
  gv_changed = abap_true.
  IF zret_s_art-article_name IS INITIAL.
    MESSAGE 'Renseignez le nom de l''article'(e02) TYPE 'E'.
  ENDIF.
  IF zret_s_art-article_type IS INITIAL.
    MESSAGE 'Choisissez un type d''article'(e03) TYPE 'E'.
  ENDIF.
  IF zret_s_art-base_uom IS INITIAL.
    zret_s_art-base_uom = 'PC'.
  ENDIF.
ENDMODULE.

MODULE check_0220 INPUT.
  gv_changed = abap_true.
  IF zret_s_art-price <= 0.
    MESSAGE 'Le prix doit être supérieur à zéro'(e04) TYPE 'E'.
  ENDIF.
  IF zret_s_art-currency IS INITIAL.
    zret_s_art-currency = 'EUR'.
  ENDIF.
ENDMODULE.

" Table control : recopie de la ligne modifiée
MODULE tc_var_pai INPUT.
  MODIFY gt_var FROM gs_var INDEX tc_var-current_line.
  gv_changed = abap_true.
ENDMODULE.

MODULE tc_var_user_command INPUT.
  CASE ok_code.
    WHEN 'ADD'.
      CLEAR gs_var. APPEND gs_var TO gt_var. CLEAR ok_code.
    WHEN 'DEL'.
      DELETE gt_var WHERE mark = 'X'. CLEAR ok_code.
  ENDCASE.
ENDMODULE.
