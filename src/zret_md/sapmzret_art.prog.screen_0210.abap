PROCESS BEFORE OUTPUT.
  MODULE init_listbox.

PROCESS AFTER INPUT.
  CHAIN.
    FIELD: zret_s_art-article_name, zret_s_art-article_type.
    MODULE check_0210.
  ENDCHAIN.
