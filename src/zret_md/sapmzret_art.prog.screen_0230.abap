PROCESS BEFORE OUTPUT.
  MODULE tc_var_init.
  LOOP AT gt_var INTO gs_var WITH CONTROL tc_var CURSOR tc_var-current_line.
    MODULE tc_var_pbo.
  ENDLOOP.

PROCESS AFTER INPUT.
  LOOP AT gt_var.
    MODULE tc_var_pai.
  ENDLOOP.
  MODULE tc_var_user_command.
