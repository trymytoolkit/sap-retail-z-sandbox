# ZMM01 : maintenance d'article façon MM01 (banc d'essai MyToolKit)

Ordre de création dans SAP (mandant 001, package ZRET_MD) :

1. SE11 : structure `ZRET_S_ART` (copie des champs de ZRET_T_ARTICLE utilisés), table `ZRET_T_ART_VAR` et structure `ZRET_S_ART_VAR` (voir `01-dictionnaire.md`).
2. SE80 : programme `SAPMZRET_ART` (type M, module pool), avec les includes
   `MZRET_ARTTOP`, `MZRET_ARTO01`, `MZRET_ARTI01`, `MZRET_ARTF01` (sources dans ce dossier).
3. SE51 : écrans 0100, 0200, 0210, 0220, 0230 (voir `02-ecrans.md` : éléments, noms EXACTS, flow logic).
4. SE41 : statut GUI `MAIN` et titre `T_MAIN` (voir `03-statut-gui.md`).
5. SE93 : transaction `ZMM01`, type dynpro, programme SAPMZRET_ART, écran 0100.
6. Activer tout, lancer ZMM01, créer un article à la main une fois.
7. Scénarios MyToolKit : `zmm01-creation.json` et `zmm01-ean-invalide.json` (copier dans Mes guides, ou dans runbooks-defaults).

Les noms de champs, de sous-écrans et du table control sont ceux que les scénarios attendent : ne les changez pas sans changer les scénarios.

## État au 02/11/2026

Importé et activé sur A4H via abapGit (transport A4HK900110). Testé à la main (création ART900 avec une variante) puis par l'Automate : campagne « 6 · ZMM01 banc d'essai » 2/2 (création 15/15, EAN invalide 17/17). Pièges rencontrés et corrigés, utiles pour ZME23N/ZMIGO : sous-écrans `TYPE I` dans l'en-tête abapGit ; unité interne `ST` (pas `PC`) ; contrôles PAI dans un `CHAIN … ENDCHAIN` et seulement sur SAVE ; zone de transport du table control déclarée en `TABLES` ; `USING VALUE(...)` quand le FORM efface la structure passée ; `TYPE E` sur BACK/EXIT/CANC du statut GUI ; boutons du POPUP_TO_CONFIRM = `wnd[1]/usr/btnBUTTON_1/2`.

## Évolutions du 02/11 (après-midi, à valider sur la VM)

- L'article créé est neuf à chaque passage : `A${UNIQ}` dans le CSV (variable fournie par MyToolKit 1.6.3 : base 36 des secondes depuis 2025, 6 caractères). Idem `K${UNIQ}` pour le scénario EAN invalide. Plus de « passage en modification » en boucle.
- `ZRET_T_ARTICLE-EAN` est rempli à la sauvegarde avec l'EAN de la première variante (il restait vide).
- Nouveau scénario `zmm01-verif-table` (SE16 sur ZRET_T_ARTICLE puis ZRET_T_ART_VAR, filtré sur `${ARTSAVED}`, conditions `text:`) inséré dans la campagne entre la création et l'EAN invalide. Ids SE16 supposés (`ctxtDATABROWSE-TABLENAME`, `txtI1-LOW`) : à confirmer au premier lancement.
