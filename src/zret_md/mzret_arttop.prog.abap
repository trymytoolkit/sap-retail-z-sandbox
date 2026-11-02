*&---------------------------------------------------------------------*
*& Include MZRET_ARTTOP : données globales du module pool SAPMZRET_ART
*&---------------------------------------------------------------------*
PROGRAM sapmzret_art.

" En-tête affiché (structure du dictionnaire : les champs portent son nom)
TABLES: zret_s_art.
DATA: gs_art_db   TYPE zret_t_article,          " état en base (mode modification)
      gv_exists   TYPE abap_bool,
      gv_changed  TYPE abap_bool,
      gv_title    TYPE string,
      ok_code     TYPE sy-ucomm,
      gv_save_ok  TYPE sy-ucomm.

" Tabstrip et sous-écran courant
CONTROLS: ts_main TYPE TABSTRIP.
DATA: gv_subscreen TYPE sy-dynnr VALUE '0210'.

" Variantes : table control
CONTROLS: tc_var TYPE TABLEVIEW USING SCREEN 0230.
DATA: gt_var     TYPE STANDARD TABLE OF zret_s_art_var,
      gs_var     TYPE zret_s_art_var,
      gt_var_db  TYPE STANDARD TABLE OF zret_t_art_var.

CONSTANTS: gc_lines_min TYPE i VALUE 5.
