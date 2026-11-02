# ZME23N : affichage et modification de commande d'achat façon ME23N

Famille d'écran : « Enjoy » (ME21N/ME23N, VA01 en S/4) : en-tête repliable, postes dans une grille ALV éditable, détail du poste sous la grille, arbre de sélection à gauche. Ce que MyToolKit doit prouver : lire et écrire des cellules ALV, utiliser les boutons de barre d'outils ALV, replier et déplier des zones, drill-down par double-clic.

## Objets (package ZRET_MM)

- Module pool `SAPMZRET_PO` (type M), transaction `ZME23N` (écran 0100). Tables existantes `ZRET_T_PO` (en-tête) et `ZRET_T_PO_ITEM` (postes). Structure écran `ZRET_S_PO_HDR` (champs de ZRET_T_PO utilisés) et structure grille `ZRET_S_PO_ITEM_ALV` (champs de ZRET_T_PO_ITEM + `CELLSTYLES TYPE lvc_t_styl` pour rendre éditables les postes non livrés).
- Classe locale `lcl_po_alv` dans l'include F01 : création des contrôles, gestion des événements `data_changed`, `double_click`, `toolbar`, `user_command`.

## Écran 0100 (unique, type normal)

Trois zones, de haut en bas et de gauche à droite :

1. **Barre de sélection** : champ `ZRET_S_PO_HDR-PO_NUMBER` (saisie du numéro), bouton `BTN_OTHER` « Autre commande » fonction `OTHER`, bouton `BTN_EDIT` « Afficher ↔ Modifier » fonction `TOGGLE` (bascule le mode ; en affichage les cellules sont en lecture seule).
2. **Custom container** `CC_TREE` à gauche (largeur 25 %) : un `cl_gui_simple_tree` listant les dix dernières commandes (numéro, fournisseur, statut) ; double-clic sur un nœud charge la commande. Fonction `TREE_TOGGLE` (bouton `BTN_TREE` « Sélection de documents ») montre ou cache le conteneur.
3. **En-tête** : zone repliable (bouton `BTN_HDR` « ▸ En-tête » / « ▾ En-tête », fonction `HDR_TOGGLE`) contenant `ZRET_S_PO_HDR-SUPPLIER_ID`, `SUPPLIER_NAME` (sortie), `SITE_ID`, `PO_DATE`, `CURRENCY`, `STATUS` (sortie), `TOTAL_AMOUNT` (sortie). Les champs sont dans un sous-écran 0110 appelé dans une zone `SUB_HDR`, vide quand replié.
4. **Custom container** `CC_ITEMS` : grille ALV `cl_gui_alv_grid` des postes, colonnes ITEM_NUM, ARTICLE_ID, QUANTITY, BASE_UOM, UNIT_PRICE, TOTAL (calculé), DELIVERED_QTY, STATUS. Colonnes QUANTITY et UNIT_PRICE éditables quand le mode est Modifier et que le poste n'est pas livré. Barre d'outils ALV standard plus deux boutons ajoutés par l'événement `toolbar` : `ADD_ITEM` (icône +, « Nouveau poste ») et `DEL_ITEM` (icône corbeille, « Supprimer le poste »). Un poste nouveau se crée avec ARTICLE_ID vide et éditable.
5. **Détail du poste** : sous-écran 0120 dans la zone `SUB_ITEM`, un tabstrip `TS_ITEM` à deux onglets : `TABI1` « Données du poste » (sous-écran 0121 : `ZRET_S_PO_ITEM_ALV-ARTICLE_ID` sortie, `ARTICLE_NAME` sortie, `QUANTITY`, `UNIT_PRICE`, `BASE_UOM`, `TOTAL` sortie) et `TABI2` « Livraison » (sous-écran 0122 : `DELIVERED_QTY` sortie, `OPEN_QTY` sortie, `GR_DATE` sortie, case `FINAL_DELIVERY`). Le détail affiche le poste de la ligne courante de la grille (événement `double_click` ou bouton de la barre « Détail »).

Statut GUI `MAIN` : Sauvegarder `SAVE` (Ctrl+S), Retour `BACK` (F3), Quitter `EXIT` (Shift+F3), Annuler `CANC` (F12), Contrôler `CHECK` (Ctrl+F1, bouton « Contrôler »), Entrée `ENTER`.

## Comportement

- Entrée du numéro + Entrée ou `OTHER` : charge l'en-tête et les postes ; inconnu → message E « Commande X inexistante ».
- `TOGGLE` en Modifier sur une commande au statut C (clôturée) ou B (facturée) → message E « Commande au statut X : modification impossible ». Sinon bascule, cellules éditables, titre « Modifier commande X ».
- `CHECK` : quantité ≤ 0 → E « Poste N : quantité invalide » ; prix ≤ 0 → E ; quantité < livré → E « Poste N : quantité inférieure au livré » ; sinon S « Commande X contrôlée, aucune erreur ».
- `SAVE` : mêmes contrôles, puis mise à jour de ZRET_T_PO_ITEM, recalcul de TOTAL_AMOUNT dans ZRET_T_PO, message S « Commande X modifiée (N postes, total T EUR) », retour en Afficher.
- `BACK`/`EXIT`/`CANC` avec données modifiées : `POPUP_TO_CONFIRM` « Les données seront perdues. Quitter ? ».
- `DEL_ITEM` sur un poste livré (DELIVERED_QTY > 0) → E « Poste livré : suppression impossible ».

## Scénarios Automate (campagne « 7 · ZME23N »)

1. `zme23n-modif-quantite` : ouvrir ZME23N, saisir `${PO}` (capturé par Inbound, ou dans le CSV), Entrée, vérifier l'en-tête chargé (`value:` sur SUPPLIER_ID), `press` sur BTN_EDIT, écrire QUANTITY=`${QTE}` sur la ligne ITEM_NUM=0002 de la grille (`set` par cellule ALV : nouvelle syntaxe `cellset:auto:grid[ITEM_NUM=0002].QUANTITY=${QTE}` à ajouter au moteur), `press` Contrôler → `statustype:S`, Ctrl+S → `status:modifiée`, `capture:TOTAL=sbar#total (\S+) EUR`.
2. `zme23n-drilldown` : double-clic sur la ligne 0001 (`dblclick:auto:grid[ITEM_NUM=0001]`), vérifier que le détail affiche l'article (`value:` sur le champ ARTICLE_ID du sous-écran 0121), `press` sur l'onglet Livraison, vérifier DELIVERED_QTY.
3. `zme23n-echec-attendu` : passer en Modifier sur une commande facturée → `statustype:E` + `status:modification impossible`.

## Ce qui manque au moteur pour ce banc d'essai

- Écriture dans une cellule ALV : `cellset:GRILLE[COL=VAL].COL2=VALEUR` (GuiGridView.modifyCell(row, col, value) puis Enter).
- Boutons de barre d'outils ALV : `toolbar:GRILLE=FCODE` (GuiGridView.pressToolbarButton).
- Conteneur replié/déplié : par `press` sur le bouton, puis `screen:`/`gone:` sur un champ de l'en-tête, déjà possible.
