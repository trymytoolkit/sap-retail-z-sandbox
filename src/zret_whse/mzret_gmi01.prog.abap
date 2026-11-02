*&---------------------------------------------------------------------*
*& Include MZRET_GMI01 : modules PAI
*&---------------------------------------------------------------------*
MODULE exit_0100 INPUT.
  DATA lv_answer TYPE c LENGTH 1.
  IF gv_loaded = abap_true AND gv_changed = abap_true.
    CALL FUNCTION 'POPUP_TO_CONFIRM'
      EXPORTING
        titlebar              = 'Quitter'(p01)
        text_question         = 'Les données seront perdues. Quitter ?'(p02)
        text_button_1         = 'Oui'(p03)
        text_button_2         = 'Non'(p04)
        default_button        = '2'
        display_cancel_button = space
      IMPORTING
        answer                = lv_answer
      EXCEPTIONS
        OTHERS                = 1.
    IF lv_answer <> '1'.
      RETURN.
    ENDIF.
  ENDIF.
  LEAVE PROGRAM.
ENDMODULE.

" Ligne du table control : recopie vers la table interne
MODULE tc_pai INPUT.
  DATA ls_old TYPE zret_s_gm_item.
  READ TABLE gt_items INTO ls_old INDEX tc_items-current_line.
  CHECK sy-subrc = 0.
  " Seules les colonnes saisissables viennent de l'écran ; le reste garde
  " la valeur de la table interne (les champs en sortie ne sont pas transportés
  " et la ligne de travail peut contenir des restes d'une autre ligne).
  gs_item          = ls_old.
  gs_item-mark     = zret_s_gm_item-mark.
  gs_item-item_ok  = zret_s_gm_item-item_ok.
  gs_item-quantity = zret_s_gm_item-quantity.
  gs_item-dst_zone = zret_s_gm_item-dst_zone.
  MODIFY gt_items FROM gs_item INDEX tc_items-current_line.
  IF gs_item <> ls_old.
    gv_changed = abap_true.
  ENDIF.
ENDMODULE.

MODULE user_command_0100 INPUT.
  DATA lv_line TYPE i.
  gv_save_ok = ok_code. CLEAR ok_code.
  " La ligne sous le curseur devient la ligne de détail
  GET CURSOR LINE lv_line.
  IF lv_line > 0 AND gv_loaded = abap_true.
    lv_line = tc_items-top_line + lv_line - 1.
    IF lv_line <= lines( gt_items ).
      gv_detail_idx = lv_line.
    ENDIF.
  ENDIF.
  CASE gv_save_ok.
    WHEN 'EXEC'.
      PERFORM load_reference.
    WHEN 'ALL_OK'.
      LOOP AT gt_items ASSIGNING FIELD-SYMBOL(<ls_item>).
        <ls_item>-item_ok = abap_true.
      ENDLOOP.
      gv_changed = abap_true.
    WHEN 'DEL'.
      DELETE gt_items WHERE mark = abap_true.
      gv_changed = abap_true.
      gv_detail_idx = 0.
    WHEN 'CHECK'.
      PERFORM check_items.
    WHEN 'POST'.
      PERFORM post_items.
    WHEN 'TABH1' OR 'TABH2'.
      ts_hdr-activetab = gv_save_ok.
    WHEN 'TABI1' OR 'TABI2' OR 'TABI3'.
      ts_item-activetab = gv_save_ok.
    WHEN 'ENTER' OR space.
      IF gv_loaded = abap_false AND zret_s_gm_hdr-ref_doc IS NOT INITIAL.
        PERFORM load_reference.
      ENDIF.
  ENDCASE.
ENDMODULE.

" Détail : seules les valeurs modifiées à l'écran du détail sont recopiées
MODULE item_pai INPUT.
  " La zone de travail est partagée avec le table control : au PAI elle porte
  " la dernière ligne transportée. On ne lit donc que les champs présents sur
  " le sous-écran courant (sy-dynnr), et seulement s'ils ont changé.
  CHECK gv_detail_idx > 0.
  READ TABLE gt_items ASSIGNING FIELD-SYMBOL(<ls_cur>) INDEX gv_detail_idx.
  CHECK sy-subrc = 0.
  CASE sy-dynnr.
    WHEN '0121'.
      IF zret_s_gm_item-quantity <> gs_item_shown-quantity.
        <ls_cur>-quantity = zret_s_gm_item-quantity. gv_changed = abap_true.
      ENDIF.
    WHEN '0122'.
      IF zret_s_gm_item-dst_zone <> gs_item_shown-dst_zone.
        <ls_cur>-dst_zone = zret_s_gm_item-dst_zone. gv_changed = abap_true.
      ENDIF.
    WHEN '0123'.
      IF zret_s_gm_item-hu_id <> gs_item_shown-hu_id OR zret_s_gm_item-batch <> gs_item_shown-batch.
        <ls_cur>-hu_id = zret_s_gm_item-hu_id. <ls_cur>-batch = zret_s_gm_item-batch.
        gv_changed = abap_true.
      ENDIF.
  ENDCASE.
ENDMODULE.
