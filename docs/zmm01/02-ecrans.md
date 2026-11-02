# Écrans (SE51), programme SAPMZRET_ART

Règle d'or : les NOMS des éléments sont ceux des champs du dictionnaire (ZRET_S_ART-ARTICLE_NAME…), c'est ce que SAP GUI Scripting expose et ce que les scénarios ciblent.

## 0100 · Écran initial (type normal)

Éléments : texte « Article », champ de saisie `ZRET_S_ART-ARTICLE_ID` (obligatoire : attribut « Saisie obligatoire », aide de recherche sur ZRET_T_ARTICLE si vous en avez une), bouton `BTN_GO` texte « Continuer », fonction `GO`. Champ OK_CODE : `OK_CODE`.

Flow logic :
```
PROCESS BEFORE OUTPUT.
  MODULE status_0100.
PROCESS AFTER INPUT.
  MODULE exit_0100 AT EXIT-COMMAND.
  MODULE user_command_0100.
```

## 0200 · Écran principal (type normal)

Éléments : un tabstrip nommé `TS_MAIN` avec trois onglets (boutons) :
- `TAB1` texte « Données de base », fonction `TAB1`, sous-écran de référence `SUB_MAIN`
- `TAB2` texte « Vente », fonction `TAB2`, même zone `SUB_MAIN`
- `TAB3` texte « Variantes », fonction `TAB3`, même zone `SUB_MAIN`
Une zone de sous-écran `SUB_MAIN` à l'intérieur du tabstrip. Champ OK_CODE : `OK_CODE`.

Flow logic :
```
PROCESS BEFORE OUTPUT.
  MODULE status_0200.
  CALL SUBSCREEN sub_main INCLUDING 'SAPMZRET_ART' gv_subscreen.
PROCESS AFTER INPUT.
  MODULE exit_0200 AT EXIT-COMMAND.
  CALL SUBSCREEN sub_main.
  MODULE user_command_0200.
```

## 0210 · Sous-écran « Données de base »

Champs (avec leur libellé à gauche) : `ZRET_S_ART-ARTICLE_NAME` (obligatoire), `ZRET_S_ART-ARTICLE_TYPE` (zone de liste déroulante, valeurs fournies par le module `init_listbox` : HARD, SOFT, FOOD), `ZRET_S_ART-BASE_UOM`, case à cocher `ZRET_S_ART-ACTIVE_FLAG` texte « Actif ».

Flow logic :
```
PROCESS BEFORE OUTPUT.
  MODULE init_listbox.
PROCESS AFTER INPUT.
  MODULE check_0210.
```

## 0220 · Sous-écran « Vente »

Champs : `ZRET_S_ART-PRICE`, `ZRET_S_ART-CURRENCY`, `ZRET_S_ART-GENERIC_ARTICLE_ID`.

Flow logic :
```
PROCESS BEFORE OUTPUT.
PROCESS AFTER INPUT.
  MODULE check_0220.
```

## 0230 · Sous-écran « Variantes »

Un table control nommé `TC_VAR` (assistant « Table control » de SE51 ou à la main), colonnes depuis la structure `ZRET_S_ART_VAR` : VARIANT_ID, COLOR, SIZE_CODE, EAN, PRICE. Colonne de sélection de ligne : `ZRET_S_ART_VAR-MARK`. 5 lignes visibles, barre de défilement verticale. Sous le table control, deux boutons : `BTN_ADD` « Ajouter ligne » fonction `ADD`, `BTN_DEL` « Supprimer ligne » fonction `DEL`.

Flow logic :
```
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
```

Identifiants que verra MyToolKit (à confirmer avec « Voir les éléments de l'écran ») :
- nom : `wnd[0]/usr/tabsTS_MAIN/tabpTAB1/ssubSUB_MAIN:SAPMZRET_ART:0210/txtZRET_S_ART-ARTICLE_NAME`
- onglet Variantes : `wnd[0]/usr/tabsTS_MAIN/tabpTAB3`
- cellule variante ligne 1, colonne VARIANT_ID : `wnd[0]/usr/tabsTS_MAIN/tabpTAB3/ssubSUB_MAIN:SAPMZRET_ART:0230/tblSAPMZRET_ARTTC_VAR/txtZRET_S_ART_VAR-VARIANT_ID[0,0]` (le suffixe [colonne,ligne] est ajouté par SAP GUI).

> Note abapGit : dans l'en-tête RPY_DYHEAD, un écran normal porte `TYPE N` et un **sous-écran porte `TYPE I`** (pas `S`). Avec `S`, abapGit crée l'objet sans erreur visible mais le dynpro n'est jamais généré (DYNPRO_NOT_FOUND à l'exécution).

> Unité de base : valeur interne 'ST' (affichée PC en anglais via l'exit de conversion CUNIT). 'PC' en interne n'existe pas et bloque la saisie (Unit *** is not created).

> Ids relevés sur A4H (dump MTK) : écran initial `wnd[0]/usr/txtZRET_S_ART-ARTICLE_ID` ; onglets `wnd[0]/usr/tabsTS_MAIN/tabpTAB1..3` ; sous-écrans `ssubSUB_MAIN:SAPMZRET_ART:0210/0220/0230` ; liste `cmbZRET_S_ART-ARTICLE_TYPE` ; table control `tblSAPMZRET_ARTTC_VAR/txtZRET_S_ART_VAR-<COL>[col,row]` (VARIANT_ID=0, COLOR=1, SIZE_CODE=2, EAN=3, PRICE=4) ; popup POPUP_TO_CONFIRM (SAPLSPO1 0502, rendu HTML) : boutons `wnd[1]/usr/btnBUTTON_1` (Oui) et `btnBUTTON_2` (Non).
