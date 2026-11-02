# ZMIGO : mouvement de marchandises façon MIGO (sortie de marchandises)

Famille d'écran : composite « transaction + en-tête + grille de postes + détail du poste en onglets + Contrôler puis Comptabiliser ». C'est l'écran le plus proche d'une recette réelle : on prépare, on contrôle, on comptabilise, on lit un numéro de document. Variante EWM possible plus tard (Z/SCWM/TU : unité de transport, mêmes principes avec un arbre de HU).

## Objets (package ZRET_WHSE)

- Module pool `SAPMZRET_GM` (type M), transaction `ZMIGO` (écran 0100). Tables existantes `ZRET_T_STOCK`, `ZRET_T_STK_MVT` ; classe existante `zcl_ret_stock` pour les mouvements (601 sortie sur livraison, 101 réception sur PO, 311 transfert de zone, 551 mise au rebut).
- Structures écran `ZRET_S_GM_HDR` (ACTION, REFTYPE, REF_DOC, POSTING_DATE, SITE_ID, HEADER_TEXT) et `ZRET_S_GM_ITEM` (ITEM_NUM, ARTICLE_ID, ARTICLE_NAME, QUANTITY, BASE_UOM, SRC_ZONE, DST_ZONE, MVT_TYPE, ITEM_OK, STOCK_AVAIL, MESSAGE).

## Écran 0100

1. **Bandeau de transaction** (ligne du haut, comme MIGO) : deux listes déroulantes `ZRET_S_GM_HDR-ACTION` (A01 Réception, A07 Sortie de marchandises, A08 Transfert, A09 Rebut) et `ZRET_S_GM_HDR-REFTYPE` (R01 Commande d'achat, R05 Livraison, R10 Autre), un champ `ZRET_S_GM_HDR-REF_DOC` et un bouton `BTN_EXEC` « Exécuter » fonction `EXEC` (charge les postes depuis la référence).
2. **En-tête** : sous-écran 0110 dans la zone `SUB_HDR`, tabstrip `TS_HDR` à deux onglets : `TABH1` « Général » (POSTING_DATE défaut aujourd'hui, SITE_ID, HEADER_TEXT) et `TABH2` « Infos » (sortie : utilisateur, nombre de postes, référence).
3. **Table control** `TC_ITEMS` (pas une grille ALV : on couvre les deux familles) : colonnes ITEM_NUM, ITEM_OK (case à cocher), ARTICLE_ID, ARTICLE_NAME (sortie), QUANTITY, BASE_UOM, SRC_ZONE, DST_ZONE, MVT_TYPE (sortie), STOCK_AVAIL (sortie), MESSAGE (sortie, texte du dernier contrôle de la ligne). Bouton `BTN_ALL_OK` « Tout OK » fonction `ALL_OK`, bouton `BTN_DEL` « Supprimer » fonction `DEL`.
4. **Détail du poste** : sous-écran 0120 dans `SUB_ITEM`, tabstrip `TS_ITEM` : `TABI1` « Article » (ARTICLE_ID, ARTICLE_NAME, QUANTITY, BASE_UOM), `TABI2` « Où » (SITE_ID, SRC_ZONE, DST_ZONE, STOCK_AVAIL), `TABI3` « Lot / HU » (champs texte libres HU_ID, BATCH, pour l'exercice). Le détail suit la ligne courante du table control.

Statut GUI `MAIN` : Contrôler `CHECK` (F7, bouton « Contrôler »), Comptabiliser `POST` (Ctrl+S, bouton « Comptabiliser »), Retour `BACK` (F3), Quitter `EXIT`, Annuler `CANC`, Entrée `ENTER`. Les boutons Contrôler et Comptabiliser sont aussi dans la barre d'application.

## Comportement

- `EXEC` avec A07 + R05 + numéro de livraison : charge les postes de la livraison (ZRET_T_DELIV_ITEM), SRC_ZONE = STORAGE, DST_ZONE vide, MVT_TYPE 601, STOCK_AVAIL = stock en STORAGE au site. Livraison inconnue → E « Livraison X inexistante ». Livraison déjà expédiée → E « Livraison X déjà expédiée ».
- `EXEC` avec A01 + R01 + numéro de PO : postes de la PO non encore réceptionnés, DST_ZONE = RECV, MVT_TYPE 101.
- `CHECK` : pour chaque poste coché ITEM_OK : quantité > 0, quantité ≤ STOCK_AVAIL pour une sortie (sinon MESSAGE de la ligne = « Stock insuffisant : disponible N », et E global « 1 poste en erreur, voir la colonne Message »), zone valide. Aucun poste coché → W « Aucun poste sélectionné » (popup d'information). Tout bon → S « Document contrôlé, N poste(s) prêt(s) ».
- `POST` : refait le contrôle, puis appelle `zcl_ret_stock=>post_movement` par poste, et dans le cas A07 fait passer la livraison au statut S (Shipped) via la classe existante. Message S « Document matière 49000NNNN comptabilisé (N postes) ». Le numéro vient d'une plage ZRET_GM (SNRO) ou d'un compteur simple dans une table ZRET_T_GM_HDR (HEADER : GM_DOC, ACTION, REF_DOC, POSTING_DATE, CREATED_BY ; ITEMS dans ZRET_T_GM_ITEM).
- `BACK`/`CANC` avec postes chargés et non comptabilisés : popup « Les données seront perdues. Quitter ? ».

## Scénarios Automate (campagne « 8 · ZMIGO »)

1. `zmigo-sortie-livraison` : ZMIGO, ACTION A07, REFTYPE R05, REF_DOC=`${DELIV}` (capturé par Outbound), Exécuter → `screen:` sur la première cellule du table control ; `press` Tout OK ; Contrôler → `statustype:S` + `status:prêt` ; Comptabiliser → `statustype:S`, `capture:GMDOC=sbar#Document matière (\d+)` ; puis dans ZRET_R_DELIV_LIST vérifier `cell:auto:grid[DELIV_NUMBER=${DELIV}].STATUS=S`.
2. `zmigo-stock-insuffisant` : même chose avec une quantité forcée à 9999 dans le table control (`set` sur la cellule QUANTITY `[col,row]`) → Contrôler → `statustype:E`, `text:Stock insuffisant` (lu dans la colonne Message via le table control ou le texte de l'écran), capture d'écran ; Annuler → popup → Oui.
3. `zmigo-aucun-poste` : Exécuter puis Contrôler sans cocher → popup d'information « Aucun poste sélectionné » (`popup:Aucun poste`), Entrée.

## Ce qui manque au moteur pour ce banc d'essai

- Rien d'obligatoire : table control adressé par `[col,row]`, popups, barre de statut, listes déroulantes, tout est déjà couvert. Le confort viendra avec `tc:` (viser une colonne par nom et une ligne par valeur, comme pour les grilles).
- Pour la version EWM (Z/SCWM/TU) : un arbre de HU (`cl_gui_simple_tree`) et la sélection de nœuds (`selectedNode`, `doubleClickNode`), à ajouter au moteur à ce moment-là.

## Réalisé le 02/11/2026 (première version, générée par `gen_zmigo.py`)

Périmètre : réception sur commande d'achat (A01 + R01) uniquement ; les autres actions répondent « non couvert ». Bandeau avec deux listes déroulantes, en-tête en tabstrip (Général / Infos), postes en table control `TC_ITEMS` (colonne OK à cocher, quantité et zone saisissables, colonne Message), détail en tabstrip (Article / Où / Lot-HU) qui suit la ligne sous le curseur, boutons Exécuter / Contrôler / Comptabiliser / Tout OK / Supprimer. La comptabilisation passe par `zcl_ret_purch_order=>post_goods_receipt` (mouvement 101 en RECV, mise à jour de la commande, tâche de rangement) ; le numéro du premier mouvement sert de document matière. Pas de tables ZRET_T_GM_* dans cette version. Les refus sont en `S DISPLAY LIKE 'E'` pour garder l'écran saisissable.

Campagnes : « 8 · ZMIGO banc d'essai » (rz-po-demo pour une commande neuve, puis popup sans poste, quantité excessive, réception avec SE16) et « 9 · Flux complet (démo) » : zmm01-creation, zmm01-verif-table, rz-po-demo, zme23n-modif-quantite, zme23n-drilldown, zmigo-reception-po. Les scénarios ZME23N/ZMIGO prennent ${PO} de la capture de rz-po-demo (plus de PO en dur dans les CSV).

## État au 02/11/2026, fin de journée : ZMIGO 3/3 et « 9 · Flux complet (démo) » 6/6 sur A4H

Flux complet en un lancement : zmm01-creation 15/15 (article neuf), zmm01-verif-table 11/11, rz-po-demo 4/4 (commande neuve), zme23n-modif-quantite 11/11 (poste 2 → 55), zme23n-drilldown 6/6, zmigo-reception-po 13/13 (réception de 55 PC, mouvement 101 vérifié en SE16). Rejouable à l'infini.

Pièges rencontrés sur ZMIGO : zone de travail TABLES partagée entre le table control et le détail (au PAI elle porte la dernière ligne transportée, y compris une ligne vide) : le détail ne lit que les champs de son propre sous-écran (`sy-dynnr`) et le table control ne reprend que ses colonnes saisissables ; refus en `S DISPLAY LIKE 'E'` pour garder l'écran saisissable ; ids du table control `tblSAPMZRET_GMTC_ITEMS/txtZRET_S_GM_ITEM-<COL>[col,row]` (ITEM_NUM=0, ITEM_OK=1 en chk, ARTICLE_ID=2, ARTICLE_NAME=3, QUANTITY=4, BASE_UOM=5, DST_ZONE=6, MVT_TYPE=7, STOCK_AVAIL=8, MESSAGE=9).

Côté MyToolKit (1.6.3, à recompiler) : le moteur épingle désormais la session SAP où sa dernière action a abouti (lectures de popup, statut, transaction, touches), les sessions sans utilisateur passent en dernier, et la fenêtre la plus haute est prise dans la liste réelle des fenêtres (plus de findById sur une popup fermée). Cause des échecs intermittents de `nopopup` et d'Entrée envoyée au mauvais endroit quand une connexion morte traîne dans SAP Logon.
