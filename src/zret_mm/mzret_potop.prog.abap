*&---------------------------------------------------------------------*
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
