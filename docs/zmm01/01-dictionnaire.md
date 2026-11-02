# Dictionnaire (SE11)

## Structure ZRET_S_ART (données écran de l'en-tête)

| Champ | Type | Remarque |
|---|---|---|
| ARTICLE_ID | ZRET_T_ARTICLE-ARTICLE_ID | clé saisie à l'écran 0100 |
| ARTICLE_NAME | ZRET_T_ARTICLE-ARTICLE_NAME | obligatoire |
| ARTICLE_TYPE | ZRET_T_ARTICLE-ARTICLE_TYPE | obligatoire, valeurs HARD / SOFT / FOOD |
| BASE_UOM | ZRET_T_ARTICLE-BASE_UOM | défaut PC |
| ACTIVE_FLAG | ZRET_T_ARTICLE-ACTIVE_FLAG | case à cocher |
| PRICE | ZRET_T_ARTICLE-PRICE | obligatoire, > 0 |
| CURRENCY | ZRET_T_ARTICLE-CURRENCY | défaut EUR |
| GENERIC_ARTICLE_ID | ZRET_T_ARTICLE-GENERIC_ARTICLE_ID | optionnel |

(Si un champ n'existe pas dans ZRET_T_ARTICLE sur votre version, prenez le type élémentaire équivalent : CHAR 40 pour le nom, CHAR 4 pour le type, UNIT pour l'unité, CURR 11.2 + CUKY pour le prix.)

## Table ZRET_T_ART_VAR (variantes d'article)

Table transparente, classe de livraison A, affichage/maintenance autorisés.

| Champ | Clé | Type | Remarque |
|---|---|---|---|
| MANDT | X | MANDT | |
| ARTICLE_ID | X | ZRET_T_ARTICLE-ARTICLE_ID | |
| VARIANT_ID | X | CHAR 4 | ex. V001 |
| COLOR | | CHAR 20 | |
| SIZE_CODE | | CHAR 6 | (SIZE est un mot réservé) |
| EAN | | CHAR 13 | 13 chiffres contrôlés à la sauvegarde |
| PRICE | | CURR 11.2 | référence devise : ZRET_T_ART_VAR-CURRENCY |
| CURRENCY | | CUKY | |

## Structure ZRET_S_ART_VAR (ligne du table control)

Mêmes champs que ZRET_T_ART_VAR sans MANDT, plus `MARK TYPE CHAR 1` (colonne de sélection du table control).
