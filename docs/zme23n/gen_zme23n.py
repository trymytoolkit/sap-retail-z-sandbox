# Génère tous les objets de ZME23N (package ZRET_MM) au format abapGit :
# structures, transaction, includes et module pool SAPMZRET_PO (dynpros + CUA).
# Repris du générateur ZMM01 avec les leçons apprises :
#  - sous-écran = TYPE I dans l'en-tête RPY_DYHEAD (pas S) ;
#  - custom container = conteneur CUST_CTRL (relevé sur RSDEMO_CUSTOM_CONTROL 0100) ;
#  - champ en sortie seule = OUTPUT_FLD X sans INPUT_FLD (pas de balise OUTPUTONLY) ;
#  - BACK/EXIT/CANC avec TYPE E dans RSMPE_FUNT ;
#  - lignes de flow logic <= 72 caractères.
# Lancer depuis la racine du dépôt : python3 -I docs/zme23n/gen_zme23n.py
import os
P = 'SAPMZRET_PO'
OUT = 'src/zret_mm'
HEAD = '﻿<?xml version="1.0" encoding="utf-8"?>\n<abapGit version="v1.0.0" serializer="{ser}" serializer_version="v1.0.0">\n <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">\n  <asx:values>\n'
TAIL = '  </asx:values>\n </asx:abap>\n</abapGit>\n'
def w(name, text):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8', newline='\n') as f: f.write(text)
def n3(v): return f'{int(v):03d}'
def tag(k, v): return f'       <{k}>{v}</{k}>\n'

# ---------------------------------------------------------------- structures
def dd03p(f):
    name, kind = f[0], f[1]
    x = '    <DD03P>\n' + f'     <FIELDNAME>{name}</FIELDNAME>\n     <ADMINFIELD>0</ADMINFIELD>\n'
    if kind == 'E':
        x = '    <DD03P>\n' + f'     <FIELDNAME>{name}</FIELDNAME>\n     <ROLLNAME>{f[2]}</ROLLNAME>\n     <ADMINFIELD>0</ADMINFIELD>\n     <COMPTYPE>E</COMPTYPE>\n'
    else:
        dt, leng, dec = f[2], f[3], (f[4] if len(f) > 4 else 0)
        inttype = {'CHAR': 'C', 'NUMC': 'N', 'DATS': 'D', 'DEC': 'P'}[dt]
        intlen = {'CHAR': leng * 2, 'NUMC': leng * 2, 'DATS': 16, 'DEC': leng // 2 + 1}[dt]
        x += f'     <INTTYPE>{inttype}</INTTYPE>\n     <INTLEN>{intlen:06d}</INTLEN>\n     <DATATYPE>{dt}</DATATYPE>\n     <LENG>{leng:06d}</LENG>\n'
        if dec: x += f'     <DECIMALS>{dec:06d}</DECIMALS>\n'
        x += f'     <MASK>  {dt}</MASK>\n'
    return x + '    </DD03P>\n'
def struct(name, text, fields):
    x = HEAD.format(ser='LCL_OBJECT_TABL')
    x += f'   <DD02V>\n    <TABNAME>{name}</TABNAME>\n    <DDLANGUAGE>E</DDLANGUAGE>\n    <TABCLASS>INTTAB</TABCLASS>\n    <DDTEXT>{text}</DDTEXT>\n    <MASTERLANG>E</MASTERLANG>\n    <EXCLASS>1</EXCLASS>\n   </DD02V>\n'
    x += '   <DD03P_TABLE>\n' + ''.join(dd03p(f) for f in fields) + '   </DD03P_TABLE>\n' + TAIL
    w(name.lower() + '.tabl.xml', x)
struct('ZRET_S_PO_HDR', 'Retail Z - PO header screen structure (ZME23N)', [
    ('PO_NUMBER', 'B', 'NUMC', 10), ('PO_DATE', 'B', 'DATS', 8), ('SUPPLIER_ID', 'B', 'CHAR', 10),
    ('SUPPLIER_NAME', 'B', 'CHAR', 40), ('SITE_ID', 'E', 'WERKS_D'), ('STATUS', 'E', 'ZRET_DE_PO_STATUS'),
    ('TOTAL_AMOUNT', 'B', 'DEC', 13, 2), ('CURRENCY', 'E', 'WAERS')])
struct('ZRET_S_PO_ITEM_ALV', 'Retail Z - PO item grid structure (ZME23N)', [
    ('ITEM_NUM', 'B', 'NUMC', 4), ('ARTICLE_ID', 'E', 'ZDE_RET_ARTICLE_ID'), ('ARTICLE_NAME', 'B', 'CHAR', 40),
    ('QUANTITY', 'B', 'DEC', 13, 3), ('BASE_UOM', 'B', 'CHAR', 3), ('UNIT_PRICE', 'B', 'DEC', 11, 2),
    ('LINE_AMOUNT', 'B', 'DEC', 13, 2), ('CURRENCY', 'E', 'WAERS'), ('DELIVERED_QTY', 'B', 'DEC', 13, 3),
    ('OPEN_QTY', 'B', 'DEC', 13, 3), ('FINAL_DELIVERY', 'E', 'ZDE_RET_ACTIVE_FLAG')])

# ---------------------------------------------------------------- transaction
w('zme23n.tran.xml', HEAD.format(ser='LCL_OBJECT_TRAN') + f'   <TSTC>\n    <TCODE>ZME23N</TCODE>\n    <PGMNA>{P}</PGMNA>\n    <DYPNO>0100</DYPNO>\n   </TSTC>\n   <TSTCC>\n    <TCODE>ZME23N</TCODE>\n   </TSTCC>\n   <TSTCT>\n    <SPRSL>E</SPRSL>\n    <TCODE>ZME23N</TCODE>\n    <TTEXT>Purchase order display/change (ME23N-style test bench)</TTEXT>\n   </TSTCT>\n' + TAIL)

# ---------------------------------------------------------------- includes
def progdir(name, subc, title):
    return HEAD.format(ser='LCL_OBJECT_PROG') + f'   <PROGDIR>\n    <NAME>{name}</NAME>\n    <DBAPL>S</DBAPL>\n    <SUBC>{subc}</SUBC>\n    <FIXPT>X</FIXPT>\n    <LDBNAME>D$S</LDBNAME>\n    <UCCHECK>X</UCCHECK>\n   </PROGDIR>\n'
def include(name, title, body, extra=''):
    w(name.lower() + '.prog.xml', progdir(name, 'I', title) + f'   <TPOOL>\n    <item>\n     <ID>R</ID>\n     <ENTRY>{title}</ENTRY>\n     <LENGTH>{len(title)}</LENGTH>\n    </item>\n   </TPOOL>\n' + TAIL)
    w(name.lower() + '.prog.abap', body)

include('MZRET_POTOP', 'ZME23N: global data', r'''*&---------------------------------------------------------------------*
*& Include MZRET_POTOP : données globales du module pool SAPMZRET_PO
*&---------------------------------------------------------------------*
PROGRAM sapmzret_po.

" En-tête affiché et poste en détail : structures du dictionnaire
TABLES: zret_s_po_hdr, zret_s_po_item_alv.

DATA: gs_po_db    TYPE zret_t_po,                       " état en base
      gt_items    TYPE STANDARD TABLE OF zret_s_po_item_alv,
      gv_loaded   TYPE abap_bool,
      gv_edit     TYPE abap_bool,                       " X = mode Modifier
      gv_changed  TYPE abap_bool,
      gv_hdr_open TYPE abap_bool VALUE 'X',             " en-tête déplié
      gs_item_shown TYPE zret_s_po_item_alv,            " détail tel qu'affiché au PBO
      gv_title    TYPE string,
      ok_code     TYPE sy-ucomm,
      gv_save_ok  TYPE sy-ucomm.

" Sous-écrans : en-tête (0110 déplié / 0111 replié), détail du poste (0120)
" et onglet actif du détail (0121 données, 0122 livraison)
DATA: gv_sub_hdr  TYPE sy-dynnr VALUE '0110',
      gv_sub_item TYPE sy-dynnr VALUE '0120',
      gv_sub_tab  TYPE sy-dynnr VALUE '0121'.
CONTROLS: ts_item TYPE TABSTRIP.

" Grille ALV des postes dans le custom container CC_ITEMS
CLASS lcl_po_alv DEFINITION DEFERRED.
DATA: go_cont    TYPE REF TO cl_gui_custom_container,
      go_grid    TYPE REF TO cl_gui_alv_grid,
      go_handler TYPE REF TO lcl_po_alv,
      gt_fcat    TYPE lvc_t_fcat.

CONSTANTS: gc_item_step TYPE n LENGTH 4 VALUE '0010'.
''')

include('MZRET_POO01', 'ZME23N: PBO modules', r'''*&---------------------------------------------------------------------*
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

" Détail du poste : resynchronisé depuis la grille (une saisie dans la
" grille doit se voir dans le détail), et mémorisé tel qu'affiché pour
" ne recopier au PAI que ce que l'utilisateur a réellement changé ici.
MODULE item_pbo OUTPUT.
  IF zret_s_po_item_alv-item_num IS NOT INITIAL.
    READ TABLE gt_items INTO DATA(ls_cur)
         WITH KEY item_num = zret_s_po_item_alv-item_num.
    IF sy-subrc = 0.
      zret_s_po_item_alv = ls_cur.
    ENDIF.
  ENDIF.
  gs_item_shown = zret_s_po_item_alv.
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
''')

include('MZRET_POI01', 'ZME23N: PAI modules', r'''*&---------------------------------------------------------------------*
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
  " Les saisies faites dans la grille ne sont transférées à gt_items qu'à
  " la demande : sans ce flush, Contrôler et Sauvegarder verraient les
  " anciennes valeurs (vécu : quantité 10 < livré 50 déclarée « sans erreur »).
  IF go_grid IS NOT INITIAL AND gv_edit = abap_true.
    go_grid->check_changed_data( ).
  ENDIF.
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
  " Seules les valeurs modifiées À L'ÉCRAN DU DÉTAIL sont recopiées : sinon
  " le détail (qui affiche encore l'ancienne valeur) écraserait une saisie
  " faite dans la grille (vécu : quantité 10 dans la grille, 50 dans le détail).
  CHECK zret_s_po_item_alv-quantity <> gs_item_shown-quantity
     OR zret_s_po_item_alv-unit_price <> gs_item_shown-unit_price
     OR zret_s_po_item_alv-final_delivery <> gs_item_shown-final_delivery.
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
''')

include('MZRET_POF01', 'ZME23N: forms and ALV handler class', r'''*&---------------------------------------------------------------------*
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
      i_structure_name   = 'ZRET_S_PO_ITEM_ALV'
      i_bypassing_buffer = 'X'
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
      WHEN 'ARTICLE_ID'.
        <ls_fcat>-edit = gv_edit.
      WHEN 'OPEN_QTY'.
        <ls_fcat>-coltext = 'Reste à livrer'(c01).
      WHEN 'ITEM_NUM'.      <ls_fcat>-coltext = 'Poste'(c03).
      WHEN 'ARTICLE_NAME'.  <ls_fcat>-coltext = 'Désignation'(c04).
      WHEN 'QUANTITY'.      <ls_fcat>-coltext = 'Quantité'(c05). <ls_fcat>-edit = gv_edit.
      WHEN 'BASE_UOM'.      <ls_fcat>-coltext = 'Unité'(c06).
        " Unité brute (les tables semées contiennent 'PC' en interne) :
        " pas d'exit de conversion, sinon ***** et message système à chaque PBO
        CLEAR: <ls_fcat>-convexit, <ls_fcat>-ref_table, <ls_fcat>-ref_field.
      WHEN 'UNIT_PRICE'.    <ls_fcat>-coltext = 'Prix unitaire'(c07). <ls_fcat>-edit = gv_edit.
      WHEN 'LINE_AMOUNT'.   <ls_fcat>-coltext = 'Montant'(c08).
      WHEN 'DELIVERED_QTY'. <ls_fcat>-coltext = 'Livré'(c09).
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
''')

# ---------------------------------------------------------------- main program
w('sapmzret_po.prog.abap', '''*&---------------------------------------------------------------------*
*& Module pool SAPMZRET_PO : purchase order display/change (ME23N-style)
*& Transaction ZME23N. Screens 0100 (main), 0110/0111 (header open/closed),
*& 0120 (item detail tabstrip), 0121 (item data), 0122 (delivery).
*&---------------------------------------------------------------------*
INCLUDE mzret_potop.
INCLUDE mzret_poo01.
INCLUDE mzret_poi01.
INCLUDE mzret_pof01.
''')
flows = {
'0100': '''PROCESS BEFORE OUTPUT.
  MODULE status_0100.
  MODULE init_grid.
  CALL SUBSCREEN sub_hdr INCLUDING 'SAPMZRET_PO' gv_sub_hdr.
  CALL SUBSCREEN sub_item INCLUDING 'SAPMZRET_PO' gv_sub_item.

PROCESS AFTER INPUT.
  MODULE exit_0100 AT EXIT-COMMAND.
  CALL SUBSCREEN sub_hdr.
  CALL SUBSCREEN sub_item.
  MODULE user_command_0100.
''',
'0110': '''PROCESS BEFORE OUTPUT.
  MODULE set_input.

PROCESS AFTER INPUT.
  MODULE hdr_pai.
''',
'0111': '''PROCESS BEFORE OUTPUT.

PROCESS AFTER INPUT.
''',
'0120': '''PROCESS BEFORE OUTPUT.
  CALL SUBSCREEN sub_tab INCLUDING 'SAPMZRET_PO' gv_sub_tab.

PROCESS AFTER INPUT.
  CALL SUBSCREEN sub_tab.
''',
'0121': '''PROCESS BEFORE OUTPUT.
  MODULE item_pbo.
  MODULE set_input.

PROCESS AFTER INPUT.
  MODULE item_pai.
''',
'0122': '''PROCESS BEFORE OUTPUT.
  MODULE item_pbo.
  MODULE set_input.

PROCESS AFTER INPUT.
  MODULE item_pai.
''',
}
for no, f in flows.items():
    for l in f.split('\n'): assert len(l) <= 72, l
    w(f'sapmzret_po.prog.screen_{no}.abap', f)

# ---------------------------------------------------------------- dynpros
def cont(type_, name, element_of='', line=0, col=0, length=0, height=0, resize=('', '', 0, 0), scroll=('', '')):
    x = '      <RPY_DYCATT>\n' + tag('TYPE', type_) + tag('NAME', name)
    if element_of: x += tag('ELEMENT_OF', element_of)
    if line or col or length or height:
        x += tag('LINE', n3(line)) + tag('COLUMN', n3(col)) + tag('LENGTH', n3(length)) + tag('HEIGHT', n3(height))
    if resize[0]: x += tag('C_RESIZE_V', 'X')
    if resize[1]: x += tag('C_RESIZE_H', 'X')
    if resize[2]: x += tag('C_LINE_MIN', n3(resize[2]))
    if resize[3]: x += tag('C_COLN_MIN', n3(resize[3]))
    if scroll[0]: x += tag('C_SCROLL_V', 'X')
    if scroll[1]: x += tag('C_SCROLL_H', 'X')
    return x + '      </RPY_DYCATT>\n'
def fld(ct, cn, type_, name, text='', line=0, col=0, length=0, vis=None, fmt='CHAR', io=False, out=False, req=False, fcode='', fromdict=False, ref='', group=''):
    vis = length if vis is None else vis
    x = '      <RPY_DYFATC>\n' + tag('CONT_TYPE', ct) + tag('CONT_NAME', cn) + tag('TYPE', type_) + tag('NAME', name)
    if text: x += tag('TEXT', text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
    x += tag('LINE', n3(line)) + tag('COLUMN', n3(col)) + tag('LENGTH', n3(length)) + tag('VISLENGTH', n3(vis)) + tag('HEIGHT', '001')
    if fcode: x += tag('PUSH_FCODE', fcode)
    x += tag('FORMAT', fmt)
    if fromdict: x += tag('FROM_DICT', 'X')
    if io: x += tag('INPUT_FLD', 'X') + tag('OUTPUT_FLD', 'X')
    elif out: x += tag('OUTPUT_FLD', 'X')
    if req: x += tag('REQU_ENTRY', 'X')
    if type_ == 'TEXT': x += tag('LABELLEFT', 'X')
    if ref: x += tag('REF_FIELD', ref)
    if group: x += tag('GROUP1', group)
    return x + '      </RPY_DYFATC>\n'
S = ('SCREEN', 'SCREEN')
_n = [0]
def lab(text, line, col, length=None):
    _n[0] += 1
    return fld(*S, 'TEXT', '%#AUTOTEXT' + n3(_n[0]), text, line, col, length or len(text))
def tmpl(name, line, col, length, vis=None, fmt='CHAR', out=False, req=False, group=''):
    return fld(*S, 'TEMPLATE', name, '_' * (vis or length), line, col, length, vis, fmt, io=not out, out=out, req=req, fromdict=True, group=group)
OK = fld(*S, 'OKCODE', 'OK_CODE', '_' * 20, 0, 0, 20).replace('      </RPY_DYFATC>\n', '       <INPUT_FLD>X</INPUT_FLD>\n      </RPY_DYFATC>\n')
def screen(no, descr, type_, lines, cols, containers, fields):
    x = '    <item>\n     <HEADER>\n' + f'      <PROGRAM>{P}</PROGRAM>\n      <SCREEN>{no}</SCREEN>\n      <LANGUAGE>E</LANGUAGE>\n      <DESCRIPT>{descr}</DESCRIPT>\n      <TYPE>{type_}</TYPE>\n      <NEXTSCREEN>{no}</NEXTSCREEN>\n      <LINES>{n3(lines)}</LINES>\n      <COLUMNS>{n3(cols)}</COLUMNS>\n     </HEADER>\n'
    x += '     <CONTAINERS>\n' + cont('SCREEN', 'SCREEN') + ''.join(containers) + '     </CONTAINERS>\n'
    x += '     <FIELDS>\n' + ''.join(fields) + '     </FIELDS>\n'
    flow = flows[no].rstrip('\n').split('\n')
    x += '     <FLOW_LOGIC>\n' + ''.join(f'      <RPY_DYFLOW>\n       <LINE>{l.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}</LINE>\n      </RPY_DYFLOW>\n' if l.strip() else '      <RPY_DYFLOW/>\n' for l in flow) + '     </FLOW_LOGIC>\n'
    return x + '    </item>\n'

# 0100 : barre de sélection, en-tête (sous-écran), grille (custom control), détail (sous-écran)
s0100 = screen('0100', 'ZME23N: purchase order (main screen)', 'N', 32, 120, [
    cont('SUBSCREEN', 'SUB_HDR', 'SCREEN', 3, 1, 118, 6, resize=('X', 'X', 2, 20), scroll=('', '')),
    cont('CUST_CTRL', 'CC_ITEMS', 'SCREEN', 10, 1, 118, 11, resize=('X', 'X', 5, 20)),
    cont('SUBSCREEN', 'SUB_ITEM', 'SCREEN', 22, 1, 118, 9, resize=('X', 'X', 4, 20))], [
    lab('Purchase order', 1, 1, 15), tmpl('ZRET_S_PO_HDR-PO_NUMBER', 1, 17, 10, fmt='NUMC'),
    fld(*S, 'PUSH', 'BTN_OTHER', 'Other PO', 1, 29, 12, fcode='OTHER'),
    fld(*S, 'PUSH', 'BTN_EDIT', 'Display/Change', 1, 43, 16, fcode='TOGGLE'),
    fld(*S, 'PUSH', 'BTN_HDR', 'Header', 1, 65, 10, fcode='HDR_TOGGLE'),
    fld(*S, 'PUSH', 'BTN_CHECK', 'Check', 1, 77, 10, fcode='CHECK'), OK])
# 0110 : en-tête déplié
s0110 = screen('0110', 'ZME23N: header (expanded)', 'I', 6, 118, [], [
    lab('Supplier', 1, 1, 14), tmpl('ZRET_S_PO_HDR-SUPPLIER_ID', 1, 16, 10, group='EDT'),
    tmpl('ZRET_S_PO_HDR-SUPPLIER_NAME', 1, 28, 40, out=True),
    lab('Site', 2, 1, 14), tmpl('ZRET_S_PO_HDR-SITE_ID', 2, 16, 4, group='EDT'),
    lab('PO date', 3, 1, 14), tmpl('ZRET_S_PO_HDR-PO_DATE', 3, 16, 10, fmt='DATS', group='EDT'),
    lab('Currency', 4, 1, 14), tmpl('ZRET_S_PO_HDR-CURRENCY', 4, 16, 5, fmt='CUKY', out=True),
    lab('Status', 2, 40, 10), tmpl('ZRET_S_PO_HDR-STATUS', 2, 52, 1, out=True),
    lab('Total', 3, 40, 10), tmpl('ZRET_S_PO_HDR-TOTAL_AMOUNT', 3, 52, 17, fmt='DEC', out=True)])
# 0111 : en-tête replié
s0111 = screen('0111', 'ZME23N: header (collapsed)', 'I', 2, 118, [], [lab('Header collapsed', 1, 1, 20)])
# 0120 : tabstrip du détail
TS = ('STRIP_CTRL', 'TS_ITEM')
s0120 = screen('0120', 'ZME23N: item detail (tabstrip)', 'I', 9, 118, [
    cont('STRIP_CTRL', 'TS_ITEM', 'SCREEN', 1, 1, 116, 8, resize=('X', 'X', 4, 20)),
    cont('SUBSCREEN', 'SUB_TAB', 'TS_ITEM', 3, 2, 112, 6, resize=('X', 'X', 3, 8), scroll=('X', 'X'))], [
    fld(*TS, 'PUSH', 'TABI1', 'Item data', 1, 1, 14, fcode='TABI1', ref='SUB_TAB'),
    fld(*TS, 'PUSH', 'TABI2', 'Delivery', 1, 2, 12, fcode='TABI2', ref='SUB_TAB')])
# 0121 : données du poste
s0121 = screen('0121', 'ZME23N: item data', 'I', 6, 112, [], [
    lab('Item', 1, 1, 12), tmpl('ZRET_S_PO_ITEM_ALV-ITEM_NUM', 1, 14, 4, fmt='NUMC', out=True),
    lab('Article', 2, 1, 12), tmpl('ZRET_S_PO_ITEM_ALV-ARTICLE_ID', 2, 14, 10, out=True),
    tmpl('ZRET_S_PO_ITEM_ALV-ARTICLE_NAME', 2, 26, 40, out=True),
    lab('Quantity', 3, 1, 12), tmpl('ZRET_S_PO_ITEM_ALV-QUANTITY', 3, 14, 17, fmt='DEC', group='EDT'),
    tmpl('ZRET_S_PO_ITEM_ALV-BASE_UOM', 3, 32, 3, out=True),
    lab('Unit price', 4, 1, 12), tmpl('ZRET_S_PO_ITEM_ALV-UNIT_PRICE', 4, 14, 14, fmt='DEC', group='EDT'),
    lab('Line amount', 5, 1, 12), tmpl('ZRET_S_PO_ITEM_ALV-LINE_AMOUNT', 5, 14, 17, fmt='DEC', out=True)])
# 0122 : livraison
s0122 = screen('0122', 'ZME23N: item delivery', 'I', 6, 112, [], [
    lab('Delivered', 1, 1, 14), tmpl('ZRET_S_PO_ITEM_ALV-DELIVERED_QTY', 1, 16, 17, fmt='DEC', out=True),
    lab('Open quantity', 2, 1, 14), tmpl('ZRET_S_PO_ITEM_ALV-OPEN_QTY', 2, 16, 17, fmt='DEC', out=True),
    fld(*S, 'CHECK', 'ZRET_S_PO_ITEM_ALV-FINAL_DELIVERY', 'Final', 3, 16, 7, io=True, fromdict=True, group='EDT')])

# ---------------------------------------------------------------- CUA
funs = [('SAVE', 'Save', 'ICON_SYSTEM_SAVE', '@2L@'), ('BACK', 'Back', '', ''), ('EXIT', 'Exit', '', ''),
        ('CANC', 'Cancel', 'ICON_CANCEL', '@0W@'), ('CHECK', 'Check', 'ICON_CHECK', '@01@'), ('ENTER', 'Enter', '', '')]
def funt(c, t, tn, ic):
    x = f'     <RSMPE_FUNT>\n      <CODE>{c}</CODE>\n      <TEXTNO>001</TEXTNO>\n'
    if c in ('BACK', 'EXIT', 'CANC'): x += '      <TYPE>E</TYPE>\n'
    x += '      <TEXT_TYPE>S</TEXT_TYPE>\n'
    if tn: x += f'      <TEXT_NAME>{tn}</TEXT_NAME>\n      <ICON_ID>{ic}</ICON_ID>\n'
    return x + f'      <FUN_TEXT>{t}</FUN_TEXT>\n     </RSMPE_FUNT>\n'
pfk = [('00', 'ENTER'), ('03', 'BACK'), ('11', 'SAVE'), ('12', 'CANC'), ('15', 'EXIT'), ('25', 'CHECK')]
cua = '   <CUA>\n    <ADM>\n     <ACTCODE>000001</ACTCODE>\n     <PFKCODE>000001</PFKCODE>\n    </ADM>\n    <STA>\n     <RSMPE_STAT>\n      <CODE>MAIN</CODE>\n      <MODAL>D</MODAL>\n      <ACTCODE>000001</ACTCODE>\n      <PFKCODE>000001</PFKCODE>\n      <BUTCODE>0001</BUTCODE>\n      <INT_NOTE>ZME23N main status</INT_NOTE>\n     </RSMPE_STAT>\n    </STA>\n'
cua += '    <FUN>\n' + ''.join(funt(*f) for f in funs) + '    </FUN>\n'
cua += '    <BUT>\n' + ''.join(f'     <RSMPE_BUT>\n      <PFK_CODE>000001</PFK_CODE>\n      <CODE>0001</CODE>\n      <NO>{no}</NO>\n      <PFNO>{pf}</PFNO>\n     </RSMPE_BUT>\n' for no, pf in [('01', '11'), ('02', '25'), ('03', '03'), ('04', '15'), ('05', '12')]) + '    </BUT>\n'
cua += '    <PFK>\n' + ''.join(f'     <RSMPE_PFK>\n      <CODE>000001</CODE>\n      <PFNO>{pf}</PFNO>\n      <FUNCODE>{fc}</FUNCODE>\n      <FUNNO>001</FUNNO>\n     </RSMPE_PFK>\n' for pf, fc in pfk) + '    </PFK>\n'
cua += '    <SET>\n' + ''.join(f'     <RSMPE_STAF>\n      <STATUS>MAIN</STATUS>\n      <FUNCTION>{f[0]}</FUNCTION>\n     </RSMPE_STAF>\n' for f in funs) + '    </SET>\n'
cua += '    <DOC>\n' + ''.join(f'     <RSMPE_ATRT>\n      <OBJ_TYPE>{t}</OBJ_TYPE>\n      <OBJ_CODE>000001</OBJ_CODE>\n{sub}      <MODAL>D</MODAL>\n      <INT_NOTE>ZME23N main status</INT_NOTE>\n     </RSMPE_ATRT>\n' for t, sub in [('A', ''), ('P', ''), ('B', '      <SUB_CODE>0001</SUB_CODE>\n')]) + '    </DOC>\n'
cua += '    <TIT>\n     <RSMPE_TITT>\n      <CODE>T_MAIN</CODE>\n      <TEXT>&amp;1</TEXT>\n     </RSMPE_TITT>\n    </TIT>\n   </CUA>\n'
title = 'ZME23N: purchase order display/change (ME23N-style test bench)'
xml = progdir(P, 'M', title)
xml += '   <DYNPROS>\n' + s0100 + s0110 + s0111 + s0120 + s0121 + s0122 + '   </DYNPROS>\n' + cua
xml += f'   <TPOOL>\n    <item>\n     <ID>R</ID>\n     <ENTRY>{title}</ENTRY>\n     <LENGTH>{len(title)}</LENGTH>\n    </item>\n   </TPOOL>\n' + TAIL
w('sapmzret_po.prog.xml', xml)
print('ok', len(xml))
