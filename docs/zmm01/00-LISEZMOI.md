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
