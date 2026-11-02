*&---------------------------------------------------------------------*
*& Include MZRET_GMF01 : formes
*&---------------------------------------------------------------------*
" Charge les postes depuis la référence (v1 : réception sur commande d'achat)
FORM load_reference.
  DATA: ls_po    TYPE zret_t_po,
        lt_poi   TYPE STANDARD TABLE OF zret_t_po_item,
        ls_item  TYPE zret_s_gm_item,
        lv_open  TYPE zret_t_po_item-quantity.
  IF zret_s_gm_hdr-action <> 'A01' OR zret_s_gm_hdr-reftype <> 'R01'.
    MESSAGE 'Ce banc d''essai ne couvre que Réception + Commande d''achat (A01 / R01)'(e01) TYPE 'S' DISPLAY LIKE 'E'.
    RETURN.
  ENDIF.
  IF zret_s_gm_hdr-ref_doc IS INITIAL.
    MESSAGE 'Renseignez le numéro de commande'(e02) TYPE 'S' DISPLAY LIKE 'E'.
    RETURN.
  ENDIF.
  SELECT SINGLE * FROM zret_t_po INTO ls_po WHERE po_number = zret_s_gm_hdr-ref_doc.
  IF sy-subrc <> 0.
    MESSAGE |Commande { zret_s_gm_hdr-ref_doc } inexistante| TYPE 'S' DISPLAY LIKE 'E'.
    RETURN.
  ENDIF.
  IF ls_po-status <> 'O' AND ls_po-status <> 'I'.
    MESSAGE |Commande { zret_s_gm_hdr-ref_doc } au statut { ls_po-status } : pas de réception possible| TYPE 'S' DISPLAY LIKE 'E'.
    RETURN.
  ENDIF.
  CLEAR: gt_items, gv_detail_idx.
  SELECT * FROM zret_t_po_item INTO TABLE lt_poi
    WHERE po_number = zret_s_gm_hdr-ref_doc ORDER BY item_num.
  LOOP AT lt_poi INTO DATA(ls_poi).
    lv_open = ls_poi-quantity - ls_poi-delivered_qty.
    CHECK lv_open > 0.
    CLEAR ls_item.
    ls_item-item_num     = ls_poi-item_num.
    ls_item-article_id   = ls_poi-article_id.
    ls_item-article_name = ls_poi-article_name.
    ls_item-quantity     = lv_open.
    ls_item-stock_avail  = lv_open.
    ls_item-base_uom     = ls_poi-base_uom.
    ls_item-dst_zone     = 'RECV'.
    ls_item-mvt_type     = '101'.
    APPEND ls_item TO gt_items.
  ENDLOOP.
  IF gt_items IS INITIAL.
    MESSAGE |Commande { zret_s_gm_hdr-ref_doc } : tous les postes sont déjà réceptionnés| TYPE 'S' DISPLAY LIKE 'E'.
    RETURN.
  ENDIF.
  zret_s_gm_hdr-posting_date = sy-datum.
  zret_s_gm_hdr-site_id      = ls_po-site_id.
  zret_s_gm_hdr-nb_items     = lines( gt_items ).
  zret_s_gm_hdr-created_by   = sy-uname.
  zret_s_gm_hdr-po_status    = ls_po-status.
  gv_loaded = abap_true.
  gv_changed = abap_false.
  gv_detail_idx = 1.
  ts_hdr-activetab = 'TABH1'.
  ts_item-activetab = 'TABI1'.
  MESSAGE |Commande { zret_s_gm_hdr-ref_doc } : { lines( gt_items ) } poste(s) à réceptionner| TYPE 'S'.
ENDFORM.

" Contrôle des postes cochés : colonne Message par ligne, bilan en statut.
" Les refus passent en S DISPLAY LIKE E pour laisser l'écran saisissable.
FORM check_items.
  DATA: lv_ok  TYPE i,
        lv_err TYPE i.
  IF gv_loaded = abap_false.
    MESSAGE 'Chargez d''abord une référence (Exécuter)'(e03) TYPE 'S' DISPLAY LIKE 'E'.
    RETURN.
  ENDIF.
  LOOP AT gt_items ASSIGNING FIELD-SYMBOL(<ls_item>).
    CLEAR <ls_item>-message.
    CHECK <ls_item>-item_ok = abap_true.
    IF <ls_item>-quantity <= 0.
      <ls_item>-message = 'Quantité invalide'(m01).
    ELSEIF <ls_item>-quantity > <ls_item>-stock_avail.
      <ls_item>-message = |Quantité supérieure au reste à livrer : { <ls_item>-stock_avail }|.
    ELSEIF <ls_item>-dst_zone <> 'RECV'.
      <ls_item>-message = 'Zone de destination invalide (RECV attendu)'(m02).
    ELSE.
      <ls_item>-message = 'OK'(m03).
      lv_ok = lv_ok + 1.
      CONTINUE.
    ENDIF.
    lv_err = lv_err + 1.
  ENDLOOP.
  IF lv_ok = 0 AND lv_err = 0.
    MESSAGE 'Aucun poste sélectionné : cochez les postes à comptabiliser'(i01) TYPE 'I'.
    RETURN.
  ENDIF.
  IF lv_err > 0.
    MESSAGE |{ lv_err } poste(s) en erreur, voir la colonne Message| TYPE 'S' DISPLAY LIKE 'E'.
  ELSE.
    MESSAGE |Document contrôlé, { lv_ok } poste(s) prêt(s)| TYPE 'S'.
  ENDIF.
ENDFORM.

" Comptabilisation : même contrôle, puis réception poste par poste via la
" classe métier (mouvement 101 en RECV, mise à jour de la commande, tâche
" de rangement). Le numéro du premier mouvement sert de numéro de document.
FORM post_items.
  DATA: lv_n     TYPE i,
        lv_err   TYPE i,
        ls_mvt   TYPE zcl_ret_stock=>ts_mvt_result,
        lv_first TYPE zret_t_stk_mvt-mvt_doc.
  IF gv_loaded = abap_false.
    MESSAGE 'Chargez d''abord une référence (Exécuter)'(e03) TYPE 'S' DISPLAY LIKE 'E'.
    RETURN.
  ENDIF.
  PERFORM check_items.
  LOOP AT gt_items INTO DATA(ls_chk) WHERE item_ok = abap_true.
    IF ls_chk-message <> 'OK'(m03).
      lv_err = lv_err + 1.
    ENDIF.
  ENDLOOP.
  IF lv_err > 0.
    MESSAGE |Comptabilisation refusée : { lv_err } poste(s) en erreur| TYPE 'S' DISPLAY LIKE 'E'.
    RETURN.
  ENDIF.
  LOOP AT gt_items INTO DATA(ls_item) WHERE item_ok = abap_true.
    TRY.
        ls_mvt = zcl_ret_purch_order=>post_goods_receipt(
          iv_po_number    = zret_s_gm_hdr-ref_doc
          iv_item_num     = ls_item-item_num
          iv_qty_received = ls_item-quantity ).
        IF lv_first IS INITIAL.
          lv_first = ls_mvt-mvt_doc.
        ENDIF.
        lv_n = lv_n + 1.
      CATCH zcx_ret_core INTO DATA(lo_ex).
        MESSAGE |Poste { ls_item-item_num } : { lo_ex->get_text( ) }| TYPE 'S' DISPLAY LIKE 'E'.
        RETURN.
    ENDTRY.
  ENDLOOP.
  IF lv_n = 0.
    MESSAGE 'Aucun poste sélectionné : cochez les postes à comptabiliser'(i01) TYPE 'I'.
    RETURN.
  ENDIF.
  gv_last_doc = lv_first.
  CLEAR: gt_items, gv_detail_idx.
  gv_loaded = abap_false.
  gv_changed = abap_false.
  MESSAGE |Document matière { lv_first } comptabilisé ({ lv_n } poste(s)) sur commande { zret_s_gm_hdr-ref_doc }| TYPE 'S'.
ENDFORM.
