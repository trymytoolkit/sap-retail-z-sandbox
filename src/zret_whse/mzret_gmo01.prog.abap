*&---------------------------------------------------------------------*
*& Include MZRET_GMO01 : modules PBO
*&---------------------------------------------------------------------*
MODULE status_0100 OUTPUT.
  SET PF-STATUS 'MAIN'.
  IF gv_loaded = abap_true.
    gv_title = |Réception sur commande { zret_s_gm_hdr-ref_doc } ({ lines( gt_items ) } poste(s))|.
  ELSE.
    gv_title = 'Mouvement de marchandises'(t01).
  ENDIF.
  SET TITLEBAR 'T_MAIN' WITH gv_title.
  IF zret_s_gm_hdr-action IS INITIAL.  zret_s_gm_hdr-action  = 'A01'. ENDIF.
  IF zret_s_gm_hdr-reftype IS INITIAL. zret_s_gm_hdr-reftype = 'R01'. ENDIF.
  CASE ts_hdr-activetab.
    WHEN 'TABH2'. gv_sub_htab = '0112'.
    WHEN OTHERS.  gv_sub_htab = '0111'. ts_hdr-activetab = 'TABH1'.
  ENDCASE.
  CASE ts_item-activetab.
    WHEN 'TABI2'. gv_sub_itab = '0122'.
    WHEN 'TABI3'. gv_sub_itab = '0123'.
    WHEN OTHERS.  gv_sub_itab = '0121'. ts_item-activetab = 'TABI1'.
  ENDCASE.
ENDMODULE.

" Listes déroulantes du bandeau (action, type de référence)
MODULE init_listboxes OUTPUT.
  DATA: lt_values TYPE vrm_values,
        ls_value  TYPE vrm_value.
  CLEAR lt_values.
  ls_value-key = 'A01'. ls_value-text = 'Réception'.              APPEND ls_value TO lt_values.
  ls_value-key = 'A07'. ls_value-text = 'Sortie de marchandises'. APPEND ls_value TO lt_values.
  ls_value-key = 'A08'. ls_value-text = 'Transfert'.              APPEND ls_value TO lt_values.
  ls_value-key = 'A09'. ls_value-text = 'Rebut'.                  APPEND ls_value TO lt_values.
  CALL FUNCTION 'VRM_SET_VALUES'
    EXPORTING
      id     = 'ZRET_S_GM_HDR-ACTION'
      values = lt_values.
  CLEAR lt_values.
  ls_value-key = 'R01'. ls_value-text = 'Commande d''achat'. APPEND ls_value TO lt_values.
  ls_value-key = 'R05'. ls_value-text = 'Livraison'.         APPEND ls_value TO lt_values.
  ls_value-key = 'R10'. ls_value-text = 'Autre'.             APPEND ls_value TO lt_values.
  CALL FUNCTION 'VRM_SET_VALUES'
    EXPORTING
      id     = 'ZRET_S_GM_HDR-REFTYPE'
      values = lt_values.
ENDMODULE.

" Table control : au moins gc_lines_min lignes affichées
MODULE tc_init OUTPUT.
  DATA lv_lines TYPE i.
  lv_lines = lines( gt_items ).
  IF lv_lines < gc_lines_min.
    tc_items-lines = gc_lines_min.
  ELSE.
    tc_items-lines = lv_lines.
  ENDIF.
ENDMODULE.

MODULE tc_pbo OUTPUT.
  zret_s_gm_item = gs_item.
ENDMODULE.

" Détail du poste : suit gv_detail_idx, resynchronisé depuis la table interne
MODULE item_pbo OUTPUT.
  IF gv_detail_idx > 0.
    READ TABLE gt_items INTO zret_s_gm_item INDEX gv_detail_idx.
    IF sy-subrc <> 0.
      CLEAR zret_s_gm_item. gv_detail_idx = 0.
    ENDIF.
  ELSE.
    CLEAR zret_s_gm_item.
  ENDIF.
  gs_item_shown = zret_s_gm_item.
ENDMODULE.
