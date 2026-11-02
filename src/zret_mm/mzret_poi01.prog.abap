*&---------------------------------------------------------------------*
*& Include MZRET_POI01 : modules PAI
*&---------------------------------------------------------------------*
" Retour / Quitter / Annuler : popup si données non sauvegardées
MODULE exit_0100 INPUT.
  DATA lv_answer TYPE c LENGTH 1.
  IF gv_changed = abap_true.
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

MODULE user_command_0100 INPUT.
  gv_save_ok = ok_code. CLEAR ok_code.
  CASE gv_save_ok.
    WHEN 'OTHER' OR 'ENTER' OR space.
      IF zret_s_po_hdr-po_number IS INITIAL.
        MESSAGE 'Renseignez un numéro de commande'(e01) TYPE 'E'.
      ENDIF.
      IF gv_loaded = abap_false OR zret_s_po_hdr-po_number <> gs_po_db-po_number.
        PERFORM load_po USING zret_s_po_hdr-po_number.
      ENDIF.
    WHEN 'TOGGLE'.
      PERFORM toggle_edit.
    WHEN 'HDR_TOGGLE'.
      IF gv_hdr_open = abap_true.
        gv_hdr_open = abap_false.
      ELSE.
        gv_hdr_open = abap_true.
      ENDIF.
    WHEN 'TABI1' OR 'TABI2'.
      ts_item-activetab = gv_save_ok.
    WHEN 'CHECK'.
      PERFORM check_all.
      MESSAGE |Commande { zret_s_po_hdr-po_number } contrôlée, aucune erreur| TYPE 'S'.
    WHEN 'SAVE'.
      IF gv_edit = abap_false.
        MESSAGE 'Passez en mode Modifier avant de sauvegarder'(e02) TYPE 'E'.
      ENDIF.
      PERFORM check_all.
      PERFORM save_po.
  ENDCASE.
ENDMODULE.

" En-tête (0110) : la saisie marque la commande modifiée
MODULE hdr_pai INPUT.
  IF gv_edit = abap_true.
    gv_changed = abap_true.
  ENDIF.
ENDMODULE.

" Détail du poste (0121/0122) : recopie vers la ligne de la grille
MODULE item_pai INPUT.
  CHECK gv_edit = abap_true AND zret_s_po_item_alv-item_num IS NOT INITIAL.
  READ TABLE gt_items ASSIGNING FIELD-SYMBOL(<ls_item>)
       WITH KEY item_num = zret_s_po_item_alv-item_num.
  IF sy-subrc = 0.
    IF <ls_item>-quantity <> zret_s_po_item_alv-quantity
       OR <ls_item>-unit_price <> zret_s_po_item_alv-unit_price
       OR <ls_item>-final_delivery <> zret_s_po_item_alv-final_delivery.
      <ls_item>-quantity       = zret_s_po_item_alv-quantity.
      <ls_item>-unit_price     = zret_s_po_item_alv-unit_price.
      <ls_item>-final_delivery = zret_s_po_item_alv-final_delivery.
      PERFORM recalc_item CHANGING <ls_item>.
      gv_changed = abap_true.
    ENDIF.
  ENDIF.
ENDMODULE.
