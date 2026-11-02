*&---------------------------------------------------------------------*
*& Include MZRET_POO01 : modules PBO
*&---------------------------------------------------------------------*
MODULE status_0100 OUTPUT.
  SET PF-STATUS 'MAIN'.
  IF gv_loaded = abap_false.
    gv_title = 'Commande d''achat : sélection'(t01).
  ELSEIF gv_edit = abap_true.
    gv_title = |Modifier commande { zret_s_po_hdr-po_number }|.
  ELSE.
    gv_title = |Afficher commande { zret_s_po_hdr-po_number }|.
  ENDIF.
  SET TITLEBAR 'T_MAIN' WITH gv_title.
  IF gv_hdr_open = abap_true.
    gv_sub_hdr = '0110'.
  ELSE.
    gv_sub_hdr = '0111'.
  ENDIF.
  CASE ts_item-activetab.
    WHEN 'TABI2'. gv_sub_tab = '0122'.
    WHEN OTHERS.  gv_sub_tab = '0121'. ts_item-activetab = 'TABI1'.
  ENDCASE.
ENDMODULE.

" Grille ALV : créée une fois, rafraîchie ensuite
MODULE init_grid OUTPUT.
  IF go_grid IS INITIAL.
    PERFORM create_grid.
  ELSE.
    PERFORM refresh_grid.
  ENDIF.
ENDMODULE.

" En-tête et détail : saisie seulement en mode Modifier
MODULE set_input OUTPUT.
  LOOP AT SCREEN.
    IF screen-group1 = 'EDT'.
      IF gv_edit = abap_true.
        screen-input = 1.
      ELSE.
        screen-input = 0.
      ENDIF.
      MODIFY SCREEN.
    ENDIF.
  ENDLOOP.
ENDMODULE.
