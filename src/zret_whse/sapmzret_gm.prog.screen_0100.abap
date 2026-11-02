PROCESS BEFORE OUTPUT.
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
