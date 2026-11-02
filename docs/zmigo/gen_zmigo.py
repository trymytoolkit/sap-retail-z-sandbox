# Génère tous les objets de ZMIGO (package ZRET_WHSE) au format abapGit :
# structures, transaction, includes et module pool SAPMZRET_GM (dynpros + CUA).
# Même socle que gen_zme23n.py (leçons ZMM01/ZME23N appliquées d'emblée).
# Version 1 : réception de marchandises sur commande d'achat (A01 + R01),
# table control (pas une grille ALV : on couvre l'autre famille), en-tête et
# détail en tabstrips, Contrôler puis Comptabiliser.
# Lancer depuis la racine du dépôt : python3 -I docs/zmigo/gen_zmigo.py
import os
P = 'SAPMZRET_GM'
OUT = 'src/zret_whse'
HEAD = '﻿<?xml version="1.0" encoding="utf-8"?>\n<abapGit version="v1.0.0" serializer="{ser}" serializer_version="v1.0.0">\n <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">\n  <asx:values>\n'
TAIL = '  </asx:values>\n </asx:abap>\n</abapGit>\n'
def w(name, text):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8', newline='\n') as f: f.write(text)
def n3(v): return f'{int(v):03d}'
def tag(k, v): return f'       <{k}>{v}</{k}>\n'

# ---------------------------------------------------------------- structures
def dd03p(f):
    name, kind = f[0], f[1]
    if kind == 'E':
        return '    <DD03P>\n' + f'     <FIELDNAME>{name}</FIELDNAME>\n     <ROLLNAME>{f[2]}</ROLLNAME>\n     <ADMINFIELD>0</ADMINFIELD>\n     <COMPTYPE>E</COMPTYPE>\n    </DD03P>\n'
    dt, leng, dec = f[2], f[3], (f[4] if len(f) > 4 else 0)
    inttype = {'CHAR': 'C', 'NUMC': 'N', 'DATS': 'D', 'DEC': 'P'}[dt]
    intlen = {'CHAR': leng * 2, 'NUMC': leng * 2, 'DATS': 16, 'DEC': leng // 2 + 1}[dt]
    x = '    <DD03P>\n' + f'     <FIELDNAME>{name}</FIELDNAME>\n     <ADMINFIELD>0</ADMINFIELD>\n'
    x += f'     <INTTYPE>{inttype}</INTTYPE>\n     <INTLEN>{intlen:06d}</INTLEN>\n     <DATATYPE>{dt}</DATATYPE>\n     <LENG>{leng:06d}</LENG>\n'
    if dec: x += f'     <DECIMALS>{dec:06d}</DECIMALS>\n'
    return x + f'     <MASK>  {dt}</MASK>\n    </DD03P>\n'
def struct(name, text, fields):
    x = HEAD.format(ser='LCL_OBJECT_TABL')
    x += f'   <DD02V>\n    <TABNAME>{name}</TABNAME>\n    <DDLANGUAGE>E</DDLANGUAGE>\n    <TABCLASS>INTTAB</TABCLASS>\n    <DDTEXT>{text}</DDTEXT>\n    <MASTERLANG>E</MASTERLANG>\n    <EXCLASS>1</EXCLASS>\n   </DD02V>\n'
    x += '   <DD03P_TABLE>\n' + ''.join(dd03p(f) for f in fields) + '   </DD03P_TABLE>\n' + TAIL
    w(name.lower() + '.tabl.xml', x)
struct('ZRET_S_GM_HDR', 'Retail Z - Goods movement header screen structure (ZMIGO)', [
    ('ACTION', 'B', 'CHAR', 3), ('REFTYPE', 'B', 'CHAR', 3), ('REF_DOC', 'B', 'NUMC', 10),
    ('POSTING_DATE', 'B', 'DATS', 8), ('SITE_ID', 'E', 'WERKS_D'), ('HEADER_TEXT', 'B', 'CHAR', 40),
    ('NB_ITEMS', 'B', 'NUMC', 3), ('CREATED_BY', 'B', 'CHAR', 12), ('PO_STATUS', 'B', 'CHAR', 1)])
struct('ZRET_S_GM_ITEM', 'Retail Z - Goods movement item screen structure (ZMIGO)', [
    ('MARK', 'B', 'CHAR', 1), ('ITEM_NUM', 'B', 'NUMC', 4), ('ITEM_OK', 'E', 'ZDE_RET_ACTIVE_FLAG'),
    ('ARTICLE_ID', 'E', 'ZDE_RET_ARTICLE_ID'), ('ARTICLE_NAME', 'B', 'CHAR', 40), ('QUANTITY', 'B', 'DEC', 13, 3),
    ('BASE_UOM', 'B', 'CHAR', 3), ('SRC_ZONE', 'B', 'CHAR', 10), ('DST_ZONE', 'B', 'CHAR', 10),
    ('MVT_TYPE', 'B', 'CHAR', 3), ('STOCK_AVAIL', 'B', 'DEC', 13, 3), ('MESSAGE', 'B', 'CHAR', 60),
    ('HU_ID', 'B', 'CHAR', 20), ('BATCH', 'B', 'CHAR', 10)])

# ---------------------------------------------------------------- transaction
w('zmigo.tran.xml', HEAD.format(ser='LCL_OBJECT_TRAN') + f'   <TSTC>\n    <TCODE>ZMIGO</TCODE>\n    <PGMNA>{P}</PGMNA>\n    <DYPNO>0100</DYPNO>\n   </TSTC>\n   <TSTCC>\n    <TCODE>ZMIGO</TCODE>\n   </TSTCC>\n   <TSTCT>\n    <SPRSL>E</SPRSL>\n    <TCODE>ZMIGO</TCODE>\n    <TTEXT>Goods movement (MIGO-style test bench)</TTEXT>\n   </TSTCT>\n' + TAIL)

# ---------------------------------------------------------------- includes
def progdir(name, subc):
    return HEAD.format(ser='LCL_OBJECT_PROG') + f'   <PROGDIR>\n    <NAME>{name}</NAME>\n    <DBAPL>S</DBAPL>\n    <SUBC>{subc}</SUBC>\n    <FIXPT>X</FIXPT>\n    <LDBNAME>D$S</LDBNAME>\n    <UCCHECK>X</UCCHECK>\n   </PROGDIR>\n'
def include(name, title, body):
    w(name.lower() + '.prog.xml', progdir(name, 'I') + f'   <TPOOL>\n    <item>\n     <ID>R</ID>\n     <ENTRY>{title}</ENTRY>\n     <LENGTH>{len(title)}</LENGTH>\n    </item>\n   </TPOOL>\n' + TAIL)
    w(name.lower() + '.prog.abap', body)

include('MZRET_GMTOP', 'ZMIGO: global data', r'''*&---------------------------------------------------------------------*
*& Include MZRET_GMTOP : données globales du module pool SAPMZRET_GM
*&---------------------------------------------------------------------*
PROGRAM sapmzret_gm.

" En-tête et ligne de table control / détail : structures du dictionnaire
TABLES: zret_s_gm_hdr, zret_s_gm_item.

DATA: gt_items      TYPE STANDARD TABLE OF zret_s_gm_item,
      gs_item       TYPE zret_s_gm_item,
      gs_item_shown TYPE zret_s_gm_item,          " détail tel qu'affiché au PBO
      gv_detail_idx TYPE i,                       " ligne de gt_items montrée en détail
      gv_loaded     TYPE abap_bool,
      gv_changed    TYPE abap_bool,
      gv_title      TYPE string,
      gv_last_doc   TYPE zret_t_stk_mvt-mvt_doc,
      ok_code       TYPE sy-ucomm,
      gv_save_ok    TYPE sy-ucomm.

" Table control des postes
CONTROLS: tc_items TYPE TABLEVIEW USING SCREEN 0100.
CONSTANTS: gc_lines_min TYPE i VALUE 6.

" Sous-écrans : en-tête 0110 (tabstrip TS_HDR -> 0111 / 0112),
" détail 0120 (tabstrip TS_ITEM -> 0121 / 0122 / 0123)
CONTROLS: ts_hdr  TYPE TABSTRIP,
          ts_item TYPE TABSTRIP.
DATA: gv_sub_hdr  TYPE sy-dynnr VALUE '0110',
      gv_sub_htab TYPE sy-dynnr VALUE '0111',
      gv_sub_item TYPE sy-dynnr VALUE '0120',
      gv_sub_itab TYPE sy-dynnr VALUE '0121'.
''')

include('MZRET_GMO01', 'ZMIGO: PBO modules', r'''*&---------------------------------------------------------------------*
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
''')

include('MZRET_GMI01', 'ZMIGO: PAI modules', r'''*&---------------------------------------------------------------------*
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
''')

include('MZRET_GMF01', 'ZMIGO: forms', r'''*&---------------------------------------------------------------------*
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
''')

# ---------------------------------------------------------------- main program + flow logic
w('sapmzret_gm.prog.abap', '''*&---------------------------------------------------------------------*
*& Module pool SAPMZRET_GM : goods movement (MIGO-style test bench)
*& Transaction ZMIGO. Screens 0100 (main), 0110/0111/0112 (header),
*& 0120/0121/0122/0123 (item detail).
*&---------------------------------------------------------------------*
INCLUDE mzret_gmtop.
INCLUDE mzret_gmo01.
INCLUDE mzret_gmi01.
INCLUDE mzret_gmf01.
''')
flows = {
'0100': '''PROCESS BEFORE OUTPUT.
  MODULE status_0100.
  MODULE init_listboxes.
  MODULE tc_init.
  LOOP AT gt_items INTO gs_item
       WITH CONTROL tc_items
       CURSOR tc_items-current_line.
    MODULE tc_pbo.
  ENDLOOP.
  CALL SUBSCREEN sub_hdr INCLUDING 'SAPMZRET_GM' gv_sub_hdr.
  CALL SUBSCREEN sub_item INCLUDING 'SAPMZRET_GM' gv_sub_item.

PROCESS AFTER INPUT.
  MODULE exit_0100 AT EXIT-COMMAND.
  LOOP AT gt_items.
    MODULE tc_pai.
  ENDLOOP.
  CALL SUBSCREEN sub_hdr.
  CALL SUBSCREEN sub_item.
  MODULE user_command_0100.
''',
'0110': '''PROCESS BEFORE OUTPUT.
  CALL SUBSCREEN sub_htab INCLUDING 'SAPMZRET_GM' gv_sub_htab.

PROCESS AFTER INPUT.
  CALL SUBSCREEN sub_htab.
''',
'0111': '''PROCESS BEFORE OUTPUT.

PROCESS AFTER INPUT.
''',
'0112': '''PROCESS BEFORE OUTPUT.

PROCESS AFTER INPUT.
''',
'0120': '''PROCESS BEFORE OUTPUT.
  CALL SUBSCREEN sub_itab INCLUDING 'SAPMZRET_GM' gv_sub_itab.

PROCESS AFTER INPUT.
  CALL SUBSCREEN sub_itab.
''',
'0121': '''PROCESS BEFORE OUTPUT.
  MODULE item_pbo.

PROCESS AFTER INPUT.
  MODULE item_pai.
''',
'0122': '''PROCESS BEFORE OUTPUT.
  MODULE item_pbo.

PROCESS AFTER INPUT.
  MODULE item_pai.
''',
'0123': '''PROCESS BEFORE OUTPUT.
  MODULE item_pbo.

PROCESS AFTER INPUT.
  MODULE item_pai.
''',
}
for no, f in flows.items():
    for l in f.split('\n'): assert len(l) <= 72, l
    w(f'sapmzret_gm.prog.screen_{no}.abap', f)

# ---------------------------------------------------------------- dynpros
def cont(type_, name, element_of='', line=0, col=0, length=0, height=0, resize=('', '', 0, 0), scroll=('', ''), tc=None):
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
    if tc:
        x += tag('TC_TABTYPE', 'ENTRY') + tag('TC_SEPAR_V', 'X') + tag('TC_SEPAR_H', 'X') + tag('TC_HEADER', 'X') + tag('TC_CONFIG', 'X')
        x += tag('TC_SEL_LNS', 'MULTIPLE') + tag('TC_SEL_CLS', 'NONE') + tag('TC_LSEL_CL', 'X') + tag('TC_FIXCOL', n3(tc))
    return x + '      </RPY_DYCATT>\n'
def esc(t): return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
def fld(ct, cn, type_, name, text='', line=0, col=0, length=0, vis=None, fmt='CHAR', io=False, out=False, req=False, fcode='', fromdict=False, ref='', group='', dd=False, tc_head=False, tc_sel=False):
    vis = length if vis is None else vis
    x = '      <RPY_DYFATC>\n' + tag('CONT_TYPE', ct) + tag('CONT_NAME', cn) + tag('TYPE', type_) + tag('NAME', name)
    if text: x += tag('TEXT', esc(text))
    if dd: x += tag('DROPDOWN', 'L')
    x += tag('LINE', n3(line)) + tag('COLUMN', n3(col)) + tag('LENGTH', n3(length)) + tag('VISLENGTH', n3(vis)) + tag('HEIGHT', '001')
    if fcode: x += tag('PUSH_FCODE', fcode)
    x += tag('FORMAT', fmt)
    if fromdict: x += tag('FROM_DICT', 'X')
    if io: x += tag('INPUT_FLD', 'X') + tag('OUTPUT_FLD', 'X')
    elif out: x += tag('OUTPUT_FLD', 'X')
    if req: x += tag('REQU_ENTRY', 'X')
    if type_ == 'TEXT' and not tc_head: x += tag('LABELLEFT', 'X')
    if ref: x += tag('REF_FIELD', ref)
    if group: x += tag('GROUP1', group)
    if tc_head: x += tag('TC_HEADING', 'X')
    if tc_sel: x += tag('TC_SELCOL', 'X')
    return x + '      </RPY_DYFATC>\n'
S = ('SCREEN', 'SCREEN')
_n = [0]
def lab(text, line, col, length=None):
    _n[0] += 1
    return fld(*S, 'TEXT', '%#AUTOTEXT' + n3(_n[0]), text, line, col, length or len(text))
def tmpl(name, line, col, length, vis=None, fmt='CHAR', out=False, req=False, group='', dd=False):
    return fld(*S, 'TEMPLATE', name, '_' * (vis or length), line, col, length, vis, fmt, io=not out, out=out, req=req, fromdict=True, group=group, dd=dd)
OK = fld(*S, 'OKCODE', 'OK_CODE', '_' * 20, 0, 0, 20).replace('      </RPY_DYFATC>\n', '       <INPUT_FLD>X</INPUT_FLD>\n      </RPY_DYFATC>\n')
def screen(no, descr, type_, lines, cols, containers, fields):
    x = '    <item>\n     <HEADER>\n' + f'      <PROGRAM>{P}</PROGRAM>\n      <SCREEN>{no}</SCREEN>\n      <LANGUAGE>E</LANGUAGE>\n      <DESCRIPT>{descr}</DESCRIPT>\n      <TYPE>{type_}</TYPE>\n      <NEXTSCREEN>{no}</NEXTSCREEN>\n      <LINES>{n3(lines)}</LINES>\n      <COLUMNS>{n3(cols)}</COLUMNS>\n     </HEADER>\n'
    x += '     <CONTAINERS>\n' + cont('SCREEN', 'SCREEN') + ''.join(containers) + '     </CONTAINERS>\n'
    x += '     <FIELDS>\n' + ''.join(fields) + '     </FIELDS>\n'
    flow = flows[no].rstrip('\n').split('\n')
    x += '     <FLOW_LOGIC>\n' + ''.join(f'      <RPY_DYFLOW>\n       <LINE>{esc(l)}</LINE>\n      </RPY_DYFLOW>\n' if l.strip() else '      <RPY_DYFLOW/>\n' for l in flow) + '     </FLOW_LOGIC>\n'
    return x + '    </item>\n'

# 0100 : bandeau, en-tête (sous-écran), table control, boutons, détail (sous-écran)
TC = ('TABLE_CTRL', 'TC_ITEMS')
cols = [('ITEM_NUM', 'Item', 4, 4, 'NUMC', 'out'), ('ITEM_OK', 'OK', 1, 3, 'CHAR', 'check'),
        ('ARTICLE_ID', 'Article', 10, 10, 'CHAR', 'out'), ('ARTICLE_NAME', 'Description', 40, 24, 'CHAR', 'out'),
        ('QUANTITY', 'Quantity', 17, 12, 'DEC', 'io'), ('BASE_UOM', 'Unit', 3, 4, 'CHAR', 'out'),
        ('DST_ZONE', 'Dest. zone', 10, 10, 'CHAR', 'io'), ('MVT_TYPE', 'MvT', 3, 3, 'CHAR', 'out'),
        ('STOCK_AVAIL', 'Open qty', 17, 12, 'DEC', 'out'), ('MESSAGE', 'Message', 60, 30, 'CHAR', 'out')]
tcf = [fld(*TC, 'CHECK', 'ZRET_S_GM_ITEM-MARK', '', 1, 0, 1, 1, io=True, fromdict=True, tc_sel=True)]
for i, (f, t, L, v, fm, kind) in enumerate(cols, 1):
    tcf.append(fld(*TC, 'TEXT', 'H_' + f, t, 1, i, v, v, tc_head=True))
for i, (f, t, L, v, fm, kind) in enumerate(cols, 1):
    if kind == 'check':
        tcf.append(fld(*TC, 'CHECK', 'ZRET_S_GM_ITEM-' + f, '', 1, i, 1, 1, io=True, fromdict=True))
    else:
        tcf.append(fld(*TC, 'TEMPLATE', 'ZRET_S_GM_ITEM-' + f, '_' * v, 1, i, L, v, fm, io=(kind == 'io'), out=(kind == 'out'), fromdict=True))
s0100 = screen('0100', 'ZMIGO: goods movement (main screen)', 'N', 34, 120, [
    cont('SUBSCREEN', 'SUB_HDR', 'SCREEN', 3, 1, 118, 6, resize=('X', 'X', 2, 20)),
    cont('TABLE_CTRL', 'TC_ITEMS', 'SCREEN', 10, 1, 118, 10, resize=('X', 'X', 3, 10), scroll=('X', 'X'), tc=1),
    cont('SUBSCREEN', 'SUB_ITEM', 'SCREEN', 23, 1, 118, 9, resize=('X', 'X', 4, 20))], [
    lab('Action', 1, 1, 8), tmpl('ZRET_S_GM_HDR-ACTION', 1, 10, 3, vis=22, dd=True),
    lab('Reference', 1, 34, 10), tmpl('ZRET_S_GM_HDR-REFTYPE', 1, 45, 3, vis=18, dd=True),
    tmpl('ZRET_S_GM_HDR-REF_DOC', 1, 65, 10, fmt='NUMC'),
    fld(*S, 'PUSH', 'BTN_EXEC', 'Execute', 1, 77, 10, fcode='EXEC'),
    fld(*S, 'PUSH', 'BTN_CHECK', 'Check', 1, 89, 9, fcode='CHECK'),
    fld(*S, 'PUSH', 'BTN_POST', 'Post', 1, 100, 9, fcode='POST')] + tcf + [
    fld(*S, 'PUSH', 'BTN_ALL_OK', 'All OK', 21, 1, 10, fcode='ALL_OK'),
    fld(*S, 'PUSH', 'BTN_DEL', 'Delete', 21, 13, 10, fcode='DEL'), OK])
# 0110 : tabstrip en-tête
TH = ('STRIP_CTRL', 'TS_HDR')
s0110 = screen('0110', 'ZMIGO: header (tabstrip)', 'I', 6, 118, [
    cont('STRIP_CTRL', 'TS_HDR', 'SCREEN', 1, 1, 116, 5, resize=('X', 'X', 3, 20)),
    cont('SUBSCREEN', 'SUB_HTAB', 'TS_HDR', 3, 2, 112, 3, resize=('X', 'X', 2, 8), scroll=('X', 'X'))], [
    fld(*TH, 'PUSH', 'TABH1', 'General', 1, 1, 12, fcode='TABH1', ref='SUB_HTAB'),
    fld(*TH, 'PUSH', 'TABH2', 'Info', 1, 2, 10, fcode='TABH2', ref='SUB_HTAB')])
s0111 = screen('0111', 'ZMIGO: header general', 'I', 3, 112, [], [
    lab('Posting date', 1, 1, 14), tmpl('ZRET_S_GM_HDR-POSTING_DATE', 1, 16, 10, fmt='DATS'),
    lab('Site', 1, 30, 6), tmpl('ZRET_S_GM_HDR-SITE_ID', 1, 37, 4),
    lab('Header text', 2, 1, 14), tmpl('ZRET_S_GM_HDR-HEADER_TEXT', 2, 16, 40)])
s0112 = screen('0112', 'ZMIGO: header info', 'I', 3, 112, [], [
    lab('User', 1, 1, 14), tmpl('ZRET_S_GM_HDR-CREATED_BY', 1, 16, 12, out=True),
    lab('Items', 1, 30, 6), tmpl('ZRET_S_GM_HDR-NB_ITEMS', 1, 37, 3, fmt='NUMC', out=True),
    lab('PO status', 2, 1, 14), tmpl('ZRET_S_GM_HDR-PO_STATUS', 2, 16, 1, out=True)])
# 0120 : tabstrip détail
TI = ('STRIP_CTRL', 'TS_ITEM')
s0120 = screen('0120', 'ZMIGO: item detail (tabstrip)', 'I', 9, 118, [
    cont('STRIP_CTRL', 'TS_ITEM', 'SCREEN', 1, 1, 116, 8, resize=('X', 'X', 4, 20)),
    cont('SUBSCREEN', 'SUB_ITAB', 'TS_ITEM', 3, 2, 112, 6, resize=('X', 'X', 3, 8), scroll=('X', 'X'))], [
    fld(*TI, 'PUSH', 'TABI1', 'Article', 1, 1, 12, fcode='TABI1', ref='SUB_ITAB'),
    fld(*TI, 'PUSH', 'TABI2', 'Where', 1, 2, 10, fcode='TABI2', ref='SUB_ITAB'),
    fld(*TI, 'PUSH', 'TABI3', 'Batch / HU', 1, 3, 14, fcode='TABI3', ref='SUB_ITAB')])
s0121 = screen('0121', 'ZMIGO: item article', 'I', 6, 112, [], [
    lab('Item', 1, 1, 12), tmpl('ZRET_S_GM_ITEM-ITEM_NUM', 1, 14, 4, fmt='NUMC', out=True),
    lab('Article', 2, 1, 12), tmpl('ZRET_S_GM_ITEM-ARTICLE_ID', 2, 14, 10, out=True),
    tmpl('ZRET_S_GM_ITEM-ARTICLE_NAME', 2, 26, 40, out=True),
    lab('Quantity', 3, 1, 12), tmpl('ZRET_S_GM_ITEM-QUANTITY', 3, 14, 17, fmt='DEC'),
    tmpl('ZRET_S_GM_ITEM-BASE_UOM', 3, 32, 3, out=True)])
s0122 = screen('0122', 'ZMIGO: item where', 'I', 6, 112, [], [
    lab('Site', 1, 1, 12), tmpl('ZRET_S_GM_HDR-SITE_ID', 1, 14, 4, out=True),
    lab('Source zone', 2, 1, 12), tmpl('ZRET_S_GM_ITEM-SRC_ZONE', 2, 14, 10, out=True),
    lab('Dest. zone', 3, 1, 12), tmpl('ZRET_S_GM_ITEM-DST_ZONE', 3, 14, 10),
    lab('Open qty', 4, 1, 12), tmpl('ZRET_S_GM_ITEM-STOCK_AVAIL', 4, 14, 17, fmt='DEC', out=True)])
s0123 = screen('0123', 'ZMIGO: item batch / HU', 'I', 6, 112, [], [
    lab('HU', 1, 1, 12), tmpl('ZRET_S_GM_ITEM-HU_ID', 1, 14, 20),
    lab('Batch', 2, 1, 12), tmpl('ZRET_S_GM_ITEM-BATCH', 2, 14, 10)])

# ---------------------------------------------------------------- CUA
funs = [('POST', 'Post', 'ICON_SYSTEM_SAVE', '@2L@'), ('CHECK', 'Check', 'ICON_CHECK', '@01@'), ('BACK', 'Back', '', ''),
        ('EXIT', 'Exit', '', ''), ('CANC', 'Cancel', 'ICON_CANCEL', '@0W@'), ('ENTER', 'Enter', '', '')]
def funt(c, t, tn, ic):
    x = f'     <RSMPE_FUNT>\n      <CODE>{c}</CODE>\n      <TEXTNO>001</TEXTNO>\n'
    if c in ('BACK', 'EXIT', 'CANC'): x += '      <TYPE>E</TYPE>\n'
    x += '      <TEXT_TYPE>S</TEXT_TYPE>\n'
    if tn: x += f'      <TEXT_NAME>{tn}</TEXT_NAME>\n      <ICON_ID>{ic}</ICON_ID>\n'
    return x + f'      <FUN_TEXT>{t}</FUN_TEXT>\n     </RSMPE_FUNT>\n'
pfk = [('00', 'ENTER'), ('03', 'BACK'), ('07', 'CHECK'), ('11', 'POST'), ('12', 'CANC'), ('15', 'EXIT')]
cua = '   <CUA>\n    <ADM>\n     <ACTCODE>000001</ACTCODE>\n     <PFKCODE>000001</PFKCODE>\n    </ADM>\n    <STA>\n     <RSMPE_STAT>\n      <CODE>MAIN</CODE>\n      <MODAL>D</MODAL>\n      <ACTCODE>000001</ACTCODE>\n      <PFKCODE>000001</PFKCODE>\n      <BUTCODE>0001</BUTCODE>\n      <INT_NOTE>ZMIGO main status</INT_NOTE>\n     </RSMPE_STAT>\n    </STA>\n'
cua += '    <FUN>\n' + ''.join(funt(*f) for f in funs) + '    </FUN>\n'
cua += '    <BUT>\n' + ''.join(f'     <RSMPE_BUT>\n      <PFK_CODE>000001</PFK_CODE>\n      <CODE>0001</CODE>\n      <NO>{no}</NO>\n      <PFNO>{pf}</PFNO>\n     </RSMPE_BUT>\n' for no, pf in [('01', '11'), ('02', '07'), ('03', '03'), ('04', '15'), ('05', '12')]) + '    </BUT>\n'
cua += '    <PFK>\n' + ''.join(f'     <RSMPE_PFK>\n      <CODE>000001</CODE>\n      <PFNO>{pf}</PFNO>\n      <FUNCODE>{fc}</FUNCODE>\n      <FUNNO>001</FUNNO>\n     </RSMPE_PFK>\n' for pf, fc in pfk) + '    </PFK>\n'
cua += '    <SET>\n' + ''.join(f'     <RSMPE_STAF>\n      <STATUS>MAIN</STATUS>\n      <FUNCTION>{f[0]}</FUNCTION>\n     </RSMPE_STAF>\n' for f in funs) + '    </SET>\n'
cua += '    <DOC>\n' + ''.join(f'     <RSMPE_ATRT>\n      <OBJ_TYPE>{t}</OBJ_TYPE>\n      <OBJ_CODE>000001</OBJ_CODE>\n{sub}      <MODAL>D</MODAL>\n      <INT_NOTE>ZMIGO main status</INT_NOTE>\n     </RSMPE_ATRT>\n' for t, sub in [('A', ''), ('P', ''), ('B', '      <SUB_CODE>0001</SUB_CODE>\n')]) + '    </DOC>\n'
cua += '    <TIT>\n     <RSMPE_TITT>\n      <CODE>T_MAIN</CODE>\n      <TEXT>&amp;1</TEXT>\n     </RSMPE_TITT>\n    </TIT>\n   </CUA>\n'
title = 'ZMIGO: goods movement (MIGO-style test bench)'
xml = progdir(P, 'M')
xml += '   <DYNPROS>\n' + s0100 + s0110 + s0111 + s0112 + s0120 + s0121 + s0122 + s0123 + '   </DYNPROS>\n' + cua
xml += f'   <TPOOL>\n    <item>\n     <ID>R</ID>\n     <ENTRY>{title}</ENTRY>\n     <LENGTH>{len(title)}</LENGTH>\n    </item>\n   </TPOOL>\n' + TAIL
w('sapmzret_gm.prog.xml', xml)
print('ok', len(xml))
