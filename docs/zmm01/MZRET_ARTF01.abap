*&---------------------------------------------------------------------*
*& Include MZRET_ARTF01 : formes
*&---------------------------------------------------------------------*
FORM load_article USING iv_id TYPE zret_t_article-article_id.
  CLEAR: gs_art_db, gt_var, gv_exists.
  SELECT SINGLE * FROM zret_t_article INTO gs_art_db WHERE article_id = iv_id.
  IF sy-subrc = 0.
    gv_exists = abap_true.
    MOVE-CORRESPONDING gs_art_db TO zret_s_art.
    SELECT * FROM zret_t_art_var INTO TABLE gt_var_db WHERE article_id = iv_id.
    LOOP AT gt_var_db INTO DATA(ls_db).
      CLEAR gs_var. MOVE-CORRESPONDING ls_db TO gs_var. APPEND gs_var TO gt_var.
    ENDLOOP.
    MESSAGE |Article { iv_id } existe : passage en modification| TYPE 'S'.
  ELSE.
    gv_exists = abap_false.
    CLEAR zret_s_art.
    zret_s_art-article_id = iv_id.
    zret_s_art-base_uom   = 'ST'.
    zret_s_art-currency   = 'EUR'.
    zret_s_art-active_flag = 'X'.
  ENDIF.
ENDFORM.

" Tous les contrôles, y compris les variantes (EAN à 13 chiffres)
FORM check_all.
  DATA lv_row TYPE i.
  IF zret_s_art-article_name IS INITIAL.
    ts_main-activetab = 'TAB1'.
    MESSAGE 'Renseignez le nom de l''article'(e02) TYPE 'E'.
  ENDIF.
  IF zret_s_art-article_type IS INITIAL.
    ts_main-activetab = 'TAB1'.
    MESSAGE 'Choisissez un type d''article'(e03) TYPE 'E'.
  ENDIF.
  IF zret_s_art-price <= 0.
    ts_main-activetab = 'TAB2'.
    MESSAGE 'Le prix doit être supérieur à zéro'(e04) TYPE 'E'.
  ENDIF.
  LOOP AT gt_var INTO gs_var.
    lv_row = sy-tabix.
    CHECK gs_var-variant_id IS NOT INITIAL OR gs_var-ean IS NOT INITIAL.
    IF gs_var-variant_id IS INITIAL.
      ts_main-activetab = 'TAB3'.
      MESSAGE |Variante ligne { lv_row } : identifiant manquant| TYPE 'E'.
    ENDIF.
    IF gs_var-ean IS NOT INITIAL AND ( strlen( gs_var-ean ) <> 13 OR gs_var-ean CN '0123456789' ).
      ts_main-activetab = 'TAB3'.
      MESSAGE |Variante ligne { lv_row } : l'EAN doit avoir 13 chiffres| TYPE 'E'.
    ENDIF.
  ENDLOOP.
ENDFORM.

FORM save_article.
  DATA: ls_art TYPE zret_t_article,
        lt_var TYPE STANDARD TABLE OF zret_t_art_var,
        ls_var TYPE zret_t_art_var,
        lv_n   TYPE i.
  MOVE-CORRESPONDING zret_s_art TO ls_art.
  ls_art-mandt = sy-mandt.
  IF gv_exists = abap_true.
    ls_art-created_by = gs_art_db-created_by.
    ls_art-created_on = gs_art_db-created_on.
  ELSE.
    ls_art-created_by = sy-uname.
    ls_art-created_on = sy-datum.
  ENDIF.
  ls_art-changed_by = sy-uname.
  ls_art-changed_on = sy-datum.
  LOOP AT gt_var INTO gs_var WHERE variant_id IS NOT INITIAL.
    CLEAR ls_var.
    MOVE-CORRESPONDING gs_var TO ls_var.
    ls_var-mandt      = sy-mandt.
    ls_var-article_id = ls_art-article_id.
    IF ls_var-currency IS INITIAL. ls_var-currency = ls_art-currency. ENDIF.
    APPEND ls_var TO lt_var.
  ENDLOOP.
  lv_n = lines( lt_var ).

  MODIFY zret_t_article FROM ls_art.
  DELETE FROM zret_t_art_var WHERE article_id = ls_art-article_id.
  IF lt_var IS NOT INITIAL.
    INSERT zret_t_art_var FROM TABLE lt_var.
  ENDIF.
  IF sy-subrc = 0.
    COMMIT WORK.
    gv_changed = abap_false.
    MESSAGE |Article { ls_art-article_id } sauvegardé ({ lv_n } variante(s))| TYPE 'S'.
    CLEAR: zret_s_art, gt_var.
    LEAVE TO SCREEN 0100.
  ELSE.
    ROLLBACK WORK.
    MESSAGE 'Erreur à la sauvegarde des variantes'(e05) TYPE 'E'.
  ENDIF.
ENDFORM.
