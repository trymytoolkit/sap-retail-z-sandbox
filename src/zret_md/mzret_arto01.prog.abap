*&---------------------------------------------------------------------*
*& Include MZRET_ARTO01 : modules PBO
*&---------------------------------------------------------------------*
MODULE status_0100 OUTPUT.
  SET PF-STATUS 'MAIN'.
  SET TITLEBAR 'T_MAIN' WITH 'Article : sélection'(t01).
ENDMODULE.

MODULE status_0200 OUTPUT.
  SET PF-STATUS 'MAIN'.
  IF gv_exists = abap_true.
    gv_title = |Modifier article { zret_s_art-article_id }|.
  ELSE.
    gv_title = 'Créer article'(t02).
  ENDIF.
  SET TITLEBAR 'T_MAIN' WITH gv_title.
  " Onglet actif -> sous-écran
  CASE ts_main-activetab.
    WHEN 'TAB2'. gv_subscreen = '0220'.
    WHEN 'TAB3'. gv_subscreen = '0230'.
    WHEN OTHERS. gv_subscreen = '0210'. ts_main-activetab = 'TAB1'.
  ENDCASE.
ENDMODULE.

" Liste déroulante du type d'article (zone de liste de l'écran 0210)
MODULE init_listbox OUTPUT.
  DATA: lt_values TYPE vrm_values,
        ls_value  TYPE vrm_value.
  CLEAR lt_values.
  ls_value-key = 'HARD'. ls_value-text = 'Hardware'.   APPEND ls_value TO lt_values.
  ls_value-key = 'SOFT'. ls_value-text = 'Softgoods'.  APPEND ls_value TO lt_values.
  ls_value-key = 'FOOD'. ls_value-text = 'Food'.       APPEND ls_value TO lt_values.
  CALL FUNCTION 'VRM_SET_VALUES'
    EXPORTING
      id     = 'ZRET_S_ART-ARTICLE_TYPE'
      values = lt_values.
ENDMODULE.

" Table control : toujours au moins gc_lines_min lignes (dont des vides)
MODULE tc_var_init OUTPUT.
  DATA lv_lines TYPE i.
  lv_lines = lines( gt_var ).
  WHILE lv_lines < gc_lines_min.
    CLEAR gs_var.
    APPEND gs_var TO gt_var.
    lv_lines = lv_lines + 1.
  ENDWHILE.
  DESCRIBE TABLE gt_var LINES tc_var-lines.
ENDMODULE.

MODULE tc_var_pbo OUTPUT.
  " gs_var est positionné par le LOOP ... WITH CONTROL ; recopie vers la zone écran
  zret_s_art_var = gs_var.
ENDMODULE.
