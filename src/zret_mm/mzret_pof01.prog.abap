*&---------------------------------------------------------------------*
*& Include MZRET_POF01 : classe de gestion de la grille et formes
*&---------------------------------------------------------------------*
CLASS lcl_po_alv DEFINITION.
  PUBLIC SECTION.
    METHODS:
      on_toolbar      FOR EVENT toolbar OF cl_gui_alv_grid
        IMPORTING e_object e_interactive,
      on_user_command FOR EVENT user_command OF cl_gui_alv_grid
        IMPORTING e_ucomm,
      on_double_click FOR EVENT double_click OF cl_gui_alv_grid
        IMPORTING e_row,
      on_data_changed FOR EVENT data_changed OF cl_gui_alv_grid
        IMPORTING er_data_changed,
      on_data_changed_finished FOR EVENT data_changed_finished OF cl_gui_alv_grid.
ENDCLASS.

CLASS lcl_po_alv IMPLEMENTATION.
  " Deux boutons ajoutés à la barre d'outils standard de la grille
  METHOD on_toolbar.
    DATA ls_btn TYPE stb_button.
    CLEAR ls_btn. ls_btn-butn_type = 3. APPEND ls_btn TO e_object->mt_toolbar.
    CLEAR ls_btn.
    ls_btn-function  = 'ADD_ITEM'.
    ls_btn-icon      = icon_create.
    ls_btn-text      = 'Nouveau poste'(b01).
    ls_btn-quickinfo = 'Ajouter un poste'(b02).
    APPEND ls_btn TO e_object->mt_toolbar.
    CLEAR ls_btn.
    ls_btn-function  = 'DEL_ITEM'.
    ls_btn-icon      = icon_delete.
    ls_btn-text      = 'Supprimer le poste'(b03).
    ls_btn-quickinfo = 'Supprimer les postes sélectionnés'(b04).
    APPEND ls_btn TO e_object->mt_toolbar.
    CLEAR ls_btn.
    ls_btn-function  = 'DETAIL'.
    ls_btn-icon      = icon_detail.
    ls_btn-text      = 'Détail'(b05).
    ls_btn-quickinfo = 'Afficher le poste sélectionné'(b06).
    APPEND ls_btn TO e_object->mt_toolbar.
  ENDMETHOD.

  METHOD on_user_command.
    DATA: lt_rows TYPE lvc_t_row,
          ls_row  TYPE lvc_s_row,
          ls_new  TYPE zret_s_po_item_alv.
    CASE e_ucomm.
      WHEN 'ADD_ITEM'.
        IF gv_edit = abap_false.
          MESSAGE 'Passez en mode Modifier'(e03) TYPE 'S' DISPLAY LIKE 'E'.
          RETURN.
        ENDIF.
        CLEAR ls_new.
        LOOP AT gt_items INTO DATA(ls_i).
          IF ls_i-item_num > ls_new-item_num. ls_new-item_num = ls_i-item_num. ENDIF.
        ENDLOOP.
        ls_new-item_num = ls_new-item_num + gc_item_step.
        ls_new-base_uom = 'ST'.
        ls_new-currency = zret_s_po_hdr-currency.
        APPEND ls_new TO gt_items.
        gv_changed = abap_true.
        PERFORM refresh_grid.
      WHEN 'DEL_ITEM'.
        IF gv_edit = abap_false.
          MESSAGE 'Passez en mode Modifier'(e03) TYPE 'S' DISPLAY LIKE 'E'.
          RETURN.
        ENDIF.
        go_grid->get_selected_rows( IMPORTING et_index_rows = lt_rows ).
        IF lt_rows IS INITIAL.
          MESSAGE 'Sélectionnez un poste'(e04) TYPE 'S' DISPLAY LIKE 'E'.
          RETURN.
        ENDIF.
        LOOP AT lt_rows INTO ls_row.
          READ TABLE gt_items INTO ls_i INDEX ls_row-index.
          IF sy-subrc = 0 AND ls_i-delivered_qty > 0.
            MESSAGE |Poste { ls_i-item_num } livré : suppression impossible| TYPE 'S' DISPLAY LIKE 'E'.
            RETURN.
          ENDIF.
        ENDLOOP.
        SORT lt_rows BY index DESCENDING.
        LOOP AT lt_rows INTO ls_row.
          DELETE gt_items INDEX ls_row-index.
        ENDLOOP.
        gv_changed = abap_true.
        PERFORM refresh_grid.
      WHEN 'DETAIL'.
        go_grid->get_selected_rows( IMPORTING et_index_rows = lt_rows ).
        READ TABLE lt_rows INTO ls_row INDEX 1.
        IF sy-subrc = 0.
          DATA(lv_idx) = CONV i( ls_row-index ).
          PERFORM show_detail USING lv_idx.
        ENDIF.
    ENDCASE.
  ENDMETHOD.

  METHOD on_double_click.
    DATA(lv_idx) = CONV i( e_row-index ).
    PERFORM show_detail USING lv_idx.
  ENDMETHOD.

  " Saisie dans la grille : rien à refuser ici, les contrôles métier sont
  " dans check_all (bouton Contrôler et sauvegarde) pour tenir dans la
  " barre de statut, lisible par l'Automate ; le protocole ALV reste vide.
  METHOD on_data_changed.
  ENDMETHOD.

  " Après validation : montants recalculés, commande marquée modifiée
  METHOD on_data_changed_finished.
    LOOP AT gt_items ASSIGNING FIELD-SYMBOL(<ls_item>).
      PERFORM recalc_item CHANGING <ls_item>.
    ENDLOOP.
    PERFORM recalc_header.
    gv_changed = abap_true.
    PERFORM refresh_grid.
  ENDMETHOD.
ENDCLASS.

FORM create_grid.
  CREATE OBJECT go_cont
    EXPORTING
      container_name = 'CC_ITEMS'.
  CREATE OBJECT go_grid
    EXPORTING
      i_parent = go_cont.
  CALL FUNCTION 'LVC_FIELDCATALOG_MERGE'
    EXPORTING
      i_structure_name = 'ZRET_S_PO_ITEM_ALV'
    CHANGING
      ct_fieldcat      = gt_fcat.
  PERFORM set_fcat_edit.
  DATA ls_layout TYPE lvc_s_layo.
  ls_layout-sel_mode   = 'A'.
  ls_layout-cwidth_opt = 'X'.
  ls_layout-stylefname = ''.
  CREATE OBJECT go_handler.
  SET HANDLER go_handler->on_toolbar FOR go_grid.
  SET HANDLER go_handler->on_user_command FOR go_grid.
  SET HANDLER go_handler->on_double_click FOR go_grid.
  SET HANDLER go_handler->on_data_changed FOR go_grid.
  SET HANDLER go_handler->on_data_changed_finished FOR go_grid.
  go_grid->set_table_for_first_display(
    EXPORTING
      is_layout       = ls_layout
    CHANGING
      it_outtab       = gt_items
      it_fieldcatalog = gt_fcat ).
  go_grid->register_edit_event( cl_gui_alv_grid=>mc_evt_enter ).
  go_grid->set_ready_for_input( 0 ).
ENDFORM.

" Colonnes éditables en mode Modifier : article (postes neufs), quantité, prix
FORM set_fcat_edit.
  LOOP AT gt_fcat ASSIGNING FIELD-SYMBOL(<ls_fcat>).
    CASE <ls_fcat>-fieldname.
      WHEN 'QUANTITY' OR 'UNIT_PRICE' OR 'ARTICLE_ID'.
        <ls_fcat>-edit = gv_edit.
      WHEN 'OPEN_QTY'.
        <ls_fcat>-coltext = 'Reste à livrer'(c01).
      WHEN 'FINAL_DELIVERY'.
        <ls_fcat>-checkbox = 'X'.
        <ls_fcat>-coltext  = 'Liv. finale'(c02).
    ENDCASE.
  ENDLOOP.
ENDFORM.

FORM refresh_grid.
  DATA ls_stable TYPE lvc_s_stbl.
  ls_stable-row = 'X'. ls_stable-col = 'X'.
  go_grid->refresh_table_display( is_stable = ls_stable ).
ENDFORM.

FORM toggle_edit.
  IF gv_loaded = abap_false.
    MESSAGE 'Chargez d''abord une commande'(e05) TYPE 'E'.
  ENDIF.
  IF gv_edit = abap_false.
    IF zret_s_po_hdr-status = 'C' OR zret_s_po_hdr-status = 'D' OR zret_s_po_hdr-status = 'X'.
      MESSAGE |Commande au statut { zret_s_po_hdr-status } : modification impossible| TYPE 'E'.
    ENDIF.
    gv_edit = abap_true.
  ELSE.
    IF gv_changed = abap_true.
      PERFORM load_po USING zret_s_po_hdr-po_number.   " abandon des saisies
    ENDIF.
    gv_edit = abap_false.
  ENDIF.
  PERFORM set_fcat_edit.
  IF go_grid IS NOT INITIAL.
    go_grid->set_frontend_fieldcatalog( gt_fcat ).
    IF gv_edit = abap_true.
      go_grid->set_ready_for_input( 1 ).
    ELSE.
      go_grid->set_ready_for_input( 0 ).
    ENDIF.
  ENDIF.
ENDFORM.

FORM load_po USING VALUE(iv_po) TYPE zret_t_po-po_number.
  DATA: lt_db TYPE STANDARD TABLE OF zret_t_po_item,
        ls_i  TYPE zret_s_po_item_alv.
  SELECT SINGLE * FROM zret_t_po INTO gs_po_db WHERE po_number = iv_po.
  IF sy-subrc <> 0.
    MESSAGE |Commande { iv_po } inexistante| TYPE 'E'.
  ENDIF.
  CLEAR: zret_s_po_hdr, gt_items, zret_s_po_item_alv.
  MOVE-CORRESPONDING gs_po_db TO zret_s_po_hdr.
  SELECT * FROM zret_t_po_item INTO TABLE lt_db WHERE po_number = iv_po ORDER BY item_num.
  LOOP AT lt_db INTO DATA(ls_db).
    CLEAR ls_i.
    MOVE-CORRESPONDING ls_db TO ls_i.
    PERFORM recalc_item CHANGING ls_i.
    APPEND ls_i TO gt_items.
  ENDLOOP.
  gv_loaded = abap_true.
  gv_changed = abap_false.
  gv_edit = abap_false.
  ts_item-activetab = 'TABI1'.
  READ TABLE gt_items INTO zret_s_po_item_alv INDEX 1.
  IF go_grid IS NOT INITIAL.
    PERFORM set_fcat_edit.
    go_grid->set_frontend_fieldcatalog( gt_fcat ).
    go_grid->set_ready_for_input( 0 ).
    PERFORM refresh_grid.
  ENDIF.
  MESSAGE |Commande { iv_po } chargée ({ lines( gt_items ) } poste(s))| TYPE 'S'.
ENDFORM.

FORM recalc_item CHANGING cs_item TYPE zret_s_po_item_alv.
  cs_item-line_amount = cs_item-quantity * cs_item-unit_price.
  cs_item-open_qty    = cs_item-quantity - cs_item-delivered_qty.
  IF cs_item-open_qty < 0. cs_item-open_qty = 0. ENDIF.
  IF cs_item-currency IS INITIAL. cs_item-currency = zret_s_po_hdr-currency. ENDIF.
ENDFORM.

FORM recalc_header.
  zret_s_po_hdr-total_amount = 0.
  LOOP AT gt_items INTO DATA(ls_i).
    zret_s_po_hdr-total_amount = zret_s_po_hdr-total_amount + ls_i-line_amount.
  ENDLOOP.
ENDFORM.

FORM show_detail USING iv_index TYPE i.
  READ TABLE gt_items INTO zret_s_po_item_alv INDEX iv_index.
  IF sy-subrc <> 0.
    MESSAGE 'Sélectionnez un poste'(e04) TYPE 'S' DISPLAY LIKE 'E'.
  ENDIF.
ENDFORM.

" Tous les contrôles ; message E au premier problème
FORM check_all.
  IF gv_loaded = abap_false.
    MESSAGE 'Chargez d''abord une commande'(e05) TYPE 'E'.
  ENDIF.
  IF zret_s_po_hdr-supplier_id IS INITIAL.
    MESSAGE 'Renseignez le fournisseur'(e06) TYPE 'E'.
  ENDIF.
  LOOP AT gt_items ASSIGNING FIELD-SYMBOL(<ls_item>).
    IF <ls_item>-article_id IS INITIAL.
      MESSAGE |Poste { <ls_item>-item_num } : article manquant| TYPE 'E'.
    ENDIF.
    IF <ls_item>-article_name IS INITIAL.
      SELECT SINGLE article_name FROM zret_t_article INTO <ls_item>-article_name
        WHERE article_id = <ls_item>-article_id.
      IF sy-subrc <> 0.
        MESSAGE |Poste { <ls_item>-item_num } : article { <ls_item>-article_id } inconnu| TYPE 'E'.
      ENDIF.
    ENDIF.
    IF <ls_item>-quantity <= 0.
      MESSAGE |Poste { <ls_item>-item_num } : quantité invalide| TYPE 'E'.
    ENDIF.
    IF <ls_item>-unit_price <= 0.
      MESSAGE |Poste { <ls_item>-item_num } : prix invalide| TYPE 'E'.
    ENDIF.
    IF <ls_item>-quantity < <ls_item>-delivered_qty.
      MESSAGE |Poste { <ls_item>-item_num } : quantité inférieure au livré| TYPE 'E'.
    ENDIF.
    PERFORM recalc_item CHANGING <ls_item>.
  ENDLOOP.
  PERFORM recalc_header.
ENDFORM.

FORM save_po.
  DATA: lt_db TYPE STANDARD TABLE OF zret_t_po_item,
        ls_db TYPE zret_t_po_item,
        lv_n  TYPE i.
  LOOP AT gt_items INTO DATA(ls_i).
    CLEAR ls_db.
    MOVE-CORRESPONDING ls_i TO ls_db.
    ls_db-client    = sy-mandt.
    ls_db-po_number = zret_s_po_hdr-po_number.
    APPEND ls_db TO lt_db.
  ENDLOOP.
  lv_n = lines( lt_db ).
  MOVE-CORRESPONDING zret_s_po_hdr TO gs_po_db.
  gs_po_db-changed_by = sy-uname.
  gs_po_db-changed_on = sy-datum.
  MODIFY zret_t_po FROM gs_po_db.
  DELETE FROM zret_t_po_item WHERE po_number = zret_s_po_hdr-po_number.
  sy-subrc = 0.
  IF lt_db IS NOT INITIAL.
    INSERT zret_t_po_item FROM TABLE lt_db.
  ENDIF.
  IF sy-subrc = 0.
    COMMIT WORK.
    gv_changed = abap_false.
    gv_edit = abap_false.
    PERFORM set_fcat_edit.
    go_grid->set_frontend_fieldcatalog( gt_fcat ).
    go_grid->set_ready_for_input( 0 ).
    PERFORM refresh_grid.
    MESSAGE |Commande { zret_s_po_hdr-po_number } modifiée ({ lv_n } postes, total { zret_s_po_hdr-total_amount } { zret_s_po_hdr-currency })| TYPE 'S'.
  ELSE.
    ROLLBACK WORK.
    MESSAGE 'Erreur à la sauvegarde des postes'(e07) TYPE 'E'.
  ENDIF.
ENDFORM.
