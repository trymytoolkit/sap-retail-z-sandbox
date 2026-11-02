*&---------------------------------------------------------------------*
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
